from datetime import date
from typing import Any

from .base import BaseResourceHandler


class PatientHandler(BaseResourceHandler):
    """Handler for FHIR Patient resource."""

    resource_type = "Patient"

    def extract_fields(self, resource: dict[str, Any]) -> dict[str, Any]:
        return {
            "patient_id": resource.get("id", ""),
            "full_name": self._extract_name(resource),
            "birth_date": resource.get("birthDate", ""),
            "age": self._calculate_age(resource.get("birthDate")),
            "gender": resource.get("gender", ""),
            "address": self._extract_address(resource),
            "phone": self._extract_telecom(resource, "phone"),
            "email": self._extract_telecom(resource, "email"),
            "language": self._extract_language(resource),
            "marital_status": self._extract_codeable_concept(
                resource.get("maritalStatus")
            ),
        }

    def _extract_name(self, resource: dict) -> str:
        """Extract formatted name from Patient."""
        names = resource.get("name", [])
        if not names:
            return ""

        # Prefer official name, otherwise use first
        name = next((n for n in names if n.get("use") == "official"), names[0])

        given = " ".join(name.get("given", []))
        family = name.get("family", "")
        return f"{given} {family}".strip()

    def _calculate_age(self, birth_date: str | None) -> int | None:
        """Calculate age from birth date."""
        if not birth_date:
            return None
        try:
            birth = date.fromisoformat(birth_date)
            today = date.today()
            age = today.year - birth.year
            if (today.month, today.day) < (birth.month, birth.day):
                age -= 1
            return age
        except ValueError:
            return None

    def _extract_address(self, resource: dict) -> str:
        """Extract formatted address."""
        addresses = resource.get("address", [])
        if not addresses:
            return ""

        addr = addresses[0]
        parts = []
        if addr.get("line"):
            parts.extend(addr["line"])
        if addr.get("city"):
            parts.append(addr["city"])
        if addr.get("state"):
            parts.append(addr["state"])
        if addr.get("postalCode"):
            parts.append(addr["postalCode"])
        if addr.get("country"):
            parts.append(addr["country"])

        return ", ".join(parts)

    def _extract_telecom(self, resource: dict, system: str) -> str:
        """Extract telecom value by system (phone, email)."""
        telecoms = resource.get("telecom", [])
        for telecom in telecoms:
            if telecom.get("system") == system:
                return telecom.get("value", "")
        return ""

    def _extract_language(self, resource: dict) -> str:
        """Extract preferred language."""
        communications = resource.get("communication", [])
        if not communications:
            return ""

        # Prefer preferred language
        comm = next(
            (c for c in communications if c.get("preferred")),
            communications[0] if communications else None,
        )
        if comm:
            return self._extract_codeable_concept(comm.get("language"))
        return ""
