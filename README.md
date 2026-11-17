<div align="center">

# 🚀 SmartHire API — Enterprise AI-Powered Recruitment Management Platform

**High-performance RESTful API powering the SmartHire Applicant Tracking System (ATS), featuring NLP resume parsing, AI candidate ranking, asynchronous task queues, and role-based permissions.**

[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Django](https://img.shields.io/badge/Django-4.2-092E20?style=for-the-badge&logo=django&logoColor=white)](https://djangoproject.com)
[![DRF](https://img.shields.io/badge/Django_REST-Framework-red?style=for-the-badge&logo=django)](https://django-rest-framework.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgresql.org)
[![Redis](https://img.shields.io/badge/Redis-Cache%20%26%20Broker-DC382D?style=for-the-badge&logo=redis&logoColor=white)](https://redis.io)
[![Celery](https://img.shields.io/badge/Celery-Distributed%20Tasks-37814A?style=for-the-badge&logo=celery&logoColor=white)](https://docs.celeryq.dev)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

</div>

---

## 📌 Executive Overview

**SmartHire API** is a production-grade backend engine designed to streamline modern recruitment lifecycles. Built with **Django 4.2** and **Django REST Framework (DRF)**, it automates end-to-end talent acquisition workflows: from resume ingestion, semantic text extraction, and algorithmic skill matching to interview scheduling and hiring analytics telemetry.

---

## 🏗️ System Architecture

```mermaid
graph TD
    Client[React Web Client / ATS Dashboard] -->|JWT HTTPS Requests| Nginx[Reverse Proxy / SSL]
    Nginx -->|WSGI Proxy| Django[SmartHire Django REST API]
    
    subgraph Core Platform
        Django --> Auth[Accounts & RBAC Module]
        Django --> Jobs[Jobs & Department Engine]
        Django --> Candidates[Candidates & Resume Pipeline]
        Django --> Interviews[Interview Scheduler]
        Django --> Dashboard[Analytics & Reporting API]
    end

    subgraph Data & Storage
        Django -->|ORM Queries| Postgres[(PostgreSQL / SQLite Database)]
        Django -->|Media Storage| Storage[Media Files / Uploaded CVs & Avatars]
    end

    subgraph Asynchronous & AI Worker Tier
        Django -->|Dispatch Async Job| Redis[(Redis Broker & Cache)]
        Redis --> Celery[Celery Background Workers]
        Celery --> AIEngine[AI Resume Parser & Skill Matcher]
        AIEngine -->|Update Match Score| Postgres
    end
```

---

## ✨ Key Capabilities

### 🔐 1. Role-Based Access Control (RBAC) & Multi-Tenant Security
- **JWT Authentication:** Stateful token issuance with automatic rotation and cryptographic refresh via `SimpleJWT`.
- **Role Isolation:** Strict permissions separating **Admin**, **Recruiter**, and **Candidate** domains.
- **Enterprise Profile Suite:** Native support for profile avatars, contact credentials, bio, and password updates with `MultiPartParser`.

### 🧠 2. AI Resume Parsing & Candidate Scoring Engine
- **Automated CV Ingestion:** Extracts structured metadata (emails, phone numbers, education, skills) from PDF resumes via `PyPDF2` and custom NLP regex patterns.
- **Algorithmic Fit Scoring:** Compares applicant skill vectors against job requirements to generate a real-time `match_score` (0–100%).
- **Automated Pipeline Staging:** Automatically triages candidates into `applied`, `screening`, `interview`, `offer`, or `rejected`.

### ⚡ 3. Asynchronous Task Processing & Queue Management
- **Celery & Redis:** Offloads heavy PDF parsing, email reminders, and AI ranking from the main request-response cycle.
- **Scheduled Beat Cron:** Automated triggers for upcoming interview notifications and expired job postings.

### 📊 4. Telemetry & Analytics Dashboard
- Aggregates live hiring velocity, department vacancy quotas, interview throughput, and application status conversion funnels in sub-millisecond queries.

---

## 📁 Repository Structure

```
smarthire-api/
├── accounts/               # Custom User model, avatars, auth views & seed data
├── jobs/                   # Job postings, department models, filters & viewsets
├── candidates/             # Candidate profiles, applications & PDF resume parser
├── interviews/             # Interview scheduling, status tracking & meet links
├── dashboard/              # Aggregate telemetry, conversion counters & metrics
├── notifications/          # In-app alerts, read tracking & user notifications
├── ai_engine/              # NLP resume parser & candidate ranking algorithms
├── tasks/                  # Celery asynchronous worker tasks
├── smarthire/              # Root settings, celery app, wsgi/asgi & urls
├── requirements.txt        # Frozen production dependencies
├── manage.py               # Django CLI management utility
├── .env.example            # Environment variables template
├── LICENSE                 # Open-source MIT License
└── README.md               # Repository documentation
```

---

## 🔗 REST API Reference

### Authentication & Accounts
| Method | Endpoint | Description | Auth Required |
|:---|:---|:---|:---|
| `POST` | `/api/v1/auth/token/` | Obtain JWT access and refresh token pair | Public |
| `POST` | `/api/v1/auth/token/refresh/` | Refresh expired access token | Public |
| `POST` | `/api/v1/accounts/register/` | Register new user account (Candidate/Recruiter) | Public |
| `GET` | `/api/v1/accounts/profile/` | Fetch authenticated user profile details | Bearer JWT |
| `PATCH`| `/api/v1/accounts/profile/` | Update profile, bio, phone & avatar photo | Bearer JWT |
| `PUT` | `/api/v1/accounts/change-password/` | Change account password | Bearer JWT |

### Jobs & Departments
| Method | Endpoint | Description | Auth Required |
|:---|:---|:---|:---|
| `GET` | `/api/v1/jobs/postings/` | Filterable list of active job vacancies | Bearer JWT |
| `POST` | `/api/v1/jobs/postings/` | Create a new job vacancy | Recruiter/Admin |
| `GET` | `/api/v1/jobs/postings/{id}/` | Retrieve complete job specifications & requirements | Bearer JWT |
| `GET` | `/api/v1/jobs/departments/` | Department overview with headcount counters | Bearer JWT |

### Candidates & Applications
| Method | Endpoint | Description | Auth Required |
|:---|:---|:---|:---|
| `GET` | `/api/v1/candidates/applications/` | List applications with AI match score & status | Recruiter/Admin |
| `POST` | `/api/v1/candidates/applications/` | Submit application for an open vacancy | Candidate |
| `POST` | `/api/v1/candidates/upload-resume/` | Upload PDF CV & trigger async parsing | Candidate |
| `PATCH`| `/api/v1/candidates/applications/{id}/` | Update application stage (screening/interview/offer) | Recruiter/Admin |

### Interviews & Dashboard Telemetry
| Method | Endpoint | Description | Auth Required |
|:---|:---|:---|:---|
| `GET` | `/api/v1/interviews/` | List scheduled interviews | Bearer JWT |
| `POST` | `/api/v1/interviews/` | Schedule new interview round with meeting link | Recruiter/Admin |
| `GET` | `/api/v1/interviews/upcoming/` | Fetch upcoming agenda for today and tomorrow | Bearer JWT |
| `GET` | `/api/v1/dashboard/stats/` | Overview metrics (applicants, active jobs, interviews) | Bearer JWT |
| `GET` | `/api/v1/dashboard/jobs-overview/` | Tabular hiring funnel distribution | Bearer JWT |

---

## ⚙️ Local Development Setup

### 1. Prerequisites
- Python 3.10+
- PostgreSQL or SQLite
- Redis (optional for async tasks, fallback configured)

### 2. Clone & Environment Setup
```bash
git clone https://github.com/aminur167/smarthire-api.git
cd smarthire-api

# Create & activate virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
```bash
cp .env.example .env
```
Key configuration settings:
```ini
DEBUG=True
SECRET_KEY=your-django-super-secret-key
DATABASE_URL=sqlite:///db.sqlite3
# or PostgreSQL: postgres://user:password@localhost:5432/smarthire_db
REDIS_URL=redis://localhost:6379/0
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

### 5. Apply Migrations & Seed Sample Data
```bash
python manage.py migrate
python manage.py seed_data
```
*Creates initial departments, 10 sample job postings, 15 candidates, and demo accounts:*
- **Admin:** `admin@smarthire.com` / `admin123`
- **Recruiter:** `recruiter@smarthire.com` / `recruiter123`
- **Candidate:** `aminur.rahman@example.com` / `candidate123`

### 6. Run Server
```bash
python manage.py runserver 8000
```
Server live at `http://127.0.0.1:8000/`.

---

## 🧪 Testing Suite
Execute the Django test runner:
```bash
python manage.py test --verbosity=2
```

---

## 📄 License
This project is open-source and licensed under the [MIT License](LICENSE).

---

<div align="center">
Made with ❤️ by <a href="https://github.com/aminur167">Aminur Rahman</a>
</div>
