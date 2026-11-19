# Evaluation plan and report

## Test set
25 self-authored synthetic notes: English, Hindi and Hinglish. The cases include complete and incomplete daily notes, missing fields, missed/refused medicines, fever, falls, pain, low food/fluid intake and routine activities.

## Metrics
1. **Evidence grounding rate** = accepted items with exact source quotes / (accepted items + items rejected for invalid quotes).
2. **Extraction coverage** = correctly extracted expected facts / all expected facts in a manually annotated gold set.
3. **Unsupported-content rate** = extracted items not supported by the source / all extracted items.
4. **Category accuracy** = correct field assignment / manually annotated expected facts.

The provided `evaluation.py` computes metric 1 and records processing errors. It does not pretend to calculate semantic accuracy. To complete a defensible evaluation, manually annotate the expected facts for all 25 notes, compare the model output against those annotations, and review all concern flags.

## Results table (fill after running)
| Metric | Result |
|---|---:|
| Notes attempted | 25 |
| Successful model runs | Pending actual run |
| Evidence grounding rate | Pending actual run |
| Extraction coverage | Requires manual gold annotation |
| Unsupported-content rate | Requires manual review |
| False concern flags | Requires manual review |

## Known failure modes
- Speech-to-text may mishear names, numbers, medicine names or units.
- Hindi/Hinglish spelling and code-switching can affect extraction.
- A valid exact quote can still be interpreted incorrectly; substring validation alone is not semantic verification.
- The model may omit a fact or put it in the wrong category.
- The model may over-flag a symptom as a concern. A care professional should review flags.

## Evaluation conclusion
Do not claim 100% accuracy or zero hallucinations based only on exact-quote checks. The validator reduces unsupported evidence claims, but field values, omissions, translations and concern classification still require human review.
