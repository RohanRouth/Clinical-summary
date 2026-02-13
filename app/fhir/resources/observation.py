from typing import Any

from .base import BaseResourceHandler


class ObservationHandler(BaseResourceHandler):
    """Handler for FHIR Observation resource."""

    resource_type = "Observation"

    def extract_fields(self, resource: dict[str, Any]) -> dict[str, Any]:
        code = resource.get("code", {})
        coding = code.get("coding", [{}])[0] if code.get("coding") else {}

        return {
            "observation_id": resource.get("id", ""),
            "observation_name": self._extract_codeable_concept(code),
            "loinc_code": coding.get("code", ""),
            "value": self._extract_value(resource),
            "unit": self._extract_unit(resource),
            "status": resource.get("status", ""),
            "category": self._extract_category(resource),
            "effective_date": self._extract_effective_date(resource),
            "interpretation": self._extract_interpretation(resource),
            "reference_range": self._extract_reference_range(resource),
        }

    def _extract_value(self, resource: dict) -> str:
        """Extract value from various value[x] types."""
        if "valueQuantity" in resource:
            return str(resource["valueQuantity"].get("value", ""))
        if "valueCodeableConcept" in resource:
            return self._extract_codeable_concept(resource["valueCodeableConcept"])
        if "valueString" in resource:
            return resource["valueString"]
        if "valueBoolean" in resource:
            return str(resource["valueBoolean"])
        if "valueInteger" in resource:
            return str(resource["valueInteger"])
        if "valueRange" in resource:
            low = self._safe_get(resource, "valueRange", "low", "value")
            high = self._safe_get(resource, "valueRange", "high", "value")
            return f"{low}-{high}" if low and high else ""
        if "valueRatio" in resource:
            num = self._safe_get(resource, "valueRatio", "numerator", "value")
            den = self._safe_get(resource, "valueRatio", "denominator", "value")
            return f"{num}/{den}" if num and den else ""
        return ""

    def _extract_unit(self, resource: dict) -> str:
        """Extract unit from valueQuantity."""
        if "valueQuantity" in resource:
            return resource["valueQuantity"].get("unit", "")
        return ""

    def _extract_category(self, resource: dict) -> str:
        """Extract observation category."""
        categories = resource.get("category", [])
        if not categories:
            return ""
        return self._extract_codeable_concept(categories[0])

    def _extract_effective_date(self, resource: dict) -> str:
        """Extract effective date from various effective[x] types."""
        if "effectiveDateTime" in resource:
            return resource["effectiveDateTime"]
        if "effectivePeriod" in resource:
            return resource["effectivePeriod"].get("start", "")
        if "effectiveInstant" in resource:
            return resource["effectiveInstant"]
        return ""

    def _extract_interpretation(self, resource: dict) -> str:
        """Extract interpretation (H/L/N etc)."""
        interpretations = resource.get("interpretation", [])
        if not interpretations:
            return ""
        return self._extract_codeable_concept(interpretations[0])

    def _extract_reference_range(self, resource: dict) -> str:
        """Extract reference range."""
        ranges = resource.get("referenceRange", [])
        if not ranges:
            return ""

        ref_range = ranges[0]
        low = self._safe_get(ref_range, "low", "value")
        high = self._safe_get(ref_range, "high", "value")
        unit = self._safe_get(ref_range, "low", "unit") or self._safe_get(
            ref_range, "high", "unit"
        )

        if low is not None and high is not None:
            return f"{low}-{high} {unit}".strip()
        if low is not None:
            return f">= {low} {unit}".strip()
        if high is not None:
            return f"<= {high} {unit}".strip()
        return ref_range.get("text", "")
