# 2–5 minute demo video script

**0:00–0:40 — Show the product first**
Open Streamlit. Paste a synthetic Hinglish note. Click Generate daily report. Show structured categories, concerns, evidence quotes and the family summary.

**0:40–1:20 — Demonstrate missing information**
Use a note that mentions only a meal and medicine. Point out that vitals, activities and mood remain “Not mentioned”; the system does not fill gaps.

**1:20–2:10 — Explain architecture**
Explain text/audio input, optional Faster-Whisper transcription, Gemini structured extraction, Pydantic validation and exact-substring evidence checking.

**2:10–2:50 — Explain safety and evaluation**
Show the 25-note synthetic dataset and evaluation script. Explain that exact evidence matching is a grounding check, not a complete accuracy score, and a human must review before sharing.

**2:50–3:10 — Close**
Mention future work: family language preference, weekly summaries, human approval and secure Firebase integration.
