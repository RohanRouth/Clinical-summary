from abc import ABC, abstractmethod
from typing import Any

import pandas as pd


class BaseResourceHandler(ABC):
    """Abstract base class for FHIR resource handlers."""

    resource_type: str = ""

    @abstractmethod
    def extract_fields(self, resource: dict[str, Any]) -> dict[str, Any]:
        """Extract relevant clinical fields from a FHIR resource."""
        pass

    def to_dataframe(self, resources: list[dict[str, Any]]) -> pd.DataFrame:
        """Convert list of resources to pandas DataFrame."""
        if not resources:
            return pd.DataFrame()

        extracted = [self.extract_fields(r) for r in resources]
        return pd.DataFrame(extracted)

    def _safe_get(self, data: dict | None, *keys, default: Any = None) -> Any:
        """Safely navigate nested dictionary."""
        if data is None:
            return default
        for key in keys:
            if isinstance(data, dict):
                data = data.get(key, default)
            elif isinstance(data, list) and isinstance(key, int):
                data = data[key] if len(data) > key else default
            else:
                return default
            if data is None:
                return default
        return data

    def _extract_codeable_concept(self, cc: dict | None) -> str:
        """Extract display text from CodeableConcept."""
        if not cc:
            return ""
        # Try coding display first, then text
        if "coding" in cc and cc["coding"]:
            coding = cc["coding"][0]
            return coding.get("display") or coding.get("code", "")
        return cc.get("text", "")

    def _extract_reference_display(self, ref: dict | None) -> str:
        """Extract display from Reference."""
        if not ref:
            return ""
        return ref.get("display", ref.get("reference", ""))
