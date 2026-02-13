from enum import Enum


class SectionType(str, Enum):
    """Clinical summary section types."""

    DEMOGRAPHICS = "demographics"
    CONDITIONS = "conditions"
    MEDICATIONS = "medications"
    OBSERVATIONS = "observations"
    ALLERGIES = "allergies"


SECTION_PROMPTS: dict[SectionType, str] = {
    SectionType.DEMOGRAPHICS: """## Patient Demographics

{data_table}

Summarize the patient's demographic information in a brief clinical format including:
- Full name, age, and gender
- Contact information if available
- Any relevant administrative details (language preferences, marital status)

Keep the summary concise (2-3 sentences) and professionally formatted.""",
    SectionType.CONDITIONS: """## Medical Conditions and Diagnoses

{data_table}

Provide a clinical summary of the patient's conditions:
1. **Active Conditions**: Current problems requiring attention, organized by clinical priority
2. **Chronic Conditions**: Ongoing conditions under management
3. **Resolved/Historical**: Significant past conditions if relevant to current care

Use standard medical terminology. Highlight clinically significant findings. If onset dates are available, note duration of conditions.""",
    SectionType.MEDICATIONS: """## Current Medications

{data_table}

Summarize the patient's medication regimen:
1. **Active Medications**: List current medications with dosing information
2. **Therapeutic Categories**: Note the general therapeutic purposes if apparent
3. **Notable Considerations**: Flag any high-alert medications if present

Format as a clear medication summary suitable for clinical review.""",
    SectionType.OBSERVATIONS: """## Vital Signs and Laboratory Results

{data_table}

Provide a clinical interpretation of the observations:

**Vital Signs** (if present):
- Recent vital sign values with any abnormalities noted

**Laboratory Results** (if present):
- Key lab values organized by category
- Flag abnormal values with clinical context
- Note interpretations (H/L) where provided

Focus on clinically significant findings. Reference normal ranges where interpretation aids understanding.""",
    SectionType.ALLERGIES: """## Allergies and Intolerances

{data_table}

Summarize allergy information:
1. **Drug Allergies**: List all medication allergies with reactions and severity
2. **Food Allergies**: Clinically significant food allergies
3. **Other Allergies**: Environmental or other sensitivities
4. **Criticality**: Note high-criticality allergies prominently

This is safety-critical information - be thorough and clear. Flag any high-risk allergies prominently.""",
}
