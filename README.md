# ULTRON AI – AI-powered Recruitment Intelligence Platform

ULTRON AI is a modern, premium recruitment platform built for the **India Runs × Redrob AI Hackathon**. 

Instead of traditional keyword-based ATS filtering, ULTRON AI leverages local cognitive AI models (**Sentence Transformers**), semantic matching vectors, and explainable scoring to understand job descriptions, analyze complete candidate profiles, and rank them with explainable human-readable AI analysis.

---

## 🌟 Key Features

1. **Semantic Matching Engine**: Uses local vector embeddings (`all-MiniLM-L6-v2`) via `sentence-transformers` for multi-dimensional cosine similarity matching. (No API Keys needed to run!).
2. **Explainable AI**: Scores candidates across 8 dimensions (Skills, Projects, Experience, Education, Soft Skills, Industry, Growth, GitHub/Portfolio) and produces clear explanations detailing strengths, weaknesses, risks, and interview recommendation.
3. **Conversational Recruiter Chat**: Context-aware recruitment assistant chatbot. Search, filter, and drill into candidates using natural language.
4. **Interactive Dashboard**: Modern UI showing recruitment KPIs, top fits, recent uploads, and interactive Chart.js visualizations.
5. **No-React Frontend**: Pure Vanilla JS, HTML5, and premium CSS3 enforcing the requested warm typography theme (Times New Roman for "ULTRON AI" branding, Helvetica for all other app text).

---

## 📂 Folder Structure

```
backend/
├── main.py                  # Entry Point
├── requirements.txt         # Dependencies
├── api/                     # REST API routers
│   ├── auth.py
│   ├── jobs.py
│   ├── resumes.py
│   ├── ...
├── database/                # SQLite DB (PostgreSQL-ready configuration)
│   ├── database.py
│   └── crud.py
├── services/                # Core AI business modules
│   ├── resume_parser.py
│   ├── matching_engine.py
│   ├── scoring_engine.py
│   └── ...
├── sample_data/             # Testing mock resumes and job description
│   └── ...
└── uploads/                 # Resumes storage folder

frontend/
├── index.html               # Premium landing page
├── login.html               # Recruiter authentication
├── dashboard.html           # Main Workspace
├── upload-job.html          # JD parser
├── upload-resume.html       # Resumes batch processor
├── candidates.html          # Candidates Pool
├── candidate-detail.html    # Profile details & explainability charts
├── rankings.html            # Sorted cognitive evaluation tables
├── analytics.html           # ChartJS graphics
├── chat.html                # Recruiter Chat Workspace
├── settings.html            # API settings configurations
└── static/
    ├── css/                 # Global styles & layout tokens
    └── js/                  # REST API requests & rendering logic
```

---

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.9+
- Modern Web Browser

### 1. Backend Setup
Navigate to the `backend` folder, install requirements, and launch the FastAPI server.

```bash
cd backend
pip install -r requirements.txt
python main.py
```
*The API server will run at `http://localhost:8000`. You can view the OpenAPI spec at `http://localhost:8000/docs`.*

### 2. Frontend Setup
The frontend consists of vanilla files. You can double-click `frontend/index.html` to open it in your browser, or run a simple local web server:

```bash
cd frontend
python -m http.server 3000
```
*Open `http://localhost:3000` in your web browser.*

### 3. Demo Credentials
Log into the recruiter workspace using the mock credentials provided:
- **Email:** `recruiter@ultron.ai`
- **Password:** `password123`

---

## ⚙️ AI Key Configurations (Optional)
By default, the platform runs using local sentence embeddings. To configure premium cloud models:
1. Log in to the application.
2. Navigate to **Settings** in the sidebar.
3. Paste your **Google Gemini** or **OpenAI** API keys and save.
4. Restart the Python backend server.
