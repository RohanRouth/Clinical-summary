import time
from datetime import datetime

from fastapi import APIRouter, HTTPException

from app.config import get_settings
from app.fhir.client import FHIRClient
from app.fhir.resources import (
    AllergyHandler,
    ConditionHandler,
    MedicationRequestHandler,
    ObservationHandler,
    PatientHandler,
)
from app.llm.client import LLMClient
from app.llm.prompts import PromptAssembler, SectionType
from app.schemas.responses import (
    DataAvailability,
    ErrorResponse,
    PatientSummaryResponse,
    SectionSummaries,
)

router = APIRouter(prefix="/api/v1", tags=["summary"])

# Resource handlers mapping
RESOURCE_HANDLERS = {
    "Patient": PatientHandler(),
    "Condition": ConditionHandler(),
    "MedicationRequest": MedicationRequestHandler(),
    "Observation": ObservationHandler(),
    "AllergyIntolerance": AllergyHandler(),
}


@router.get(
    "/summary/{patient_id}",
    response_model=PatientSummaryResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Patient not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def get_patient_summary(patient_id: str) -> PatientSummaryResponse:
    """
    Generate a comprehensive clinical summary for a patient.

    Queries FHIR R4 resources from the HAPI server, extracts relevant clinical
    fields, and uses LLM to generate section summaries and a final cohesive
    clinical narrative.

    Args:
        patient_id: The FHIR Patient resource ID

    Returns:
        PatientSummaryResponse with comprehensive summary and section details
    """
    start_time = time.time()
    settings = get_settings()

    # Step 1: Fetch all FHIR resources in parallel
    async with FHIRClient() as fhir_client:
        try:
            resources = await fhir_client.get_patient_resources(
                patient_id=patient_id,
                resource_types=list(RESOURCE_HANDLERS.keys()),
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"FHIR query failed: {str(e)}",
            )

    # Check if patient exists
    if not resources.get("Patient"):
        raise HTTPException(
            status_code=404,
            detail=f"Patient {patient_id} not found in FHIR server",
        )

    # Step 2: Convert resources to DataFrames
    dataframes = {}
    data_availability = {}

    for resource_type, handler in RESOURCE_HANDLERS.items():
        resource_list = resources.get(resource_type, [])
        df = handler.to_dataframe(resource_list)
        dataframes[resource_type] = df
        data_availability[resource_type] = not df.empty

    # Step 3: Build section prompts
    assembler = PromptAssembler()
    section_prompts = assembler.build_all_section_prompts(dataframes)

    # Step 4: Generate section summaries
    llm = LLMClient()
    section_summaries: dict[SectionType, str] = {}

    for section_type, prompt in section_prompts.items():
        summary = await llm.generate_section_summary(prompt)
        section_summaries[section_type] = summary

    # Step 5: Generate final comprehensive summary
    final_prompt = assembler.build_final_prompt(section_summaries)
    final_summary = await llm.generate_final_summary(final_prompt)

    # Step 6: Build response
    processing_time = int((time.time() - start_time) * 1000)

    return PatientSummaryResponse(
        patient_id=patient_id,
        generated_at=datetime.utcnow(),
        summary=final_summary,
        sections=SectionSummaries(
            demographics=section_summaries.get(SectionType.DEMOGRAPHICS),
            conditions=section_summaries.get(SectionType.CONDITIONS),
            medications=section_summaries.get(SectionType.MEDICATIONS),
            observations=section_summaries.get(SectionType.OBSERVATIONS),
            allergies=section_summaries.get(SectionType.ALLERGIES),
        ),
        data_availability=DataAvailability(**data_availability),
        processing_time_ms=processing_time,
        model=settings.openai_model,
    )


@router.get("/resources/{patient_id}")
async def get_patient_resources(patient_id: str) -> dict:
    """
    Debug endpoint to fetch raw FHIR resources for a patient.

    Useful for testing and debugging the FHIR data extraction.
    """
    async with FHIRClient() as fhir_client:
        resources = await fhir_client.get_patient_resources(
            patient_id=patient_id,
            resource_types=list(RESOURCE_HANDLERS.keys()),
        )

    # Convert to DataFrames and return as dict
    result = {}
    for resource_type, handler in RESOURCE_HANDLERS.items():
        resource_list = resources.get(resource_type, [])
        df = handler.to_dataframe(resource_list)
        result[resource_type] = {
            "count": len(resource_list),
            "data": df.to_dict(orient="records") if not df.empty else [],
        }

    return result
