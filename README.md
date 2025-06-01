# alemeno assignment
Submission for alemeno backend assignment


# Credit Approval Backend
A fully dockerized Django REST API for credit approval, customer registration, loan management, and eligibility checks, using PostgreSQL and Celery for background data ingestion.

🚀 Features
Customer & Loan Management: Register customers, view and manage loans.

Credit Eligibility: Automated credit score calculation and eligibility checks.

Loan Creation: Create loans with EMI and slab-based interest logic.

Data Ingestion: Background ingestion of Excel data via Celery worker.

API-First: All features exposed via RESTful endpoints.

Fully Dockerized: One-command setup with Docker Compose.

Unit Tests: Comprehensive API tests included.

🗂️ Project Structure
text
.
├── approvals/           # Django app for credit logic, models, views, tasks, tests
├── core/                # Django project settings and root URLs
├── customer_data.xlsx   # Initial customer data
├── loan_data.xlsx       # Initial loan data
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md

⚙️ Quickstart
1. Clone the Repository
bash
git clone <your-repo-url>
cd <your-repo-folder>
2. Build and Start All Services
bash
docker compose up --build
This launches:

Django API server

PostgreSQL database (with persistent volume)

Redis (for Celery broker)

Celery worker

3. Apply Migrations
In a new terminal:

bash
docker compose exec web python manage.py migrate
4. Ingest Initial Data
In a new terminal, open Django shell and trigger ingestion tasks:

bash
docker compose exec web python manage.py shell
python
from approvals.tasks import ingest_customer_data, ingest_loan_data
ingest_customer_data.delay('/app/customer_data.xlsx')
ingest_loan_data.delay('/app/loan_data.xlsx')
Watch the Celery logs for completion.

🛠️ API Endpoints
Base URL: http://localhost:8000/api/

Customer Registration
POST /register/

Register a new customer.

Eligibility Check
POST /check-eligibility/

Check loan eligibility and credit score.

Loan Creation
POST /create-loan/

Request a new loan for a customer.

View Loan
GET /view-loan/<loan_id>/

Retrieve details of a specific loan.

View All Loans for Customer
GET /view-loans/<customer_id>/

Retrieve all loans for a given customer.

See the assignment PDF or API code for detailed request/response examples.

🧪 Running Tests
Run all API and logic tests:

bash
docker compose exec web python manage.py test approvals
🧩 Code Quality & Organization
Models: approvals/models.py

Serializers: approvals/serializers.py

Views (API logic): approvals/views.py

Background Tasks: approvals/tasks.py

Tests: approvals/tests.py

URLs: approvals/urls.py, included in core/urls.py

🐳 Docker Details
PostgreSQL data is persisted via a named Docker volume.

Celery worker runs in the same container as Django (web service).

No local installation required—everything runs in containers.
