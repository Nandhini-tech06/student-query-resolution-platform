# Student Query Resolution Platform using Generative AI & AI Agents

An enterprise-grade, role-based student-service platform designed to resolve student inquiries across diverse university operations — including **academics, examinations, admissions, hostel, library, transport, fees, placements, facilities, certificates, and campus regulations**.

> **Milestone 2 Release**: Core Student Query Resolution system, Retrieval-Augmented Generation (RAG) with anti-hallucination guardrails, Dynamic Knowledge Base CRUD with zero-retraining updates, modular Generative AI provider abstraction (Google Gemini + Grounded Synthesizer), source citations, and real-time student satisfaction feedback.

---

## 🏛️ System Architecture

```
                                  +-----------------------------+
                                  |         Web Browser         |
                                  +--------------+--------------+
                                                 |
                                                 | HTTP / REST (JSON)
                                                 v
                     +-------------------------------------------------------+
                     |                     React Frontend                    |
                     |  - Vite + React 19 + React Router DOM                 |
                     |  - Global AuthContext (JWT session management)        |
                     |  - Student Dashboard: Live RAG Query & History        |
                     |  - Admin Dashboard: Knowledge Base CRUD & Telemetry   |
                     +---------------------------+---------------------------+
                                                 |
                                                 | Authorization: Bearer <JWT>
                                                 v
                     +-------------------------------------------------------+
                     |                 FastAPI Backend Layer                 |
                     |  - Uvicorn ASGI Server & CORS Middleware              |
                     |  - JWT Authentication & Strict RBAC Dependencies      |
                     |  - Query Routing: POST /api/v1/queries/ask            |
                     |  - Knowledge CRUD: /api/v1/admin/knowledge            |
                     |  - Telemetry: /api/v1/admin/feedback-stats            |
                     +---------------------------+---------------------------+
                                                 |
                         +-----------------------+-----------------------+
                         |                                               |
                         v                                               v
         +-------------------------------+               +-------------------------------+
         |     Retrieval Engine (RAG)    |               |        Database Layer         |
         |  - Token & Phrase Matcher     | <-----------> |  - users                      |
         |  - Category weighting         |               |  - knowledge_items (Active)   |
         |  - Confidence Scoring         |               |  - student_queries            |
         |  - Anti-Hallucination Guard   |               |  (MySQL + SQLite dev fallback)|
         +---------------+---------------+               +-------------------------------+
                         |
                         | Context Chunks + Query
                         v
         +-------------------------------+
         |     Modular LLM Providers     |
         |    (BaseLLMProvider Interface)|
         |  ├── GeminiLLMProvider (GenAI)|  --> Uses 'gemini-2.5-flash' via google-genai
         |  └── DirectGroundingProvider  |  --> Zero-config deterministic grounded synthesizer
         +---------------+---------------+
                         |
                         v
           Grounded Answer + Cited Sources
            (or Official Unavailable Notice)
```

---

## 🧠 How the RAG Pipeline Works

The platform adheres to a strict **"Zero Hallucination"** standard. When a student submits a question:

1. **Category & Query Preprocessing**:
   - The question is cleaned of stopwords and tokenized into distinct search stems and n-grams.
   - Any selected service domain (e.g., `academics`, `fees`, `hostel`) provides contextual weighting.
2. **Context Retrieval**:
   - The system queries only **Active** (`is_active = True`) knowledge records from the database.
   - Scores candidates using multi-factor relevance (Title weight 45%, Content weight 30%, Tag weight 25%, plus exact phrase match bonuses).
3. **Anti-Hallucination Confidence Threshold**:
   - If the highest-scoring record falls below `RAG_MIN_CONFIDENCE` (default `0.20`), the pipeline **refuses to speculate**.
   - Instead, it returns an official fallback response:
     > *"I could not find verified institutional records or approved policies regarding your question. Please contact the relevant University Administrative Office or check official notices."*
4. **Context-Constrained Generation**:
   - If relevant knowledge is retrieved, the facts are passed with system instructions forbidding speculation.
   - The LLM synthesizes a structured, concise resolution.
5. **Mandatory Source Attribution**:
   - The exact document title, issuing authority (e.g., *Controller of Examinations*, *Chief Warden*), and reference URL are attached to the answer.
6. **Student History & Satisfaction Loop**:
   - Every resolved query is logged to the student's personal history. Students can rate answers as **Helpful** or **Not Helpful**, streaming telemetry to the Admin dashboard.

---

## 👥 Role Boundaries & Permissions

| Role | Permitted Routes | Primary Portal Capabilities |
| :--- | :--- | :--- |
| **`STUDENT`** | `/student/dashboard`<br>`/api/v1/queries/*` | • Submit natural-language service queries<br>• Select from 9 university service domains<br>• View real-time grounded answers with cited sources<br>• Access personal query history<br>• Rate resolution helpfulness (Feedback loop)<br>• Strictly blocked from Admin operations (403 Forbidden) |
| **`ADMIN`** | `/admin/dashboard`<br>`/api/v1/admin/*` | • Add, edit, and delete knowledge base circulars<br>• Archive outdated policies instantly with **zero model retraining**<br>• Search and filter knowledge base by category and keyword<br>• Monitor real-time student satisfaction metrics & queries handled<br>• Verify system health & database telemetry |

---

## 📁 Project Directory Structure

```
Student Query Resolution Platform/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── deps.py                  # DB sessions, JWT get_current_user, RBAC guards
│   │   │   └── v1/
│   │   │       ├── auth.py              # /login, /register, /me, role tests
│   │   │       ├── health.py            # /health with live database connectivity check
│   │   │       ├── queries.py           # /queries/ask, /queries/history, /queries/{id}/feedback
│   │   │       └── admin_knowledge.py   # /admin/knowledge CRUD & /admin/feedback-stats
│   │   ├── core/
│   │   │   ├── config.py                # Pydantic Settings (.env, Gemini config, RAG thresholds)
│   │   │   └── security.py              # bcrypt password hashing & PyJWT token utilities
│   │   ├── db/
│   │   │   ├── base.py                  # SQLAlchemy DeclarativeBase
│   │   │   ├── session.py               # MySQL engine & sessionmaker (SQLite dev fallback)
│   │   │   └── seed_knowledge.py        # 12 initial verified student service knowledge records
│   │   ├── models/
│   │   │   ├── user.py                  # User model with UserRole (STUDENT, ADMIN)
│   │   │   ├── knowledge.py             # KnowledgeItem model (title, category, content, is_active)
│   │   │   └── query.py                 # StudentQuery model (question, answer, sources, feedback)
│   │   ├── schemas/
│   │   │   ├── token.py                 # Token & TokenPayload schemas
│   │   │   ├── user.py                  # UserCreate, UserLogin, UserResponse
│   │   │   ├── knowledge.py             # KnowledgeCreate, KnowledgeUpdate, KnowledgeResponse
│   │   │   └── query.py                 # QueryAskRequest, QueryResponse, Feedback schemas
│   │   ├── services/
│   │   │   ├── rag/
│   │   │   │   └── retriever.py         # KnowledgeRetriever with lexical & confidence scoring
│   │   │   └── llm/
│   │   │       ├── base.py              # Abstract BaseLLMProvider interface
│   │   │       ├── gemini.py            # GeminiLLMProvider (google-genai / gemini-2.5-flash)
│   │   │       ├── direct.py            # DirectGroundingProvider (zero-config grounded synthesizer)
│   │   │       └── factory.py           # Dynamic provider selector
│   │   └── main.py                      # FastAPI initialization, CORS, lifespan startup seeder
│   ├── .env                             # Environment configuration
│   ├── .env.example                     # Environment template
│   ├── requirements.txt                 # Backend dependencies
│   ├── run.py                           # Uvicorn runner
│   ├── test_api.py                      # Milestone 1 integration tests
│   └── test_milestone2.py               # Milestone 2 RAG, Knowledge CRUD & RBAC test suite
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Navbar.jsx               # Navigation bar with role badge & sign-out
│   │   │   └── ProtectedRoute.jsx       # Client-side RBAC route protector
│   │   ├── context/
│   │   │   └── AuthContext.jsx          # Global auth state, persistent token store
│   │   ├── pages/
│   │   │   ├── Login.jsx                # User login with quick demo credentials
│   │   │   ├── Register.jsx             # Student registration
│   │   │   ├── StudentDashboard.jsx     # Live RAG Query interface, citations & history
│   │   │   ├── AdminDashboard.jsx       # Knowledge Base CRUD manager, search & telemetry
│   │   │   └── Unauthorized.jsx         # 403 Forbidden page
│   │   ├── services/
│   │   │   └── api.js                   # Axios client with JWT interceptor & API methods
│   │   ├── App.jsx                      # React Router routes
│   │   ├── index.css                    # Responsive CSS styling & modal themes
│   │   └── main.jsx                     # React DOM root
│   ├── package.json
│   └── vite.config.js                   # Vite config with backend proxy
└── README.md                            # Complete architecture & setup documentation
```

---

## 🚀 Getting Started

### 1. Prerequisites
- **Python 3.10+** (Tested on Python 3.13)
- **Node.js v18+** (Tested on Node v22.15) & **npm**
- **MySQL 8.0+** (Optional: application automatically falls back to local SQLite for zero-setup development)
- **Gemini API Key** (Optional: configure `GEMINI_API_KEY` in `.env` to enable Google Gemini, or leave blank to use the built-in deterministic grounding synthesizer)

---

### 2. Backend Setup

1. Open a terminal and navigate to `backend/`:
   ```powershell
   cd backend
   ```

2. Activate the virtual environment:
   ```powershell
   .\venv\Scripts\Activate.ps1   # Windows PowerShell
   # source venv/bin/activate    # Linux/macOS
   ```

3. Configure `.env`:
   ```ini
   DATABASE_URL="mysql+pymysql://root:password@localhost:3306/student_query_db"
   ENABLE_SQLITE_FALLBACK=True

   # Optional: Add your Google Gemini API key to activate Gemini 2.5 Flash
   GEMINI_API_KEY=""
   GEMINI_MODEL="gemini-2.5-flash"
   ```

4. Run the Milestone 2 automated test suite:
   ```powershell
   python test_milestone2.py
   ```

5. Start the backend development server:
   ```powershell
   python run.py
   ```
   - API is running at: `http://localhost:8000`
   - Interactive OpenAPI Docs: `http://localhost:8000/docs`
   - Health check: `http://localhost:8000/api/v1/health`

---

### 3. Frontend Setup

1. Open a second terminal and navigate to `frontend/`:
   ```powershell
   cd frontend
   ```

2. Start the Vite development server:
   ```powershell
   npm run dev
   ```
   The application will be accessible at: `http://localhost:5173`.

---

## 🔑 Default Credentials for Testing

| Role | Email | Password | Pre-configured Privileges |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin@platform.edu` | `Admin@12345` | Full Knowledge Base CRUD, document archiving, feedback stats |
| **Student** | `sarah.connor@student.edu` | `SecurePass@2026` | Query asking, prompt suggestions, personal history, feedback ratings |

*(Both accounts feature 1-click autofill demo buttons on the Sign In page).*

---

## 📡 API Endpoints Reference

### Student Query Resolution
- `POST /api/v1/queries/ask`: Submit natural-language query; returns grounded answer with cited source documents and confidence score.
- `GET /api/v1/queries/history`: Retrieve student's personal query history and resolution records.
- `POST /api/v1/queries/{query_id}/feedback`: Submit `HELPFUL` or `UNHELPFUL` feedback rating and comments.

### Admin Knowledge Base Management
- `GET /api/v1/admin/knowledge`: List knowledge items with keyword search (`q`) and category filters.
- `POST /api/v1/admin/knowledge`: Add a new institutional document, circular, or policy.
- `GET /api/v1/admin/knowledge/{id}`: Retrieve single knowledge item.
- `PUT /api/v1/admin/knowledge/{id}`: Update existing knowledge item without model retraining.
- `DELETE /api/v1/admin/knowledge/{id}`: Delete a knowledge record.
- `PATCH /api/v1/admin/knowledge/{id}/toggle-status`: Toggle Active / Archived status.
- `GET /api/v1/admin/feedback-stats`: Aggregated metrics on query volume, resolution rate, and student satisfaction.

### Authentication & System Health
- `POST /api/v1/auth/register`: Public student registration.
- `POST /api/v1/auth/login`: Authenticate credentials; returns JWT token with role claims.
- `GET /api/v1/auth/me`: Current user profile.
- `GET /health` & `GET /api/v1/health`: System health reporting active database engine and latency.

---

## 🗺️ Project Roadmap

- [x] **Milestone 1**: Core Architecture, FastAPI Backend, React Frontend, MySQL Integration, User Model, JWT Authentication, Strict RBAC, Dashboard Placeholders, Health Check.
- [x] **Milestone 2**: Core Student Query Resolution System, RAG Pipeline with Anti-Hallucination Guardrails, Dynamic Knowledge Base CRUD, Modular LLM Providers (Google Gemini & Grounded Synthesizer), Source Citations, Feedback Loop.
- [ ] **Milestone 3**: Vector Database setup & Semantic Embeddings for Institutional Knowledge Base.
- [ ] **Milestone 4**: Multi-Source Ingestion Pipeline (Automatic PDF Parsing, University Website Crawlers, Student Database APIs).
- [ ] **Milestone 5**: Multi-Domain AI Agents for Query Routing & Tool Coordination (Academic Agent, Exam Agent, Hostel Agent, Accounts Agent).
- [ ] **Milestone 6**: Personalized Student Record Authorization Gateway & Advanced Feedback Analytics.
