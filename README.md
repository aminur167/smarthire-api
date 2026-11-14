# SmartHire API — AI-Powered Recruitment Management System

> Production-grade Django REST API powering the SmartHire recruitment platform.

## 🚀 Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | Django 4.2 + Django REST Framework |
| Auth | JWT (SimpleJWT) |
| Database | PostgreSQL / SQLite (dev) |
| Task Queue | Celery + Redis |
| AI Engine | Custom NLP-based resume parser & skill matcher |
| Deployment | Gunicorn + WhiteNoise |

## 📁 Project Structure

```
smarthire-api/
├── smarthire/        # Project configuration
├── accounts/         # User auth, registration, profiles
├── jobs/             # Job postings & departments
├── candidates/       # Candidate profiles, applications, resume upload
├── interviews/       # Interview scheduling & feedback
├── dashboard/        # Analytics & aggregate endpoints
├── ai_engine/        # Resume matching & candidate ranking
├── notifications/    # In-app notifications
└── tasks/            # Celery background tasks
```

## ⚡ Quick Start

```bash
# 1. Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up environment
copy .env.example .env       # Windows
# cp .env.example .env       # macOS/Linux

# 4. Run migrations
python manage.py migrate

# 5. Create admin user
python manage.py createsuperuser

# 6. Seed demo data (optional)
python manage.py seed_data

# 7. Start the server
python manage.py runserver
```

## 🔗 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/auth/token/` | POST | Obtain JWT token |
| `/api/v1/auth/token/refresh/` | POST | Refresh JWT token |
| `/api/v1/accounts/register/` | POST | Register new user |
| `/api/v1/accounts/profile/` | GET/PUT | User profile |
| `/api/v1/jobs/postings/` | GET/POST | Job listings |
| `/api/v1/jobs/departments/` | GET/POST | Departments |
| `/api/v1/candidates/applications/` | GET/POST | Applications |
| `/api/v1/candidates/upload-resume/` | POST | Upload & parse CV |
| `/api/v1/interviews/` | GET/POST | Interviews |
| `/api/v1/interviews/upcoming/` | GET | Upcoming interviews |
| `/api/v1/dashboard/stats/` | GET | Dashboard statistics |
| `/api/v1/dashboard/jobs-overview/` | GET | Jobs overview |
| `/api/v1/notifications/` | GET | User notifications |

## 📄 License

MIT © SmartHire
