# AI Usage Record

> **This is a template for you to complete in your own words.** It was generated without any knowledge of your actual AI usage history. Every `TODO` must be filled in by you, and anything that does not apply should be deleted rather than guessed. Do not submit it with TODOs or the example entry still in place.

---

## 1. AI tools actually used

| Tool / model | Version or date used | What I used it for |
|--------------|----------------------|--------------------|
| TODO | TODO | TODO |

## 2. Actual prompts

Paste the real prompts exactly as you sent them (or reference the exported transcript, see `SUBMISSION.md`).

1. TODO: prompt 1
2. TODO: prompt 2

## 3. Suggestions accepted

| Suggestion | Where in the project | Why I accepted it |
|------------|----------------------|-------------------|
| TODO | TODO | TODO |

## 4. Suggestions rejected or modified

Only list things you really rejected or changed. If you changed nothing, say so.

| Suggestion | What I did instead | Why |
|------------|--------------------|-----|
| TODO | TODO | TODO |

## 5. Mistakes identified

Mistakes in AI output that *you* noticed (wrong logic, failing tests, misleading text, etc.).

| Mistake | How I found it | How it was fixed |
|---------|----------------|------------------|
| TODO | TODO | TODO |

## 6. How I verified important behaviour

Run each check yourself and record what you actually saw.

| Behaviour | How I verified it | Result |
|-----------|-------------------|--------|
| Cheapest eligible box is recommended | TODO (e.g. ran `python manage.py test`, tried it in the browser) | TODO |
| Rotation (all six orientations) | TODO | TODO |
| Weight capacity boundary (equal vs. exceeded) | TODO | TODO |
| Quantity affects total weight | TODO | TODO |
| No eligible box → clear explanation | TODO | TODO |
| Empty order / invalid quantity handled | TODO | TODO |
| Form and model validation | TODO | TODO |
| Multi-product limitation understood | TODO (explain it in your own words) | TODO |

---

## EXAMPLE FORMAT: NOT A FACTUAL RECORD

*The entry below only shows the level of detail expected. It describes nobody's real usage; delete it before submitting.*

> **Suggestion rejected/modified (example):** The AI suggested storing weights as `FloatField`. I changed them to `DecimalField` because I tested `0.1 * 3` in a Python shell and saw `0.30000000000000004`, which could wrongly reject a box whose capacity is exactly 0.3 kg. I then wrote a test for that exact boundary.
