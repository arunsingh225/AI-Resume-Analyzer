# 🤖 AI Resume Analyzer

[![CI](https://github.com/arunsingh225/AI-Resume-Analyzer/actions/workflows/ci.yml/badge.svg)](https://github.com/arunsingh225/AI-Resume-Analyzer/actions)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://python.org)
[![React 18](https://img.shields.io/badge/react-18-61DAFB.svg)](https://react.dev)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

An AI-powered SaaS platform that analyzes resumes against ATS (Applicant Tracking System) standards, matches them to job descriptions using semantic AI, and provides actionable improvement suggestions.

![Dashboard Preview](https://img.shields.io/badge/status-production--ready-brightgreen)

---

## ✨ Features

### 🎯 Core Analysis
- **ATS Scoring** — Weighted scoring across 5 dimensions (keywords, formatting, sections, experience, skills) calibrated for 53+ professional fields
- **Field Detection** — Automatically detects your career domain (Frontend, Data Science, Finance, etc.) from resume content
- **Section Analysis** — Identifies missing sections and provides field-specific recommendations

### 🤖 AI-Powered
- **Semantic JD Matching** — Uses `sentence-transformers` (all-MiniLM-L6-v2) for genuine semantic similarity between resumes and job descriptions
- **Hybrid Matching** — 60% semantic embeddings + 40% TF-IDF for optimal accuracy with graceful fallback
- **Smart Skill Detection** — Synonym-aware matching (e.g., "ML" = "Machine Learning" = "Deep Learning")

### 📊 Data Visualization
- **Radar Charts** — 5-axis ATS breakdown (Recharts)
- **Skill Distribution** — Horizontal bar charts for skill categories
- **Animated Scores** — Smooth number transitions with ease-out cubic

### 🔒 Security
- **JWT Authentication** — Token-based auth with auto-refresh
- **Rate Limiting** — slowapi (3/min signup, 5/min login)
- **Password Validation** — 8+ chars, uppercase, lowercase, digit required
- **Magic Byte Validation** — Verifies actual file content, not just extensions
- **Security Headers** — X-Frame-Options, X-Content-Type-Options, XSS Protection

### 🎨 UI/UX
- **Dark Mode** — System preference detection + manual toggle + persistence
- **Glassmorphism Design** — Custom design system (Syne + DM Sans typography)
- **Skeleton Loaders** — Shimmer animations during loading states
- **Toast Notifications** — Context-based auto-dismiss notifications
- **Error Boundaries** — Crash protection with retry UI
- **Responsive** — Mobile-first, works on all screen sizes

### 📝 SaaS Features
- **Analysis History** — All analyses persisted with SHA-256 dedup
- **Feedback System** — Star rating, category selection, comments
- **PDF/DOCX Support** — Upload any resume format
- **Report Downloads** — Export analysis as JSON or PDF

---

## 🏗 Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | React 18, Vite, Tailwind CSS, Recharts, Lucide Icons |
| **Backend** | FastAPI, SQLAlchemy, Pydantic v2, slowapi |
| **AI/ML** | sentence-transformers, scikit-learn (TF-IDF), NLTK |
| **Database** | SQLite (dev) / PostgreSQL (prod) |
| **Auth** | JWT (PyJWT), bcrypt, passlib |
| **Testing** | pytest (68 tests), pytest-cov |
| **DevOps** | Docker, docker-compose, Nginx, GitHub Actions CI |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+

### 1. Clone & Setup Backend
```bash
git clone https://github.com/YOUR_USERNAME/ai-resume-analyzer.git
cd ai-resume-analyzer/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your JWT_SECRET

# Start server
uvicorn app.main:app --reload
```

### 2. Setup Frontend
```bash
cd ../frontend
npm install
npm run dev
```

### 3. Open
Navigate to `http://localhost:5173`

### Docker (Alternative)
```bash
docker-compose up --build -d
# Frontend: http://localhost
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

---

## 🧪 Testing

```bash
cd backend
python -m pytest tests/ -v --cov=app --cov-report=term-missing

# 68 tests covering:
# - Parser (21 tests): text cleaning, email/phone extraction, formatting
# - ATS Scorer (7 tests): scoring, grades, field-specific logic
# - JD Matcher (16 tests): TF-IDF, tokenization, semantic matching
# - API Integration (24 tests): auth, upload, validation, feedback, history
```

---

## 📁 Project Structure

```
ai-resume-analyzer/
├── backend/
│   ├── app/
│   │   ├── config.py              # Pydantic Settings (env-driven)
│   │   ├── constants.py           # Shared constants (DRY)
│   │   ├── database.py            # SQLAlchemy models + session
│   │   ├── main.py                # FastAPI app + middleware
│   │   ├── routers/
│   │   │   ├── auth.py            # Auth + rate limiting
│   │   │   ├── resume.py          # Upload + analysis + history save
│   │   │   ├── feedback.py        # Feedback CRUD + stats
│   │   │   ├── history.py         # Analysis history CRUD
│   │   │   └── ...
│   │   ├── services/
│   │   │   ├── ats_scorer.py      # ATS scoring engine (53 fields)
│   │   │   ├── field_detector.py  # Career field detection
│   │   │   ├── jd_matcher.py      # JD matching (semantic + TF-IDF)
│   │   │   ├── semantic_matcher.py # sentence-transformers wrapper
│   │   │   ├── parser.py          # Resume text extraction
│   │   │   └── ...
│   │   └── utils/
│   │       ├── auth_utils.py      # JWT helpers
│   │       └── response.py        # Standardized API responses
│   ├── tests/                     # 68 pytest tests
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ui/                # ErrorBoundary, Toast, Skeleton, FeedbackWidget, ThemeToggle
│   │   │   ├── charts/            # ATSRadarChart, SkillBarChart
│   │   │   └── ...                # 15+ feature components
│   │   ├── pages/                 # Home, Login, Signup, Dashboard
│   │   ├── hooks/                 # useAuth, useAnimatedNumber
│   │   └── services/              # API client, auth helpers
│   └── tailwind.config.js         # Custom design system
├── Dockerfile                     # Multi-stage build
├── docker-compose.yml             # One-command deployment
├── nginx.conf                     # Production web server
└── .github/workflows/ci.yml       # CI pipeline
```

---

## 🔧 Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `JWT_SECRET` | (required) | Secret key for JWT signing |
| `DATABASE_URL` | `sqlite:///./resume_analyzer.db` | Database connection string |
| `CORS_ORIGINS` | `http://localhost:5173` | Allowed CORS origins |
| `ENABLE_SEMANTIC_MATCHING` | `true` | Toggle AI semantic matching |
| `RATE_LIMIT_DEFAULT` | `60/minute` | Default API rate limit |

---

## 📄 API Documentation

Once running, visit: `http://localhost:8000/docs` (Swagger UI)

### Key Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/auth/signup` | Create account (rate limited: 3/min) |
| `POST` | `/auth/login` | Login (rate limited: 5/min) |
| `POST` | `/api/resume/analyze` | Upload + analyze resume |
| `POST` | `/api/jd/match` | Match resume to job description |
| `GET` | `/api/history/` | Get analysis history |
| `POST` | `/api/feedback/` | Submit feedback |
| `GET` | `/api/feedback/stats` | Feedback analytics |

---

## 📜 License

MIT License — See [LICENSE](LICENSE) for details.
