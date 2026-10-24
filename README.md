# AI-Assisted Box Selection System

A small Django warehouse application that recommends the cheapest suitable shipping box for an order, based on product dimensions and weight, box internal dimensions, box weight capacity, and box cost.

> **Important limitation:** the recommendation is a *simplified selection*, not a 3D packing solver. It checks that each product fits the box on its own (with rotation), then checks total weight and total volume. It **cannot guarantee** that several products physically fit together in the same box. See [Assumptions and limitations](#assumptions-and-limitations).

## Features

- **Products**: create, list, view, update, delete (name, SKU, length, width, height, weight).
- **Shipping boxes**: create, list, view, update, delete (name, internal dimensions, max weight, cost).
- **Orders**: create an order with one or more products and quantities; order detail page lists products, quantities and total weight; delete orders.
- **Box recommendation**: dedicated results page showing the cheapest eligible box, all eligible boxes cheapest-first, and, for every box ruled out, the exact reasons (dimensions / weight / volume).
- **Clear feedback**: success and error messages, empty states, field-level validation errors, 404 pages for missing objects.
- **Safe deletes**: a product that appears on an order cannot be deleted (shows a message instead of crashing).
- **Django admin** for data entry as an alternative to the UI.
- **112 automated tests** (service, models, forms, views).

## Technology stack

- Python 3.11+ (developed and tested on 3.13)
- Django 5.2 (LTS)
- SQLite, Django ORM and migrations
- Django templates, forms, formsets and plain CSS (no JavaScript, no external services, no API keys)
- Django's built-in test framework

## Requirements

- Python 3.11 or newer
- `pip`
- Dependencies: only Django (see `requirements.txt`)

## Installation

```bash
# 1. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate          # Windows PowerShell: .venv\Scripts\Activate.ps1

# 2. Install dependencies
pip install -r requirements.txt
```

## Migrations

```bash
python manage.py migrate
```

This creates `db.sqlite3` (ignored by Git). Migrations are already committed in `warehouse/migrations/`; run `python manage.py makemigrations` only if you change a model.

## Create a superuser (optional, for `/admin/`)

```bash
python manage.py createsuperuser
```

## Run the application

```bash
python manage.py runserver
```

Open <http://127.0.0.1:8000/>. No environment variables are needed for local development: `DEBUG` is on by default and a random throw-away `SECRET_KEY` is generated at start-up.

## Run the tests

```bash
python manage.py test
# verbose, one line per test:
python manage.py test -v 2
```

See `TEST_OUTPUT.md` for the captured output of a real run.

## Sample workflow

1. **Add boxes** (Boxes → Add box), lengths/widths/heights are *internal* dimensions in cm:

   | Name   | L × W × H (cm) | Max weight (kg) | Cost |
   |--------|----------------|-----------------|------|
   | Small  | 20 × 15 × 10   | 5               | 1.50 |
   | Medium | 30 × 25 × 20   | 15              | 3.00 |
   | Large  | 50 × 40 × 30   | 30              | 6.50 |

2. **Add products** (Products → Add product):

   | Name            | SKU     | L × W × H (cm) | Weight (kg) |
   |-----------------|---------|----------------|-------------|
   | Ceramic Mug     | MUG-001 | 12 × 9 × 9     | 0.4         |
   | Stoneware Plate | PLT-001 | 26 × 26 × 3    | 0.75        |
   | Poster Tube     | TUB-001 | 60 × 8 × 8     | 0.5         |

3. **Create orders** (Orders → New order) and click **Recommend box**. With the data above the engine gives:

   | Order                    | Total weight | Result                                                                                   |
   |--------------------------|--------------|------------------------------------------------------------------------------------------|
   | 1 × Mug                  | 0.4 kg       | **Small** (cheapest); Medium and Large are also eligible                                 |
   | 2 × Mug + 4 × Plate      | 3.8 kg       | **Large** only. The 26 × 26 plate is wider than Medium's 25 cm side; Small is far too small |
   | 1 × Poster Tube          | 0.5 kg       | **No suitable box**: the 60 cm tube does not fit any box, and the page explains why         |

## Algorithm explanation

Implemented in `warehouse/services/box_recommendation.py` (pure Python, no Django imports, so it is unit-testable without a database). For each configured box the engine collects every reason the box fails:

1. **Per-item fit with rotation.** Each product, on its own, must fit inside the box's internal dimensions in at least one of the **six** permutations of (length, width, height). A side equal to the box side is allowed (exact fit).
2. **Weight capacity.** `sum(unit weight × quantity)` over all items must be `<=` the box's maximum weight. Exactly equal is allowed.
3. **Volume sanity check.** The combined volume of all units must be `<=` the box's internal volume. This is a *necessary* condition for any real packing, so a box that fails it can never hold the order.

A box with no failures is **eligible**. Eligible boxes are sorted by cost, cheapest first (ties: smaller internal volume, then name, then id), and the first is the **primary recommendation**. If nothing is eligible, the result has no recommended box and a message plus per-box reasons; the engine never falls back to an invalid box.

Input safety: invalid dimensions/weights (zero, negative, missing, non-numeric, NaN/infinity), invalid quantities (zero, negative, fractional, non-integer, booleans), unnamed products, empty orders and missing entries raise `RecommendationInputError` with a clear message (the UI shows it). No configured boxes returns a dedicated `NO_BOXES` result. All arithmetic uses `Decimal`, so e.g. 3 × 0.1 kg equals exactly 0.3 kg against a 0.3 kg capacity.

## Assumptions and limitations

- **Not full 3D packing.** Checks 1-3 are necessary, not sufficient. Example: two 6 × 6 × 6 cubes pass every check for a 10 × 10 × 6 box (each fits; 432 ≤ 600 by volume) but cannot actually be packed together, since two cubes need 12 units along some axis. This case is documented in a test (`test_known_limitation_passing_checks_is_not_a_packing_guarantee`) and the results page always displays a disclaimer. Treat results for multi-unit orders as a shortlist to confirm physically or with a real packing algorithm.
- Only axis-aligned (90°) rotations are considered.
- One unit system: dimensions in **cm**, weights in **kg**. No conversion is performed. Cost is a plain amount with no currency symbol.
- Box dimensions must be **internal** (usable) dimensions; padding and packing material are not modelled.
- Fragility, stacking rules, dimensional weight, and shipping carrier limits are not modelled.
- An order cannot list the same product twice (combine into one line); a product on an order cannot be deleted.
- There is no authentication: the app is intended for local use. The Django admin is protected by Django's standard login.

## Project structure

```
box_selection_system/
├── manage.py
├── requirements.txt
├── README.md                    # this file
├── AI_USAGE.md                  # template for YOU to fill in honestly
├── TEST_OUTPUT.md               # real captured test output
├── PROGRESS.md                  # build checkpoint / design decisions
├── SUBMISSION.md                # git commands, ZIP commands, transcript export
├── LEARNING_REFLECTION_CHECKLIST.md
├── .gitignore
├── config/                      # Django project (settings, root URLs, wsgi/asgi)
└── warehouse/                   # the app
    ├── models.py                # Product, Box, Order, OrderItem (+ DB constraints)
    ├── validators.py            # positive / non-negative validators
    ├── forms.py                 # ModelForms + order-item formset
    ├── views.py                 # class-based CRUD views + order creation
    ├── urls.py
    ├── admin.py
    ├── services/
    │   └── box_recommendation.py   # the recommendation engine (pure Python)
    ├── migrations/
    ├── templates/warehouse/     # base, dashboard, CRUD pages, recommendation page
    ├── static/warehouse/style.css
    └── tests/
        ├── helpers.py           # test data factories
        ├── test_service.py      # engine unit tests (no database)
        ├── test_models.py       # validation, constraints, order totals
        ├── test_forms.py        # form and formset validation
        └── test_views.py        # HTTP responses, messages, 404s, CSRF
```

## Security notes

Development defaults are deliberately convenient; production must set environment variables (see `config/settings.py`):

| Variable | Purpose |
|----------|---------|
| `DJANGO_DEBUG` | Set to `0` in production (default is on for local development). |
| `DJANGO_SECRET_KEY` | **Required** when `DJANGO_DEBUG=0`; the app refuses to start without it. Generate with `python -c "from django.core.management.utils import get_random_secret_key as g; print(g())"`. Never commit it. |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated hostnames, e.g. `example.com,www.example.com`. |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | Comma-separated origins such as `https://example.com` when behind a proxy. |
| `DJANGO_SECURE_SSL_REDIRECT` | Defaults to on when not in debug; set to `0` only if TLS is terminated elsewhere and redirected there. |
| `DJANGO_HSTS_SECONDS` / `DJANGO_HSTS_INCLUDE_SUBDOMAINS` | HSTS controls; default 3600 s, raise once HTTPS is confirmed working. |

When `DJANGO_DEBUG=0` the settings also enable secure session and CSRF cookies and content-type nosniff. Always-on protections: CSRF tokens on every form (tested), template auto-escaping, ORM parameterised queries, clickjacking middleware, and DB `CHECK` constraints so invalid rows cannot be stored even if form validation is bypassed.

`python manage.py check --deploy` with production-style variables reports only two optional HSTS warnings (`SECURE_HSTS_INCLUDE_SUBDOMAINS`, `SECURE_HSTS_PRELOAD`) that must be enabled deliberately. A production deployment would also need a real WSGI server, `collectstatic` plus static file serving, and a production-grade database; those are out of scope here.

## Future improvements

- Real 3D bin packing (e.g. extreme-point or skyline heuristics) with tests against known-solvable and known-impossible cases.
- Support for several boxes per order (split shipments) when no single box suffices.
- Unit selection and conversion (cm/in, kg/lb) and a currency setting.
- Box padding allowance and product fragility/orientation constraints ("this side up").
- Authentication and per-user permissions; REST API; search, filtering and CSV import for products.
#   b o x _ s e l e c t i o n _ s y s t e m _ s u b m i s s i o n  
 