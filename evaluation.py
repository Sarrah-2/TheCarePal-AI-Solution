
import json, os, sys
from pathlib import Path
from app import extract

data=Path("data/synthetic_notes.jsonl")
total=0; accepted=0; rejected=0; empty=0; errors=[]
for line in data.read_text(encoding="utf-8").splitlines():
    row=json.loads(line); total+=1
    try:
        report,bad=extract(row["note"])
        note_accepted = sum(len(getattr(report,c)) for c in ["vitals","meals","medicines","activities","mood","concerns"])
        accepted += note_accepted
        rejected += len(bad)
        if note_accepted == 0: empty += 1
    except Exception as exc:
        errors.append({"id":row["id"],"error":str(exc)})
print(json.dumps({
 "notes_total":total,
 "accepted_evidence_backed_items":accepted,
 "items_rejected_for_invalid_evidence":rejected,
 "evidence_grounding_rate": round(accepted/(accepted+rejected),4) if accepted+rejected else None,
 "processing_errors":errors,
 "note":"Grounding rate measures exact-quote validity only, not semantic correctness. Review every generated value."
},ensure_ascii=False,indent=2))
