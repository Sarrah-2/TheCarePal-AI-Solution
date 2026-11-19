import time
from pathlib import Path
import os, json, re, tempfile
from datetime import date
import streamlit as st
from dotenv import load_dotenv
from pydantic import BaseModel, Field, ValidationError
from typing import List, Optional

load_dotenv()
st.set_page_config(page_title="TheCarePal | Daily Care Report", page_icon="🩺", layout="wide")

class Fact(BaseModel):
    value: str
    evidence: str

class CareReport(BaseModel):
    vitals: List[Fact] = Field(default_factory=list)
    meals: List[Fact] = Field(default_factory=list)
    medicines: List[Fact] = Field(default_factory=list)
    activities: List[Fact] = Field(default_factory=list)
    mood: List[Fact] = Field(default_factory=list)
    concerns: List[Fact] = Field(default_factory=list)
    language_detected: str = "unknown"

SYSTEM = """You convert a nurse's daily care note into a factual report for a family.
Understand English, Hindi and Hinglish. Do not diagnose, infer, calculate, or add facts.
Only extract facts explicitly stated in the note. If a category is not mentioned, return [].
For every item, evidence MUST be an exact verbatim substring copied from the original note,
including its original language. Keep values concise and preserve units/times.
Put observations that may need attention (e.g. fever, fall, pain, missed/refused medicine,
poor intake, low fluid intake, unusual symptoms) in concerns as well as their relevant
category. Do not label a condition as an emergency or recommend treatment.
Do not invent a mood from behaviour. Use neutral language.
Return only data matching the requested schema."""

def validate_evidence(report: CareReport, source: str):
    """Remove unsupported claims; evidence must be an exact substring of source."""
    rejected = []
    for category in ["vitals","meals","medicines","activities","mood","concerns"]:
        kept = []
        for fact in getattr(report, category):
            if fact.evidence and fact.evidence in source:
                kept.append(fact)
            else:
                rejected.append({"category":category,"value":fact.value,"evidence":fact.evidence})
        setattr(report, category, kept)
    return report, rejected


def extract(note: str):
    from groq import Groq
    import os
    import json
    from pathlib import Path
    from dotenv import load_dotenv

    # Load environment variables from project folder
    env_path = Path(__file__).resolve().parent / ".env"
    load_dotenv(dotenv_path=env_path, override=True)

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY not found. Check your .env file."
        )

    client = Groq(api_key=api_key)

    model = os.getenv(
        "GROQ_MODEL",
        "openai/gpt-oss-20b"
    )

    prompt = f"""
    You are an AI assistant that converts nurse notes
    into accurate daily care reports.

    Understand English, Hindi and Hinglish.

    STRICT RULES:
    1. Extract only facts explicitly mentioned.
    2. Never invent medical information.
    3. Every fact must have exact evidence copied
       from the original note.
    4. If information is missing, return an empty list.
    5. Do not diagnose or recommend treatment.
    6. Put attention-worthy observations in concerns.
    7. Preserve original units, times and meaning.

    Return ONLY valid JSON in this structure:

    {{
      "vitals": [],
      "meals": [],
      "medicines": [],
      "activities": [],
      "mood": [],
      "concerns": [],
           "language_detected": "unknown"
    }}

    Each category must contain objects like:
    {{
      "value": "BP 120/80",
      "evidence": "BP 120/80 tha"
    }}

    Original nurse note:
    {note}
    """

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Return accurate structured JSON. "
                        "Never invent facts."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            response_format={"type": "json_object"},
            max_completion_tokens=2000
        )

        result = response.choices[0].message.content

        if not result:
            raise ValueError("Empty response received from Groq.")

        # Convert JSON into our Pydantic report structure
        report = CareReport.model_validate_json(result)

        # Reject facts whose evidence is not in the source note
        report, rejected = validate_evidence(report, note)

        return report, rejected

    except Exception as e:
        raise RuntimeError(
            f"Groq extraction failed: {str(e)}"
        ) from e


def family_summary(r: CareReport):
    lines = []

    mapping = [
        ("Vitals", r.vitals),
        ("Meals", r.meals),
        ("Medicines", r.medicines),
        ("Activities", r.activities),
        ("Mood", r.mood)
    ]

    for label, facts in mapping:
        if facts:
            details = "; ".join(f.value for f in facts)
            lines.append(f"{label}: {details}")

    if r.concerns:
        details = "; ".join(f.value for f in r.concerns)
        lines.append(f"Attention required: {details}")
    else:
        lines.append("Concerns: None explicitly documented.")

    if not any(getattr(r, cat) for cat in [
        "vitals", "meals", "medicines", "activities", "mood"
    ]):
        return "No care details were documented in the note."

    return "\n\n".join(lines)




def transcribe(upload):
    from groq import Groq

    env_path = Path(__file__).resolve().parent / ".env"
    load_dotenv(env_path, override=True)

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise RuntimeError("GROQ_API_KEY not found in .env")

    client = Groq(api_key=api_key)

    # Read uploaded audio directly
    audio_bytes = upload.getvalue()

    if not audio_bytes:
        raise RuntimeError("Uploaded audio file is empty.")

    # Hindi/Hinglish transcription
    transcription = client.audio.transcriptions.create(
        file=(upload.name, audio_bytes),
        model="whisper-large-v3",
        language="hi",
        response_format="json",
        temperature=0.0,
        prompt=(
            "This is a Hindi and Hinglish conversation about "
            "daily elderly care. Recognize Hindi words and common "
            "English words such as breakfast, lunch, medicine, "
            "blood pressure, temperature, headache and walking. "
            "Preserve the spoken meaning accurately."
        )
    )

    return transcription.text, "Hindi"


def show_facts(title, facts):
    st.markdown(f"**{title}**")
    if not facts:
        st.caption("Not mentioned")
    for fact in facts:
        st.write("•",fact.value)
        st.caption("Evidence: “"+fact.evidence+"”")

st.title("🩺 TheCarePal — Daily Care Notes to Family Report")
st.caption("Turn nurse notes into evidence-linked daily updates. Synthetic demo only — not for clinical decision-making.")
with st.sidebar:
    st.header("About this demo")
    st.write("Languages: English, Hindi and Hinglish")
    st.write("AI extraction: Groq (GPT-OSS 20B)")
    st.write("Audio transcription: Faster-Whisper (optional)")
    st.info("Every extracted item is checked against an exact quote from the original note. Unsupported items are discarded.")

tab1,tab2=st.tabs(["✍️ Text note","🎙️ Voice note"])
note=""
with tab1:
    note=st.text_area("Paste the nurse's daily note",height=180,placeholder="Example: Aaj dadi ne breakfast poora kiya...")
with tab2:
    audio_file = st.file_uploader(
    "Upload voice note",
    type=["mp3", "wav", "m4a"],
    key="audio_uploader"
)

if audio_file is not None:

    # Check whether a new audio file has been uploaded
    if st.session_state.get("last_audio_name") != audio_file.name:

        st.session_state["last_audio_name"] = audio_file.name
        st.session_state["transcribed_text"] = ""

    if st.button("Transcribe Audio", key="transcribe_button"):

        with st.spinner("Transcribing audio..."):
            text, language = transcribe(audio_file)

            st.session_state["transcribed_text"] = text
            st.session_state["detected_language"] = language

# Display the latest transcription
if st.session_state.get("transcribed_text"):
    st.text_area(
        "Transcribed Text",
        value=st.session_state["transcribed_text"],
        key="transcription_display"
    )


# Use the typed note when provided; otherwise use the latest voice transcription.
# This is the missing link that caused the warning in the screenshot.
note = note.strip() or st.session_state.get("transcribed_text", "").strip()

if st.button("Generate daily report",type="primary",use_container_width=True):
    if not note:
        st.warning("Please enter or transcribe a nurse note first.")
    else:
        try:
            with st.spinner("Extracting facts and checking evidence..."):
                report,rejected=extract(note)
            st.session_state["last_report"]=report.model_dump()
            st.session_state["last_source"]=note
            st.session_state["last_rejected"]=rejected
        except Exception as e:
            st.error(f"Could not generate report: {e}")

if st.session_state.get("last_report"):
    r=CareReport.model_validate(st.session_state["last_report"])
    st.divider()
    st.subheader("Daily care report")
    cols=st.columns(2)
    cats=[("Vitals",r.vitals),("Meals",r.meals),("Medicines",r.medicines),
          ("Activities",r.activities),("Mood",r.mood)]
    for i,(name,facts) in enumerate(cats):
        with cols[i%2]: show_facts(name,facts)
    st.subheader("⚠️ Concerns requiring attention")
    if r.concerns:
        for f in r.concerns:
            st.warning(f.value)
            st.caption("Evidence: “"+f.evidence+"”")
        st.caption("These are observations from the note, not medical diagnoses.")
    else: st.success("No concerns were explicitly documented in the note.")
    st.subheader("Family summary")
    summary=family_summary(r)
    st.write(summary)
    payload={"source_note":st.session_state["last_source"],"report":r.model_dump(),
             "family_summary":summary,"rejected_unsupported_items":st.session_state["last_rejected"]}
    st.download_button("Download report (JSON)",json.dumps(payload,ensure_ascii=False,indent=2),
                       file_name="daily_care_report.json",mime="application/json")
    