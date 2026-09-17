# EstateLedger

## About

EstateLedger is a Django-based web application designed to help manage property-related operations efficiently. It brings together user account management, property records, billing workflows, payment tracking, and audit functionality in one system.

The project is intended to support estate and property management needs such as organizing owners, tenants, payments, and operational records in a structured way.

## Tech Stack

- Python 3.12+
- Django 6.1.1
- Django REST Framework 3.18.1
- SQLite (default development database)

## Project Structure

- `accounts/` — user authentication and account management
- `audit/` — audit-related models and views
- `billing/` — billing logic
- `payments/` — payment handling
- `properties/` — property management
- `estateledger/` — Django project settings and URL configuration
- `manage.py` — Django management entry point
- `requirements.txt` — Python dependencies

## Local Setup

1. Create and activate a virtual environment.
   ```bash
   python -m venv estate
   estate\Scripts\activate
   ```
2. Install dependencies.
   ```bash
   pip install -r requirements.txt
   ```
3. Apply migrations.
   ```bash
   python manage.py migrate
   ```
4. Run the development server.
   ```bash
   python manage.py runserver
   ```

## Authentication

The app uses a serializer-based authentication flow for user login and registration under the `accounts` app.

## GitHub Push Readiness

This repository is prepared for pushing to GitHub without running any `git init` or `git push` commands here.

Recommended next steps on your machine:

1. Create a new repository on GitHub.
2. Connect this local project to the remote repository.
3. Commit and push your changes normally.

## Notes

- `db.sqlite3` is ignored by default for local development.
- The local virtual environment folder `estate/` is also ignored.
- Migrations are left tracked so the Django app can be set up consistently on a fresh clone.
