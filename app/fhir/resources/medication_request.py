from typing import Any

from .base import BaseResourceHandler


class MedicationRequestHandler(BaseResourceHandler):
    """Handler for FHIR MedicationRequest resource."""

    resource_type = "MedicationRequest"

    def extract_fields(self, resource: dict[str, Any]) -> dict[str, Any]:
        dosage = self._extract_dosage(resource)
        return {
            "medication_id": resource.get("id", ""),
            "medication_name": self._extract_medication(resource),
            "status": resource.get("status", ""),
            "intent": resource.get("intent", ""),
            "dosage_text": dosage.get("text", ""),
            "dose_value": dosage.get("dose_value", ""),
            "dose_unit": dosage.get("dose_unit", ""),
            "frequency": dosage.get("frequency", ""),
            "route": dosage.get("route", ""),
            "prescribed_date": resource.get("authoredOn", ""),
            "reason": self._extract_codeable_concept(
                self._safe_get(resource, "reasonCode", 0)
            ),
        }

    def _extract_medication(self, resource: dict) -> str:
        """Extract medication name from medicationCodeableConcept or reference."""
        if "medicationCodeableConcept" in resource:
            return self._extract_codeable_concept(resource["medicationCodeableConcept"])
        if "medicationReference" in resource:
            return self._extract_reference_display(resource["medicationReference"])
        return ""

    def _extract_dosage(self, resource: dict) -> dict[str, str]:
        """Extract dosage information."""
        result = {
            "text": "",
            "dose_value": "",
            "dose_unit": "",
            "frequency": "",
            "route": "",
        }

        dosage_instructions = resource.get("dosageInstruction", [])
        if not dosage_instructions:
            return result

        dosage = dosage_instructions[0]

        # Text instruction
        result["text"] = dosage.get("text", "")

        # Dose quantity
        dose_and_rate = dosage.get("doseAndRate", [])
        if dose_and_rate:
            dose_qty = dose_and_rate[0].get("doseQuantity", {})
            result["dose_value"] = str(dose_qty.get("value", ""))
            result["dose_unit"] = dose_qty.get("unit", "")

        # Frequency/timing
        timing = dosage.get("timing", {})
        if timing:
            timing_code = timing.get("code", {})
            result["frequency"] = self._extract_codeable_concept(timing_code)
            if not result["frequency"]:
                # Try to extract from repeat
                repeat = timing.get("repeat", {})
                freq = repeat.get("frequency")
                period = repeat.get("period")
                period_unit = repeat.get("periodUnit")
                if freq and period:
                    result["frequency"] = f"{freq}x per {period} {period_unit}"

        # Route
        result["route"] = self._extract_codeable_concept(dosage.get("route"))

        return result
