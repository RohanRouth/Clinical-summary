from typing import Any

from .base import BaseResourceHandler


class ConditionHandler(BaseResourceHandler):
    """Handler for FHIR Condition resource."""

    resource_type = "Condition"

    def extract_fields(self, resource: dict[str, Any]) -> dict[str, Any]:
        return {
            "condition_id": resource.get("id", ""),
            "condition_name": self._extract_codeable_concept(resource.get("code")),
            "clinical_status": self._extract_codeable_concept(
                resource.get("clinicalStatus")
            ),
            "verification_status": self._extract_codeable_concept(
                resource.get("verificationStatus")
            ),
            "severity": self._extract_codeable_concept(resource.get("severity")),
            "category": self._extract_codeable_concept(
                self._safe_get(resource, "category", 0)
            ),
            "onset_date": self._extract_onset(resource),
            "abatement_date": self._extract_abatement(resource),
            "recorded_date": resource.get("recordedDate", ""),
        }

    def _extract_onset(self, resource: dict) -> str:
        """Extract onset from various onset[x] types."""
        if "onsetDateTime" in resource:
            return resource["onsetDateTime"]
        if "onsetAge" in resource:
            age = resource["onsetAge"]
            return f"{age.get('value', '')} {age.get('unit', 'years')}"
        if "onsetPeriod" in resource:
            return resource["onsetPeriod"].get("start", "")
        if "onsetRange" in resource:
            low = self._safe_get(resource, "onsetRange", "low", "value")
            return str(low) if low else ""
        if "onsetString" in resource:
            return resource["onsetString"]
        return ""

    def _extract_abatement(self, resource: dict) -> str:
        """Extract abatement from various abatement[x] types."""
        if "abatementDateTime" in resource:
            return resource["abatementDateTime"]
        if "abatementAge" in resource:
            age = resource["abatementAge"]
            return f"{age.get('value', '')} {age.get('unit', 'years')}"
        if "abatementPeriod" in resource:
            return resource["abatementPeriod"].get("start", "")
        if "abatementString" in resource:
            return resource["abatementString"]
        return ""
