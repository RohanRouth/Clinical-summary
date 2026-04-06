from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams

MCP_SERVER_URL = "http://localhost:8000/mcp"

AGENT_INSTRUCTION = """You are a clinical assistant that helps healthcare providers
retrieve comprehensive patient summaries from a FHIR-based clinical system.

When a user asks about a patient, use the get_patient_summary tool to retrieve their
clinical summary. The tool requires a patient_id (e.g. "123" or "pat-456").

When presenting results, highlight active conditions, current medications, and
critical allergies. Use clear, professional clinical language.

If the patient is not found, inform the user and suggest verifying the patient ID.
If unsure of the patient ID, ask the user to confirm before calling the tool."""

root_agent = LlmAgent(
    name="clinical_summary_agent",
    model=LiteLlm(model="openai/gpt-4o-mini"),
    instruction=AGENT_INSTRUCTION,
    tools=[
        McpToolset(
            connection_params=StreamableHTTPConnectionParams(
                url=MCP_SERVER_URL,
            ),
            tool_filter=["get_patient_summary"],
        )
    ],
)
