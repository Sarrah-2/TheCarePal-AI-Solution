# TheCarePal AI-07 — Daily Care Notes to Family Report

A Streamlit prototype that converts English, Hindi and Hinglish nurse notes into structured daily care reports, evidence-linked facts, separately flagged concerns, and a concise family update.

> **Safety:** This is an internship demo using synthetic data only. It is not a clinical decision-support system. It does not diagnose or recommend treatment. A qualified care professional must review reports before sharing them with families.

## Features
- Text input for nurse notes.
- Optional audio upload and transcription using Faster-Whisper.
- Gemini extraction into vitals, meals, medicines, activities, mood and concerns.
- Every extracted item must include an exact verbatim evidence quote from the original note.
- Post-processing rejects items whose evidence is not an exact substring of the source note.
- Missing categories remain empty and are displayed as “Not mentioned”.
- Family summary is assembled from extracted facts rather than generated independently, reducing unsupported additions.
- JSON download for downstream use.
- 25 synthetic multilingual notes in `data/synthetic_notes.jsonl`.

## Setup
1. Install Python 3.10 or newer.
2. Create and activate a virtual environment:
   - Windows PowerShell: `python -m venv .venv` then `.venv\Scripts\Activate.ps1`
   - macOS/Linux: `python -m venv .venv` then `source .venv/bin/activate`
3. Install dependencies: `pip install -r requirements.txt`
4. Copy `.env.example` to `.env` and add your Gemini API key.
5. Run: `streamlit run app.py`

Audio transcription downloads/loads the selected Whisper model on first use and is CPU-intensive. If setup time is limited, demonstrate the text workflow; audio is implemented as an optional path.

## How it works
1. The nurse enters text or uploads audio.
2. Faster-Whisper transcribes audio to text (when audio is used).
3. Gemini receives a strict extraction instruction and a Pydantic response schema.
4. The model returns facts with exact source evidence.
5. Python validates each evidence quote against the original note. Any unsupported item is discarded and logged.
6. The family summary is composed only from validated extracted facts. Empty categories are not filled with guesses.

### Data structure
Each category contains a list of `{ "value": "...", "evidence": "exact source quote" }` objects. Categories are `vitals`, `meals`, `medicines`, `activities`, `mood`, and `concerns`.

## Evaluation
- `data/synthetic_notes.jsonl` contains 25 realistic English, Hindi and Hinglish examples, including normal updates and attention-worthy cases.
- `evaluation.py` runs each note through the same extraction pipeline and reports the number of evidence-backed items, rejected items, empty outputs, and exact-evidence grounding rate.
- The evaluation report template is in `EVALUATION.md`. Run the script with a valid `.env` to obtain actual model-run results. Do not report a score until the run has completed and outputs have been manually reviewed.

## Costs
- Python, Streamlit, Pydantic, Pandas, python-dotenv and Faster-Whisper are open-source packages; no per-call software licence fee. Compute, hosting and storage may still cost money.
- Gemini API usage is subject to Google's current model pricing, quotas and regional availability. Cost depends on input/output tokens and the selected model. Check the current official Gemini API pricing before deployment; this repository does not hard-code a price.
- Whisper transcription runs locally in this prototype, so there is no per-minute API fee, but it uses CPU/RAM and downloads a model. Hosted deployment may require a larger machine.
- Streamlit Community Cloud may offer a free tier subject to current limits; Firebase is not required for this standalone prototype.

## Limitations and assumptions
- Exact substring validation catches unsupported evidence but cannot guarantee that a model's `value` is a faithful interpretation of its quote. Human review remains necessary.
- Hinglish spelling varies; transcription and extraction may make mistakes.
- The prototype does not connect to TheCarePal's Firebase, CRM, nurse app or family portal.
- Concern categories are observations for human attention, not diagnoses or urgency determinations.
- No real patient data should be entered.

## What I would build next
1. Add human review/edit/approve workflow before a family receives a report.
2. Add family language preference and verified translation of the approved report.
3. Generate a weekly summary from seven approved daily reports.
4. Add role-based access, audit logs, encryption, retention controls and consent.
5. Improve extraction with a reviewed gold dataset, field-level confidence calibration and regression tests.
6. Integrate with Firebase only after security, privacy and product requirements are agreed.

## AI tools used
- Gemini API: multilingual information extraction into a constrained structured schema.
- Faster-Whisper: local speech-to-text transcription for uploaded voice notes.
- Python evidence validator: rejects extracted items without exact source evidence; it is a deterministic guardrail, not an AI model.
