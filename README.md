# Clinical Patient Summary API

A FastAPI application that generates comprehensive clinical patient summaries by querying FHIR R4 resources and using LLM-powered analysis to create coherent clinical narratives.

## Features

- **FHIR R4 Integration**: Queries patient data from any FHIR R4-compliant server (default: HAPI public server)
- **Parallel Data Fetching**: Asynchronously fetches multiple resource types simultaneously
- **Structured Data Extraction**: Converts complex FHIR resources into clean pandas DataFrames
- **LLM-Powered Summarization**: Uses OpenAI GPT models to generate clinical narratives
- **Two-Stage Summarization**: Section-specific summaries combined into a comprehensive final summary
- **RESTful API**: Clean JSON responses with full OpenAPI documentation

## Supported FHIR Resources

| Resource | Clinical Data |
|----------|---------------|
| Patient | Demographics, contact info, language preferences |
| Condition | Diagnoses, problems, clinical status, severity |
| MedicationRequest | Current medications, dosing, frequency |
| Observation | Vital signs, lab results, interpretations |
| AllergyIntolerance | Allergies, reactions, criticality |

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    GET /api/v1/summary/{patient_id}             │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│  FHIR CLIENT                                                     │
│  Parallel async HTTP requests to FHIR server                     │
│  ┌─────────┐ ┌───────────┐ ┌──────────┐ ┌─────┐ ┌───────┐      │
│  │ Patient │ │ Condition │ │ MedReq   │ │ Obs │ │Allergy│      │
│  └─────────┘ └───────────┘ └──────────┘ └─────┘ └───────┘      │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│  RESOURCE HANDLERS                                               │
│  Extract relevant fields → Convert to pandas DataFrames          │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│  PROMPT ASSEMBLER                                                │
│  DataFrame → Markdown table → Section-specific prompt            │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│  LLM CLIENT (OpenAI)                                             │
│  Generate 5 section summaries → Combine into final summary       │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│  JSON RESPONSE                                                   │
│  { summary, sections, data_availability, processing_time }       │
└─────────────────────────────────────────────────────────────────┘
```

## Installation

### Prerequisites

- Python 3.11+
- OpenAI API key

### Setup

```bash
# Clone the repository
git clone <repository-url>
cd Clinical-summary

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .

# Configure environment
cp .env.example .env
# Edit .env and add your OpenAI API key
```

## Configuration

Create a `.env` file in the project root:

```env
# FHIR Server Configuration
FHIR_BASE_URL=http://hapi.fhir.org/baseR4
FHIR_TIMEOUT=30

# OpenAI Configuration
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-4o
LLM_TEMPERATURE=0.3
LLM_MAX_TOKENS=2000

# Application Settings
DEBUG=false
LOG_LEVEL=INFO
```

### Configuration Options

| Variable | Default | Description |
|----------|---------|-------------|
| `FHIR_BASE_URL` | `http://hapi.fhir.org/baseR4` | FHIR R4 server endpoint |
| `FHIR_TIMEOUT` | `30` | HTTP timeout in seconds |
| `OPENAI_API_KEY` | - | Your OpenAI API key (required) |
| `OPENAI_MODEL` | `gpt-4o` | Model to use (`gpt-4o`, `gpt-4o-mini`, `gpt-3.5-turbo`) |
| `LLM_TEMPERATURE` | `0.3` | Response randomness (0.0-1.0) |
| `LLM_MAX_TOKENS` | `2000` | Max tokens for final summary |

## Usage

### Start the Server

```bash
# Development mode with auto-reload
uvicorn app.main:app --reload

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### API Endpoints

#### Health Check
```bash
curl http://localhost:8000/health
# {"status": "healthy"}
```

#### Generate Patient Summary
```bash
curl http://localhost:8000/api/v1/summary/{patient_id}
```

#### Debug: View Raw Extracted Data
```bash
curl http://localhost:8000/api/v1/resources/{patient_id}
```

### Example Response

```json
{
  "patient_id": "12345",
  "generated_at": "2026-02-13T00:27:21.162440",
  "summary": "## 1. Patient Overview\nJohn Smith is a 54-year-old male...",
  "sections": {
    "demographics": "Full Name: John Smith, Age: 54, Gender: Male...",
    "conditions": "### Active Conditions\n1. Type 2 Diabetes...",
    "medications": "### Active Medications\n- Metformin 500mg BID...",
    "observations": "### Vital Signs\n- Blood Pressure: 130/85 mmHg...",
    "allergies": "### Drug Allergies\n- Penicillin (severe)..."
  },
  "data_availability": {
    "Patient": true,
    "Condition": true,
    "MedicationRequest": true,
    "Observation": true,
    "AllergyIntolerance": true
  },
  "processing_time_ms": 15234,
  "model": "gpt-4o"
}
```

### Interactive API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Project Structure

```
Clinical-summary/
├── pyproject.toml              # Dependencies and project metadata
├── .env.example                # Environment template
├── .env                        # Your configuration (git-ignored)
├── .gitignore
├── README.md
│
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application factory
│   ├── config.py               # Pydantic Settings configuration
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── summary.py      # Main summary endpoint
│   │       └── health.py       # Health check endpoint
│   │
│   ├── fhir/
│   │   ├── __init__.py
│   │   ├── client.py           # Async FHIR HTTP client
│   │   └── resources/
│   │       ├── __init__.py
│   │       ├── base.py         # Abstract base handler
│   │       ├── patient.py      # Patient resource handler
│   │       ├── condition.py    # Condition resource handler
│   │       ├── medication_request.py
│   │       ├── observation.py
│   │       └── allergy.py
│   │
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── client.py           # OpenAI client wrapper
│   │   └── prompts/
│   │       ├── __init__.py
│   │       ├── section_prompts.py  # Per-resource prompts
│   │       ├── final_prompt.py     # Final summary template
│   │       └── assembler.py        # Prompt builder
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── responses.py        # Pydantic response models
│   │
│   └── processing/
│       └── __init__.py
│
└── tests/
    ├── __init__.py
    └── conftest.py             # Pytest fixtures
```

## Extending the Application

### Adding a New FHIR Resource

1. **Create a new handler** in `app/fhir/resources/`:

```python
# app/fhir/resources/procedure.py
from typing import Any
from .base import BaseResourceHandler

class ProcedureHandler(BaseResourceHandler):
    resource_type = "Procedure"

    def extract_fields(self, resource: dict[str, Any]) -> dict[str, Any]:
        return {
            "procedure_id": resource.get("id", ""),
            "procedure_name": self._extract_codeable_concept(resource.get("code")),
            "status": resource.get("status", ""),
            "performed_date": resource.get("performedDateTime", ""),
            # Add more fields as needed
        }
```

2. **Add the handler** to `app/fhir/resources/__init__.py`:

```python
from .procedure import ProcedureHandler
__all__ = [..., "ProcedureHandler"]
```

3. **Register in the endpoint** (`app/api/routes/summary.py`):

```python
RESOURCE_HANDLERS = {
    ...
    "Procedure": ProcedureHandler(),
}
```

4. **Add section prompt** in `app/llm/prompts/section_prompts.py`:

```python
class SectionType(str, Enum):
    ...
    PROCEDURES = "procedures"

SECTION_PROMPTS = {
    ...
    SectionType.PROCEDURES: """## Surgical and Procedural History
{data_table}

Summarize the patient's procedures..."""
}
```

5. **Update the assembler mapping** in `app/llm/prompts/assembler.py`:

```python
RESOURCE_TO_SECTION = {
    ...
    "Procedure": SectionType.PROCEDURES,
}
```

### Switching LLM Providers

To use a different LLM (e.g., Anthropic Claude), modify `app/llm/client.py`:

```python
from anthropic import AsyncAnthropic

class LLMClient:
    def __init__(self):
        self.client = AsyncAnthropic(api_key=settings.anthropic_api_key)

    async def generate(self, prompt: str, ...) -> str:
        response = await self.client.messages.create(
            model="claude-sonnet-4-20250514",
            messages=[{"role": "user", "content": prompt}],
            ...
        )
        return response.content[0].text
```

## Testing

### Finding Test Patient IDs

The HAPI public FHIR server contains test data:

```bash
# List some patients
curl "http://hapi.fhir.org/baseR4/Patient?_count=5"

# Search by name
curl "http://hapi.fhir.org/baseR4/Patient?name=smith&_count=5"
```

### Running Tests

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=app
```

## Performance Considerations

- **FHIR queries run in parallel** - All 5 resource types are fetched concurrently
- **LLM calls are sequential** - Each section summary waits for the previous (ensures coherence)
- **Typical response time**: 15-30 seconds (depends on LLM model and data volume)
- **For faster responses**: Use `gpt-4o-mini` or `gpt-3.5-turbo`

## Error Handling

| HTTP Code | Meaning |
|-----------|---------|
| 200 | Success |
| 404 | Patient not found in FHIR server |
| 500 | Internal error (FHIR query failed, LLM error) |

## Security Notes

- Store API keys in `.env` (never commit to git)
- The `.env` file is git-ignored by default
- HAPI public server is for testing only - do not store real patient data
- For production, use a secured FHIR server with proper authentication

## License

MIT

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request
