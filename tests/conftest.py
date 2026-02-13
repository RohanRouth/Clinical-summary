import pytest


@pytest.fixture
def sample_patient_resource():
    """Sample FHIR Patient resource for testing."""
    return {
        "resourceType": "Patient",
        "id": "test-patient-123",
        "name": [
            {
                "use": "official",
                "family": "Smith",
                "given": ["John", "Robert"],
            }
        ],
        "gender": "male",
        "birthDate": "1970-01-15",
        "address": [
            {
                "line": ["123 Main St"],
                "city": "Boston",
                "state": "MA",
                "postalCode": "02101",
            }
        ],
        "telecom": [
            {"system": "phone", "value": "555-123-4567"},
            {"system": "email", "value": "john.smith@email.com"},
        ],
    }


@pytest.fixture
def sample_condition_resource():
    """Sample FHIR Condition resource for testing."""
    return {
        "resourceType": "Condition",
        "id": "condition-123",
        "code": {
            "coding": [
                {
                    "system": "http://snomed.info/sct",
                    "code": "44054006",
                    "display": "Type 2 diabetes mellitus",
                }
            ]
        },
        "clinicalStatus": {
            "coding": [{"code": "active", "display": "Active"}]
        },
        "verificationStatus": {
            "coding": [{"code": "confirmed", "display": "Confirmed"}]
        },
        "onsetDateTime": "2015-03-01",
    }


@pytest.fixture
def sample_medication_request_resource():
    """Sample FHIR MedicationRequest resource for testing."""
    return {
        "resourceType": "MedicationRequest",
        "id": "medrx-123",
        "status": "active",
        "intent": "order",
        "medicationCodeableConcept": {
            "coding": [
                {
                    "system": "http://www.nlm.nih.gov/research/umls/rxnorm",
                    "code": "860975",
                    "display": "Metformin 500 MG Oral Tablet",
                }
            ]
        },
        "dosageInstruction": [
            {
                "text": "Take 1 tablet by mouth twice daily",
                "timing": {"code": {"text": "BID"}},
                "doseAndRate": [
                    {
                        "doseQuantity": {"value": 500, "unit": "mg"}
                    }
                ],
                "route": {
                    "coding": [{"display": "Oral"}]
                },
            }
        ],
        "authoredOn": "2024-01-15",
    }
