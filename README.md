# Box Selection System

A Django application that helps warehouse staff choose a suitable shipping box for an ecommerce order. It considers product dimensions, weight, box capacity and cost, then lists the boxes that meet its selection rules from cheapest to most expensive.

## Overview

When an order is ready to ship, the warehouse needs to choose a box that can accommodate the products without exceeding its weight limit. This project provides a simple interface for managing products, boxes and orders, along with a recommendation page for comparing suitable boxes.

The application is built with Django and SQLite and can be run locally without external services or API keys.

## Features

- **Product management:** Add, view, edit and delete products, including their SKU, dimensions and weight.
- **Box management:** Maintain box dimensions, maximum weight capacity and cost.
- **Order management:** Create orders with multiple products and quantities, and view order details and total weight.
- **Box recommendations:** Compare eligible boxes and display the cheapest option first.
- **Validation:** Check dimensions, weights and quantities, with helpful feedback for invalid input.
- **Failure explanations:** Show why a box does not meet the selection criteria.
- **Django admin:** Manage application data through Django's built-in admin interface.
- **Automated tests:** Test the recommendation logic and important application behaviour.

## Technology

- Python 3.11 or later
- Django 5.2
- SQLite
- Django ORM, forms and templates
- HTML and CSS
- Django's built-in testing framework

Dependencies are listed in `requirements.txt`.

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/Vaibhav5941/box_selection_system_submission.git
cd box_selection_system_submission
```

### 2. Create a virtual environment

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

On macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Apply database migrations

```bash
python manage.py migrate
```

### 5. Start the development server

```bash
python manage.py runserver
```

Open http://127.0.0.1:8000/ in your browser.

### 6. Open the Django admin (optional)

Create an administrator account:

```bash
python manage.py createsuperuser
```

Then visit http://127.0.0.1:8000/admin/.

## Running Tests

Run the complete test suite with:

```bash
python manage.py test
```

For more detailed output:

```bash
python manage.py test -v 2
```

Run Django's configuration check with:

```bash
python manage.py check
```

See `TEST_OUTPUT.md` for the recorded test results. Test counts and results should reflect the latest actual run.

## How the Application Works

1. Add products and enter their dimensions and weight.
2. Add shipping boxes with their internal dimensions, weight limits and costs.
3. Create an order and select its products and quantities.
4. Open the recommendation results for that order.
5. Compare eligible boxes and use the lowest-cost option as the primary recommendation.

Dimensions are measured in centimetres and weights in kilograms. Box costs are stored as decimal values.

## Recommendation Logic

The selection logic is implemented in `warehouse/services/box_recommendation.py`.

For each box, the application checks the following:

1. **Dimensions:** Each product must fit within the box when considered individually. The algorithm checks all six permutations of the product's length, width and height, allowing the product to be rotated.
2. **Weight:** The combined weight of the products, including their quantities, must not exceed the box's maximum weight capacity.
3. **Volume:** The total volume of the ordered items must not exceed the box's internal volume.

Boxes that pass the implemented checks are listed by increasing cost. If multiple boxes have the same cost, the application uses its configured tie-breaking rules.

If no box meets the criteria, the application reports that no suitable option was found instead of recommending a box that failed the checks.

### An important limitation

This is a simplified selection algorithm, not a complete three-dimensional packing solver.

Checking each product individually does not prove that all products can fit together in the same box. The combined-volume check can rule out some impossible choices, but it cannot guarantee a valid arrangement of the remaining products.

For example, two cubes measuring 6 × 6 × 6 cannot both fit inside a 10 × 10 × 6 box, even though each cube fits individually and their combined volume is less than the box's volume.

The recommendation should therefore be treated as a shortlist of possible boxes. A production warehouse system would need a proper packing algorithm to verify the arrangement of all items.

## Project Structure

```text
box_selection_system/
├── manage.py
├── requirements.txt
├── README.md
├── AI_USAGE.md
├── TEST_OUTPUT.md
├── .gitignore
├── config/
└── warehouse/
    ├── models.py
    ├── validators.py
    ├── forms.py
    ├── views.py
    ├── urls.py
    ├── admin.py
    ├── services/
    │   └── box_recommendation.py
    ├── migrations/
    ├── templates/
    ├── static/
    └── tests/
```

The `config` directory contains the Django project configuration. The `warehouse` app contains the data models, forms, views, recommendation logic, templates and tests.

## Validation and Security

The application uses Django forms and model validation to help prevent invalid data from entering the system. Database constraints should also be used for important rules where supported by the current models.

CSRF protection and Django's template escaping provide standard protections for form submissions and rendered content.

The default configuration is intended for local development, not direct production deployment. Before deployment:

- Set `DEBUG` to `False`.
- Configure a secure, private `SECRET_KEY`.
- Set `ALLOWED_HOSTS` to the appropriate hostnames.
- Configure HTTPS, secure cookies and other production security settings.
- Use a suitable production server and configure static file serving.
- Choose and configure an appropriate production database.

Review `config/settings.py` for the settings supported by this project.

## Current Limitations

- The recommendation logic does not solve complete 3D packing.
- Only rotations represented by the six axis-aligned dimension permutations are considered.
- Product dimensions are expected in centimetres and weights in kilograms.
- Packaging material, padding, fragility and stacking restrictions are not modelled.
- The application does not calculate dimensional shipping weight.
- Authentication and per-user permissions for the warehouse interface are not implemented unless added separately.

## Possible Improvements

Some useful next steps would be to implement and test a proper 3D packing algorithm, support splitting an order across multiple boxes, add search and filtering, and introduce authentication and role-based permissions.

## AI Usage

This project was developed with assistance from AI tools. The tools used, prompts, changes made, mistakes identified and verification steps should be documented in `AI_USAGE.md` based on the actual development process.

