# TheCarePal AI-07 — Daily Care Notes to Family Report

A Streamlit prototype that converts English, Hindi and Hinglish nurse notes into structured daily care reports, evidence-linked facts, separately flagged concerns, and concise family updates.

> **Safety:** This is an internship demo using synthetic data only. It is not a clinical decision-support system. It does not diagnose or recommend treatment. A qualified care professional must review reports before sharing them with families.

## Features

- Text input for nurse notes.
- Audio upload and transcription using Groq Whisper Large V3.
- AI-powered extraction using GPT-OSS 20B via the Groq API.
- Structured extraction of vitals, meals, medicines, activities, mood and concerns.
- Every extracted item includes an exact evidence quote from the original note.
- Post-processing rejects items whose evidence is not an exact substring of the source note.
- Missing categories remain empty and are displayed as "Not mentioned".
- Attention-worthy observations are separately flagged under concerns.
- Family summaries are assembled from extracted facts rather than generated independently, reducing unsupported additions.
- JSON report download for downstream use.
- 25 synthetic multilingual notes in `data/synthetic_notes.jsonl`.

## Tech Stack

- **Frontend:** Streamlit
- **LLM:** GPT-OSS 20B via Groq API
- **Speech-to-Text:** Whisper Large V3 via Groq API
- **Data Validation:** Pydantic
- **Language Support:** English, Hindi and Hinglish
- **Programming Language:** Python

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/TheCarePal-AI-Solution.git
cd TheCarePal-AI-Solution
```

### 2. Install Python

Install Python 3.10 or newer.

### 3. Create and activate a virtual environment

**Windows PowerShell:**

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**macOS/Linux:**

```bash
python -m venv .venv
source .venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure environment variables

Create a `.env` file in the project root directory:

```env
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=openai/gpt-oss-20b
WHISPER_MODEL=base
```

Replace `your_groq_api_key` with your API key from the Groq Console.

**Never upload your `.env` file or expose your API key publicly.**

### 6. Run the application

```bash
streamlit run app.py
```

The application will open in your browser.

## How It Works

1. The nurse enters a daily care note or uploads an audio recording.
2. Uploaded audio is transcribed using Groq's Whisper Large V3 model.
3. The transcribed or written note is processed using GPT-OSS 20B via Groq.
4. The model extracts information into structured categories: vitals, meals, medicines, activities, mood and concerns.
5. Each extracted fact must include exact evidence copied from the original note.
6. Python validates each evidence quote against the source note.
7. Items with invalid evidence are rejected and logged.
8. A concise family summary is assembled using the validated facts.
9. The generated report can be downloaded as a JSON file.

## Data Structure

Each extracted category contains objects in the following format:

```json
{
  "value": "Blood pressure 120/80",
  "evidence": "BP 120/80 tha"
}
```

The report contains the following categories:

- `vitals`
- `meals`
- `medicines`
- `activities`
- `mood`
- `concerns`
- `language_detected`

## Evaluation

- `data/synthetic_notes.jsonl` contains 25 synthetic English, Hindi and Hinglish examples.
- The test cases include routine updates, missing information, missed medicines, fever, falls, pain and low food/fluid intake.
- `evaluation.py` runs the notes through the extraction pipeline and reports accepted evidence-backed items, rejected evidence, processing errors and evidence-grounding rate.
- `EVALUATION.md` contains the evaluation methodology, metrics, limitations and results template.

Run the evaluation using:

```bash
python evaluation.py
```

The evaluation requires a valid Groq API key and API connectivity.

The evidence-grounding rate measures whether extracted items contain valid source quotations. It does not independently establish semantic accuracy, completeness or correct categorization. Results should be manually reviewed before reporting performance.

## Costs

- Python, Streamlit, Pydantic and other supporting libraries are open-source.
- GPT-OSS 20B extraction uses the Groq API.
- Audio transcription uses the Groq Whisper Large V3 API.
- API usage is subject to provider pricing, rate limits and availability.
- Costs depend on usage and the provider's current pricing.
- No Firebase integration or separate database is required for this prototype.

## Limitations

- Exact substring validation verifies evidence presence but cannot guarantee that the extracted value correctly interprets the quote.
- Speech transcription may misrecognize names, medicine names, numbers or units.
- Hindi and Hinglish code-switching and spelling variations may affect transcription and extraction.
- The model may omit information or assign it to an incorrect category.
- Concerns are observations for human attention, not diagnoses or urgency determinations.
- The application has not been validated for clinical use.
- The prototype does not connect to Firebase, a CRM, nurse app or family portal.
- Only synthetic data should be used for demonstrations.

## Future Improvements

1. Add a human review, edit and approval workflow before reports are shared.
2. Add family language preferences and verified report translations.
3. Generate weekly summaries from approved daily reports.
4. Implement role-based access, audit logs, encryption, retention controls and consent management.
5. Improve extraction using a manually annotated gold dataset and regression testing.
6. Integrate Firebase after security, privacy and product requirements are established.

## AI and Tools Used

- **Groq API — GPT-OSS 20B:** Structured extraction of care-related information from multilingual nurse notes.
- **Groq API — Whisper Large V3:** Speech-to-text transcription of uploaded voice notes.
- **Pydantic:** Validation of the structured report schema.
- **Python Evidence Validator:** Deterministic validation that extracted evidence quotes exist exactly in the source note.

The evidence validator acts as a guardrail against unsupported evidence; it does not guarantee that the AI's interpretation is correct.
