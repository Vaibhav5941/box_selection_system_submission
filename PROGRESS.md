# Progress / Checkpoint

Status: **complete and verified** (build date 2026-10-24).

## Completed

- [x] Django 5.2 project (`config/`) + `warehouse` app, SQLite, migrations committed
- [x] Models: Product, Box, Order, OrderItem (field validators + DB `CheckConstraint`s + unique constraints)
- [x] Recommendation engine: `warehouse/services/box_recommendation.py` (pure Python, Decimal arithmetic)
- [x] Forms/formset (duplicate-product check, quantity >= 1), class-based CRUD views, order creation, recommendation page
- [x] Templates + CSS (dashboard, products, boxes, orders, recommendation results, messages, empty states)
- [x] 112 tests (service / models / forms / views): all pass
- [x] README, AI_USAGE template, TEST_OUTPUT (real output), SUBMISSION guide, reflection checklist, .gitignore, requirements.txt
- [x] Submission ZIP built and verified (see handoff for path)

## Key design decisions

1. **Service is Django-free.** Models convert themselves to `ItemSpec` / `BoxSpec` dataclasses, so the engine is tested with `SimpleTestCase` and no database.
2. **Eligibility = per-item fit (6 rotations) + total weight + total volume.** The volume check is an *additional necessary condition* (provably correct: items cannot occupy more space than the box has). It is not sufficient, so the limitation is documented in the module docstring, README, a test, and a disclaimer on every results page.
3. **Decimal everywhere** (no floats) so boundary cases such as 3 x 0.1 kg == 0.3 kg are exact.
4. **Validation in layers:** field validators (forms/`full_clean`), `CheckConstraint`s (direct ORM writes), and service-level validation (bad input raises `RecommendationInputError`).
5. **Order items:** same product cannot appear twice per order; products on orders are `PROTECT`ed from deletion.
6. **No hardcoded secret:** `SECRET_KEY` from env; random throw-away key in DEBUG; production refuses to start without one.
7. Tie-break for equal-cost boxes: smaller internal volume, then name, then id (deterministic).

## Issues found and fixed during the build

Four initial test failures (one wrong test expectation, one real UX issue with `min="0"` on quantity, and two for the generic duplicate-product message). Details in `TEST_OUTPUT.md`.

## Not done / for the user

- Fill in `AI_USAGE.md` honestly; write your own reflection from `LEARNING_REFLECTION_CHECKLIST.md`.
- Export the real chat transcript yourself (`SUBMISSION.md`).
- Push to GitHub yourself (commands in `SUBMISSION.md`). Nothing has been uploaded.
- Re-run `python manage.py test` on your machine.

## Next steps if extending

Real 3D packing; multi-box (split) shipments; unit conversion. See README "Future improvements".
