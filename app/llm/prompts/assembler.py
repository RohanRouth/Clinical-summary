import pandas as pd

from .final_prompt import FINAL_SUMMARY_PROMPT
from .section_prompts import SECTION_PROMPTS, SectionType


class PromptAssembler:
    """Assembles section and final prompts from DataFrames."""

    RESOURCE_TO_SECTION: dict[str, SectionType] = {
        "Patient": SectionType.DEMOGRAPHICS,
        "Condition": SectionType.CONDITIONS,
        "MedicationRequest": SectionType.MEDICATIONS,
        "Observation": SectionType.OBSERVATIONS,
        "AllergyIntolerance": SectionType.ALLERGIES,
    }

    def build_section_prompt(self, section_type: SectionType, df: pd.DataFrame) -> str:
        """Build a single section prompt from DataFrame."""
        template = SECTION_PROMPTS[section_type]

        if df.empty:
            data_table = "*No data available for this section*"
        else:
            data_table = df.to_markdown(index=False)

        return template.format(data_table=data_table)

    def build_all_section_prompts(
        self, dataframes: dict[str, pd.DataFrame]
    ) -> dict[SectionType, str]:
        """Build prompts for all sections from resource DataFrames."""
        prompts: dict[SectionType, str] = {}

        for resource_type, df in dataframes.items():
            section_type = self.RESOURCE_TO_SECTION.get(resource_type)
            if section_type:
                prompts[section_type] = self.build_section_prompt(section_type, df)

        return prompts

    def build_final_prompt(self, section_summaries: dict[SectionType, str]) -> str:
        """Build the final comprehensive summary prompt."""
        # Order sections logically
        section_order = [
            SectionType.DEMOGRAPHICS,
            SectionType.CONDITIONS,
            SectionType.MEDICATIONS,
            SectionType.OBSERVATIONS,
            SectionType.ALLERGIES,
        ]

        sections_parts = []
        for section_type in section_order:
            if section_type in section_summaries:
                section_name = section_type.value.replace("_", " ").title()
                summary = section_summaries[section_type]
                sections_parts.append(f"### {section_name}\n{summary}")

        sections_text = "\n\n".join(sections_parts)
        return FINAL_SUMMARY_PROMPT.format(all_sections=sections_text)
