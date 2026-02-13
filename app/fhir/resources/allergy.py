from typing import Any

from .base import BaseResourceHandler


class AllergyHandler(BaseResourceHandler):
    """Handler for FHIR AllergyIntolerance resource."""

    resource_type = "AllergyIntolerance"

    def extract_fields(self, resource: dict[str, Any]) -> dict[str, Any]:
        return {
            "allergy_id": resource.get("id", ""),
            "allergen": self._extract_codeable_concept(resource.get("code")),
            "clinical_status": self._extract_codeable_concept(
                resource.get("clinicalStatus")
            ),
            "verification_status": self._extract_codeable_concept(
                resource.get("verificationStatus")
            ),
            "type": resource.get("type", ""),
            "category": self._extract_categories(resource),
            "criticality": resource.get("criticality", ""),
            "onset_date": self._extract_onset(resource),
            "reaction": self._extract_reaction(resource),
            "reaction_severity": self._extract_reaction_severity(resource),
        }

    def _extract_categories(self, resource: dict) -> str:
        """Extract allergy categories (food, medication, environment, biologic)."""
        categories = resource.get("category", [])
        return ", ".join(categories) if categories else ""

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

    def _extract_reaction(self, resource: dict) -> str:
        """Extract reaction manifestations."""
        reactions = resource.get("reaction", [])
        if not reactions:
            return ""

        # Get manifestations from first reaction
        manifestations = reactions[0].get("manifestation", [])
        if not manifestations:
            return ""

        # Extract display text from all manifestations
        texts = [self._extract_codeable_concept(m) for m in manifestations]
        return ", ".join(filter(None, texts))

    def _extract_reaction_severity(self, resource: dict) -> str:
        """Extract reaction severity (mild, moderate, severe)."""
        reactions = resource.get("reaction", [])
        if not reactions:
            return ""
        return reactions[0].get("severity", "")
