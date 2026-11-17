<p align="center">
  <img src="https://img.shields.io/badge/SmartHire-AI%20Recruitment-6366F1?style=for-the-badge&logo=briefcase&logoColor=white" alt="SmartHire" />
</p>

<h1 align="center">🧠 SmartHire — AI-Powered Recruitment Management System</h1>

<p align="center">
  <strong>A full-stack, production-grade Applicant Tracking System with AI-based resume matching, candidate ranking, and intelligent interview scheduling.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Django-4.2-092E20?style=flat-square&logo=django&logoColor=white" />
  <img src="https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react&logoColor=black" />
  <img src="https://img.shields.io/badge/Tailwind%20CSS-3.4-06B6D4?style=flat-square&logo=tailwindcss&logoColor=white" />
  <img src="https://img.shields.io/badge/REST%20API-DRF-ff1709?style=flat-square&logo=django&logoColor=white" />
  <img src="https://img.shields.io/badge/JWT-Auth-000000?style=flat-square&logo=jsonwebtokens&logoColor=white" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" />
</p>

---

## 📋 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Architecture](#-architecture)
- [Quick Start](#-quick-start)
- [API Documentation](#-api-documentation)
- [Screenshots](#-screenshots)
- [Project Structure](#-project-structure)
- [Contributing](#-contributing)
- [License](#-license)

---

## ✨ Features

| Category | Features |
|----------|----------|
| **Authentication** | Email-based JWT auth, Role-based access (Admin/Recruiter/Candidate), Secure password management |
| **Job Management** | CRUD job postings, Department management, Status tracking, Advanced filtering & search |
| **Candidate Pipeline** | CV upload (PDF), Automated resume parsing, Skill extraction, Application tracking |
| **AI Engine** | Keyword-based skill matching, Candidate ranking algorithm, Match score calculation |
| **Interview Management** | Schedule interviews, Multiple interview types (Phone/Video/In-Person/Technical), Feedback & rating |
| **Dashboard** | Real-time application statistics, Jobs overview, Upcoming interviews, Hiring request tracking |
| **Reports** | Application trends, Status distribution charts, Hire rate analytics |
| **Notifications** | In-app notifications, Unread count, Mark as read |

---

## 🛠 Tech Stack

### Backend (`smarthire-api/`)
| Technology | Purpose |
|-----------|---------|
| **Python 3.10+** | Core language |
| **Django 4.2** | Web framework |
| **Django REST Framework** | API layer |
| **SimpleJWT** | JWT authentication |
| **django-filter** | Advanced filtering |
| **django-cors-headers** | CORS handling |
| **PyPDF2** | Resume PDF parsing |
| **Celery + Redis** | Background task processing |
| **PostgreSQL / SQLite** | Database |
| **WhiteNoise** | Static file serving |

### Frontend (`smarthire-client/`)
| Technology | Purpose |
|-----------|---------|
| **React 18** | UI framework |
| **Vite** | Build tool |
| **Tailwind CSS 3.4** | Utility-first styling |
| **React Router v6** | Client-side routing |
| **Axios** | HTTP client |
| **Lucide React** | Icon library |
| **Recharts** | Data visualization |
| **React Dropzone** | File upload |
| **React Hot Toast** | Notifications |

---

## 🏗 Architecture

```
┌──────────────────────────────────────────────────────────┐
│                     SmartHire Platform                     │
├─────────────────────────┬────────────────────────────────┤
│      Frontend (React)   │        Backend (Django)         │
│   ┌─────────────────┐   │   ┌────────────────────────┐   │
│   │  Dashboard UI   │   │   │  REST API (DRF)        │   │
│   │  Job Listings   │◄──┼──►│  JWT Authentication    │   │
│   │  Applications   │   │   │  Resume Parser (NLP)   │   │
│   │  Interviews     │   │   │  AI Matching Engine    │   │
│   │  Reports        │   │   │  Candidate Ranker      │   │
│   └─────────────────┘   │   │  Celery Tasks          │   │
│   Port: 5173            │   └────────────────────────┘   │
│                         │   Port: 8000                    │
└─────────────────────────┴────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │  PostgreSQL/SQLite │
                    │  Redis (Queue)     │
                    └───────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- npm

### 1. Clone the repository
```bash
git clone https://github.com/aminur167/smarthire-recruitment-system.git
cd smarthire-recruitment-system
```

### 2. Backend Setup
```bash
cd smarthire-api
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py seed_data     # Load demo data
python manage.py runserver
```

### 3. Frontend Setup
```bash
cd smarthire-client
npm install
npm run dev
```

### 4. Access the Application
- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000/api/v1/
- **Admin Panel:** http://localhost:8000/admin/

### Demo Credentials
| Role | Email | Password |
|------|-------|----------|
| Admin | admin@smarthire.com | admin123 |
| Recruiter | recruiter@smarthire.com | recruiter123 |
| Candidate | aminur.rahman@example.com | candidate123 |

---

## 📡 API Documentation

| Endpoint | Method | Description | Auth |
|----------|--------|-------------|------|
| `/api/v1/auth/token/` | POST | Login (get JWT) | Public |
| `/api/v1/auth/token/refresh/` | POST | Refresh token | Public |
| `/api/v1/accounts/register/` | POST | Register user | Public |
| `/api/v1/accounts/profile/` | GET/PUT | User profile | ✅ |
| `/api/v1/jobs/postings/` | GET/POST | Job listings | ✅ |
| `/api/v1/jobs/departments/` | GET/POST | Departments | ✅ |
| `/api/v1/candidates/applications/` | GET/POST | Applications | ✅ |
| `/api/v1/candidates/upload-resume/` | POST | Upload & parse CV | ✅ |
| `/api/v1/interviews/` | GET/POST | Interviews | ✅ |
| `/api/v1/dashboard/stats/` | GET | Dashboard stats | ✅ |
| `/api/v1/notifications/` | GET | Notifications | ✅ |

---

## 📁 Project Structure

```
smarthire-recruitment-system/
├── smarthire-api/              # Django Backend
│   ├── accounts/               # User auth & profiles
│   ├── jobs/                   # Job postings & departments
│   ├── candidates/             # Applications & resume parsing
│   ├── interviews/             # Interview scheduling
│   ├── dashboard/              # Analytics endpoints
│   ├── ai_engine/              # AI matching & ranking
│   ├── notifications/          # In-app notifications
│   ├── tasks/                  # Celery background tasks
│   └── smarthire/              # Django project config
│
├── smarthire-client/           # React Frontend
│   ├── src/
│   │   ├── api/                # Axios API layer
│   │   ├── components/         # Reusable UI components
│   │   ├── pages/              # Route pages
│   │   ├── context/            # Auth context
│   │   ├── hooks/              # Custom React hooks
│   │   └── utils/              # Helpers & constants
│   └── public/                 # Static assets
│
└── README.md                   # This file
```

---

## 👨‍💻 Author

**Aminur Rahman** — [@aminur167](https://github.com/aminur167)

---

## 📄 License

This project is licensed under the MIT License.

---

<p align="center">
  <strong>⭐ Star this repo if you found it useful!</strong>
</p>
