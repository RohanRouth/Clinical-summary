FINAL_SUMMARY_PROMPT = """You are creating a comprehensive clinical patient summary based on the following section summaries.

# Section Summaries

{all_sections}

---

# Instructions

Synthesize all available information into a unified, professionally-formatted clinical summary. Structure your response as follows:

## 1. Patient Overview
Brief identification including name, age, gender, and key demographics (2-3 sentences).

## 2. Active Problem List
Summary of current active conditions requiring clinical attention, organized by priority.

## 3. Medication Summary
Current medication regimen with key therapeutic goals noted.

## 4. Recent Clinical Data
Key vital signs and laboratory findings with any abnormalities highlighted.

## 5. Allergy Alert
List of known allergies with severity/criticality. Flag high-risk allergies prominently.

## 6. Clinical Impression
Brief synthesis of the patient's overall clinical picture (2-3 sentences).

---

**Important Guidelines:**
- Use clear medical terminology appropriate for clinical audiences
- Be concise but comprehensive
- Prioritize clinically significant information
- If data is missing for a section, note "No data available" rather than omitting
- Do not fabricate information not present in the source data
- Flag any safety-critical information (severe allergies, high-alert medications)

Generate the comprehensive clinical summary now:"""
