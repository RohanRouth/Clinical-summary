import asyncio
from typing import Any

import httpx

from app.config import get_settings


class FHIRClient:
    """Async FHIR R4 client for querying resources from HAPI server."""

    def __init__(self, base_url: str | None = None):
        settings = get_settings()
        self.base_url = base_url or settings.fhir_base_url
        self.timeout = settings.fhir_timeout
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> "FHIRClient":
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
            headers={"Accept": "application/fhir+json"},
        )
        return self

    async def __aexit__(self, *args) -> None:
        if self._client:
            await self._client.aclose()

    async def get_resource(
        self, resource_type: str, resource_id: str
    ) -> dict[str, Any] | None:
        """Fetch a single resource by ID."""
        if not self._client:
            raise RuntimeError("Client not initialized. Use async context manager.")

        response = await self._client.get(f"/{resource_type}/{resource_id}")
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()

    async def search_resources(
        self, resource_type: str, params: dict[str, str]
    ) -> list[dict[str, Any]]:
        """Search for resources with given parameters."""
        if not self._client:
            raise RuntimeError("Client not initialized. Use async context manager.")

        response = await self._client.get(
            f"/{resource_type}",
            params={**params, "_format": "json"},
        )
        response.raise_for_status()
        bundle = response.json()

        # Extract resources from FHIR Bundle
        entries = bundle.get("entry", [])
        return [entry["resource"] for entry in entries if "resource" in entry]

    async def get_patient_resources(
        self, patient_id: str, resource_types: list[str]
    ) -> dict[str, list[dict[str, Any]]]:
        """Fetch all resource types for a patient in parallel."""

        async def fetch_resource_type(res_type: str) -> tuple[str, list[dict[str, Any]]]:
            try:
                if res_type == "Patient":
                    result = await self.get_resource("Patient", patient_id)
                    return (res_type, [result] if result else [])
                else:
                    results = await self.search_resources(
                        res_type,
                        {"patient": patient_id, "_count": "100"},
                    )
                    return (res_type, results)
            except httpx.HTTPStatusError:
                return (res_type, [])

        # Execute all queries in parallel
        tasks = [fetch_resource_type(rt) for rt in resource_types]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results, handling any errors gracefully
        output: dict[str, list[dict[str, Any]]] = {}
        for result in results:
            if isinstance(result, Exception):
                continue
            res_type, resources = result
            output[res_type] = resources

        return output
