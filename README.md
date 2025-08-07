# 🪙 Personal Finance Tracker API

A full-featured Django + DRF back-end for tracking expenses, income, savings goals and recurring transactions.

[![CI](https://img.shields.io/github/actions/workflow/status/<your-org>/<repo>/ci.yml?label=tests)](./actions)
[![Coverage](https://img.shields.io/badge/coverage-90%25-brightgreen)](./htmlcov)
[![License](https://img.shields.io/github/license/<your-org>/<repo>)](/LICENSE)

---

##  Features

| Module | What you get |
|--------|--------------|
| **Accounts** | JWT auth, per-user data isolation |
| **Transactions** | CRUD, pagination, filter + search + ordering |
| **Categories** | Per-user unique names, CRUD |
| **Savings Goals** | Progress calculation, name filter |
| **Recurring Transactions** | RFC-5545 RRULE engine + “post due” endpoint |
| **Summary** | Income/expense totals + per-category + goal progress |
| **API Docs** | Swagger (`/api/docs/`) & ReDoc (`/api/redoc/`) |
| **Quality Gate** | *black*, *flake8*, *pytest* (cov ≥ 80 %) via **pre-commit** |

---

##  Quick-start (local)

> **Prereqs** Python 3.9+ & PostgreSQL 14+.  
> Use a **virtual env**.

```bash
git clone https://github.com/<your-org>/<repo>.git
cd finance-tracker

python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -r dev-requirements.txt

cp .env.example .env            # add DB creds, SECRET_KEY …
python manage.py migrate
python manage.py runserver
Browse → http://127.0.0.1:8000/api/docs/

Tests & coverage
bash
Copy code
pytest                   # full suite (coverage enforced ≥ 80 %)
pytest -q                # quiet
pytest --cov --cov-report=html && open htmlcov/index.html
Code-style & pre-commit
bash
Copy code
pre-commit install           # one-time
git add … && git commit      # hooks auto-run

# or on demand
pre-commit run --all-files
Hooks: black · flake8 · pytest + coverage

Deployment on Render
File	Purpose
render.yaml	Build + web-service definition
build.sh	CI (lint → tests)
start.sh	migrate → collectstatic → gunicorn

Render → Environment Vars

Key	Example
DJANGO_SETTINGS_MODULE	core.settings
SECRET_KEY	p6BsW…
DATABASE_URL	postgresql://user:pass@host/db
DEBUG	False

Optional daily job to post due recurring transactions
yaml
Copy code
jobs:
  - name: post-recurring
    schedule: "daily"                 # free tier → 1× / day
    command: python manage.py post_recurring

API reference (key routes)
Method & path	Description
POST /api/auth/login/	obtain JWT
POST /api/auth/refresh/	refresh JWT
GET /api/finance/categories/	list ↔️ CRUD
GET /api/finance/transactions/?ordering=-amount	filters/search/ordering
GET /api/finance/summary/	aggregated overview
POST /api/finance/post-recurring/	materialise due recurring tx
Docs	/api/docs/ (Swagger) · /api/redoc/ (ReDoc)
Schema	/api/schema/ (OpenAPI 3 JSON)

Health-check
bash
Copy code
GET /healthz/   →   {"ok": true}
Used by Render for zero-downtime deploys.

Security
Please disclose vulnerabilities responsibly via security@your-org.com.
See SECURITY.md for details.

License
MIT – see LICENSE.
