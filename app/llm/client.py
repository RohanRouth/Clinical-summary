from openai import AsyncOpenAI

from app.config import get_settings


class LLMClient:
    """OpenAI client wrapper for generating clinical summaries."""

    def __init__(self):
        settings = get_settings()
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
        self.temperature = settings.llm_temperature
        self.max_tokens = settings.llm_max_tokens

    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        """Generate a completion for the given prompt."""
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature or self.temperature,
            max_tokens=max_tokens or self.max_tokens,
        )

        return response.choices[0].message.content or ""

    async def generate_section_summary(self, prompt: str) -> str:
        """Generate a section summary with clinical documentation system prompt."""
        return await self.generate(
            prompt=prompt,
            system_prompt=(
                "You are a clinical documentation specialist. "
                "Provide concise, accurate clinical summaries using standard medical terminology. "
                "Focus on clinically significant information."
            ),
            max_tokens=500,
        )

    async def generate_final_summary(self, prompt: str) -> str:
        """Generate the final comprehensive clinical summary."""
        return await self.generate(
            prompt=prompt,
            system_prompt=(
                "You are a clinical documentation specialist creating a comprehensive patient summary. "
                "Synthesize all available clinical data into a cohesive, professionally-formatted narrative "
                "suitable for healthcare provider review."
            ),
        )
