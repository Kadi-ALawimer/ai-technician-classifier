# AI Technician Request Classifier

An AI-powered web application that reads a free-text description of a home
maintenance problem (in Arabic or English), classifies it by **category**
(plumbing, electrical, carpentry, AC, insulation, flooring, other) and
**priority** (normal / urgent), and — if the text describes more than one
independent problem — automatically splits it into separate requests.

Built as a practical test project for an **AI Application Developer**
role. It is intentionally scoped to be small, correct, and easy to explain
in a live technical interview rather than feature-heavy.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Features](#2-features)
3. [Tech Stack](#3-tech-stack)
4. [Architecture](#4-architecture)
5. [Project Structure](#5-project-structure)
6. [Requirements](#6-requirements)
7. [Installation](#7-installation)
8. [Environment Variables](#8-environment-variables)
9. [Running the Backend](#9-running-the-backend)
10. [Running the Frontend](#10-running-the-frontend)
11. [Mock AI Mode](#11-mock-ai-mode)
12. [Real AI Mode](#12-real-ai-mode)
13. [API Endpoints](#13-api-endpoints)
14. [Database](#14-database)
15. [AI Prompt / Structured Output](#15-ai-prompt--structured-output)
16. [Security Considerations](#16-security-considerations)
17. [Testing](#17-testing)
18. [Technical Decisions](#18-technical-decisions)
19. [AI Tools Used](#19-ai-tools-used)
20. [Limitations](#20-limitations)
21. [Future Improvements](#21-future-improvements)
22. [Pushing This Project to GitHub](#22-pushing-this-project-to-github)
23. [How to Explain This Project in the Live Review](#23-how-to-explain-this-project-in-the-live-review)
24. [Potential Live-Coding Changes](#24-potential-live-coding-changes)
25. [Final Checklist](#25-final-checklist)

---

## 1. Project Overview

A customer types a problem description such as:

> "عندي تسريب مويه في المطبخ والكهرباء مقطوعة في غرفة النوم"

The backend sends this text to an LLM with a strict instruction to return
**structured JSON only**. The AI splits it into independent problems and
classifies each one:

```json
{
  "requests": [
    { "problem": "تسريب مويه في المطبخ", "category": "plumbing", "priority": "urgent" },
    { "problem": "الكهرباء مقطوعة في غرفة النوم", "category": "electrical", "priority": "normal" }
  ]
}
```

The user reviews the result, can correct the category/priority of any
item, confirms, and the request is saved to the database. A second page
lists every saved request.

## 2. Features

- Natural-language problem analysis in **Arabic and English**.
- Automatic **splitting** of a message into multiple independent requests.
- Editable **category** and **priority** before saving (AI proposes, human
  confirms).
- Swappable AI provider: **mock** (no API key needed), **Gemini**, or
  **OpenAI**.
- Strict **server-side validation** of every field (never trusts the AI or
  the frontend blindly).
- Responsive, mobile-first UI with loading / error / empty states.
- Automatic SQLite database creation on first run.
- Basic automated backend test suite (pytest).

## 3. Tech Stack

| Layer | Technology | Notes |
|---|---|---|
| Frontend | React 18 + Vite + **TypeScript** | Mobile-first, responsive CSS (no UI framework) |
| Backend | Python 3.11+ + **FastAPI** | Async, Pydantic-validated |
| AI | **Gemini** or **OpenAI** (swappable) + a **Mock** provider | Structured JSON output |
| Database | **SQLite** + SQLModel (SQLAlchemy 2.0 + Pydantic) | Auto-created on first run |
| API style | **REST** (JSON over HTTP) | 4 endpoints total |
| Testing | **pytest** | Runs against the mock provider, no API key needed |

See [Technical Decisions](#18-technical-decisions) for the reasoning
behind each of these choices.

## 4. Architecture

```
┌─────────────┐      POST /api/analyze       ┌──────────────┐      ┌──────────────┐
│   React     │ ───────────────────────────► │   FastAPI    │ ───► │  AI Service  │
│  (Vite,TS)  │                               │   Backend    │      │   (Gemini /  │
│             │ ◄─────────────────────────── │              │ ◄─── │  OpenAI /    │
└─────────────┘   { requests: [...] }         └──────────────┘      │   Mock)      │
      │                                              │               └──────────────┘
      │  user reviews & edits                        │
      │  POST /api/requests                          ▼
      └──────────────────────────────────────►  ┌──────────┐
                                                  │  SQLite  │
                                                  └──────────┘
```

Strict separation of concerns:

- **Frontend (React)** only talks to our own backend. It never calls
  Gemini/OpenAI directly and never sees an API key.
- **Backend (FastAPI)** owns all validation, orchestration, and database
  access.
- **AI Service** is an isolated layer (`app/services/ai_service.py` +
  `app/services/providers/*`). Routes never call a provider SDK/API
  directly — they only call `analyze_request()`.
- **Database (SQLite)** is only written to after the user confirms.

## 5. Project Structure

```
ai-technician-classifier/
│
├── frontend/
│   ├── src/
│   │   ├── components/        # Navigation, LoadingSpinner, ProblemResultCard
│   │   ├── pages/              # NewRequestPage, RequestsPage
│   │   ├── services/           # api.ts - the only file that calls fetch()
│   │   ├── types/               # Shared TS types (mirrors backend schemas)
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── index.css
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig*.json
│   ├── index.html
│   └── .env.example
│
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app, CORS, startup, error handlers
│   │   ├── api/                 # Route handlers (analyze, requests, health)
│   │   ├── models/              # SQLModel table + shared enums
│   │   ├── schemas/             # Pydantic request/response contracts
│   │   ├── services/
│   │   │   ├── ai_service.py    # Orchestrator: validate provider output
│   │   │   ├── prompts.py       # The single source of truth for the LLM prompt
│   │   │   └── providers/       # base / mock / gemini / openai / factory
│   │   ├── database/            # SQLite engine + session
│   │   └── core/                # Settings (.env) + logging setup
│   ├── tests/                   # pytest suite
│   ├── requirements.txt
│   ├── pytest.ini
│   └── .env.example
│
├── .gitignore
└── README.md
```

This mirrors a typical small production service (routes / schemas / models
/ services separated) without adding layers the project doesn't need
(no repository pattern, no dependency-injection framework, etc. — see
[Technical Decisions](#18-technical-decisions)).

## 6. Requirements

You said you currently only have **Visual Studio Code**. Here is exactly
what to install, in order.

| Tool | Why | Download |
|---|---|---|
| **Git** | version control, pushing to GitHub | https://git-scm.com/downloads |
| **Node.js** (LTS, v20+) | runs the React/Vite frontend | https://nodejs.org |
| **Python** (3.11+) | runs the FastAPI backend | https://www.python.org/downloads/ |
| **VS Code extensions** (optional but recommended) | *Python* (Microsoft), *Pylance*, *ESLint* — install from the Extensions panel (`Ctrl+Shift+X`) inside VS Code | — |

During the Python installer on Windows, **check "Add python.exe to PATH"**.

After installing, open a terminal **inside VS Code** (`` Ctrl+` ``, make
sure it's set to *PowerShell*) and verify everything:

```powershell
node --version
npm --version
python --version
git --version
```

Each command should print a version number. If `python --version` fails,
try `py --version` instead (Windows sometimes aliases it) — if `py` works,
use `py` instead of `python` in the commands below.

## 7. Installation

Run these commands **in order**, from VS Code's PowerShell terminal.

### 7.1 Get the project onto your machine

If you received this project as a folder/zip, extract it and open that
folder in VS Code (`File > Open Folder`). Then open a terminal and skip to
step 7.2.

If you are starting from scratch instead:

```powershell
mkdir ai-technician-classifier
cd ai-technician-classifier
```

(then place the `frontend/`, `backend/`, `.gitignore`, and `README.md`
provided into this folder)

### 7.2 Backend setup

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
```

> If PowerShell blocks the activation script with an "execution policy"
> error, run this once (as your normal user, not admin):
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, then re-run the
> `Activate.ps1` command.

```powershell
pip install -r requirements.txt
copy .env.example .env
```

Your `.env` defaults to `AI_PROVIDER=mock`, so the backend already runs
with **no API key required**. See [Real AI Mode](#12-real-ai-mode) to
switch to Gemini/OpenAI later.

### 7.3 Frontend setup

Open a **second** PowerShell terminal (keep the backend one for later) and
run:

```powershell
cd frontend
npm install
copy .env.example .env
```

The frontend `.env` only configures the backend URL — it never contains an
API key (see [Security Considerations](#16-security-considerations)).

### 7.4 Run both

See [Running the Backend](#9-running-the-backend) and
[Running the Frontend](#10-running-the-frontend) below — you need **both
terminals running at the same time**.

## 8. Environment Variables

### `backend/.env`

| Variable | Default | Description |
|---|---|---|
| `AI_PROVIDER` | `mock` | `mock` \| `gemini` \| `openai` |
| `GEMINI_API_KEY` | *(empty)* | Required only if `AI_PROVIDER=gemini` |
| `GEMINI_MODEL` | `gemini-2.0-flash` | Gemini model name |
| `OPENAI_API_KEY` | *(empty)* | Required only if `AI_PROVIDER=openai` |
| `OPENAI_MODEL` | `gpt-4o-mini` | OpenAI model name |
| `DATABASE_URL` | `sqlite:///./data/app.db` | SQLite connection string |
| `CORS_ORIGINS` | `http://localhost:5173,http://127.0.0.1:5173` | Allowed frontend origins |

### `frontend/.env`

| Variable | Default | Description |
|---|---|---|
| `VITE_API_BASE_URL` | `http://localhost:8000` | Backend base URL |

**`backend/.env` and `frontend/.env` are both git-ignored.** Only the
`.env.example` files (with no real secrets) are committed.

## 9. Running the Backend

In the terminal with the `.venv` activated, inside `backend/`:

```powershell
uvicorn app.main:app --reload
```

- API base URL: `http://localhost:8000`
- Interactive docs (Swagger UI): `http://localhost:8000/docs`
- The SQLite database file is created automatically on first run at
  `backend/data/app.db`.

## 10. Running the Frontend

In the second terminal, inside `frontend/`:

```powershell
npm run dev
```

- App URL: `http://localhost:5173`
- Open it in your browser. Go to **New Request**, describe a problem, and
  click **Analyze**.

## 11. Mock AI Mode

With `AI_PROVIDER=mock` (the default), no API key or internet connection
is needed. A small rule-based classifier simulates the AI so the entire
app works end-to-end. It correctly handles the examples from the spec:

| Input | Output |
|---|---|
| "water leak in kitchen" | plumbing / urgent |
| "AC is not cooling" | ac / normal |
| "power is out in bedroom" | electrical / normal |
| "water leak in kitchen and electricity is out in bedroom" | 2 requests: plumbing/urgent, electrical/normal |
| "عندي تسريب مويه في المطبخ والكهرباء مقطوعة في غرفة النوم" | 2 requests: plumbing/urgent, electrical/... |

The mock provider lives entirely in
`backend/app/services/providers/mock_provider.py`. It's simple
keyword/heuristic logic **by design** — it only needs to stand in for a
real LLM during development and demos; see
[AI Prompt / Structured Output](#15-ai-prompt--structured-output) for how
the real providers actually understand meaning instead of keywords.

## 12. Real AI Mode

### Option A — Gemini (recommended: generous free tier, fast, simple REST API)

1. Go to **Google AI Studio** (`https://aistudio.google.com`), sign in with
   a Google account.
2. Click **"Get API key"** → **"Create API key"**.
3. Copy the generated key.
4. In `backend/.env`:
   ```
   AI_PROVIDER=gemini
   GEMINI_API_KEY=your_real_key_here
   ```
5. Restart the backend (`Ctrl+C`, then `uvicorn app.main:app --reload` again).

### Option B — OpenAI

1. Go to `https://platform.openai.com/api-keys`, sign in.
2. Click **"Create new secret key"**, copy it (you can't view it again
   later).
3. In `backend/.env`:
   ```
   AI_PROVIDER=openai
   OPENAI_API_KEY=your_real_key_here
   ```
4. Restart the backend.

**Never commit a real key.** `backend/.env` is git-ignored specifically to
prevent this. Only `backend/.env.example` (with empty values) is tracked.

**Why Gemini over OpenAI for this project?** Both work identically well
through this codebase (the provider is a one-line env var change). Gemini
was chosen as the primary recommendation because, at the time of writing,
its free tier is generous enough to run this entire test end-to-end
without a billing account — convenient for a take-home test. If you
already have OpenAI credits, `AI_PROVIDER=openai` works exactly the same
way.

## 13. API Endpoints

Base URL: `http://localhost:8000`

### `GET /api/health`
Liveness check.
```json
{ "status": "ok", "ai_provider": "mock" }
```

### `POST /api/analyze`
Classifies free text into one or more structured requests. Does **not**
save anything to the database.

Request:
```json
{ "description": "عندي تسريب مويه في المطبخ والكهرباء مقطوعة في غرفة النوم" }
```

Response `200`:
```json
{
  "requests": [
    { "problem": "تسريب مويه في المطبخ", "category": "plumbing", "priority": "urgent" },
    { "problem": "الكهرباء مقطوعة في غرفة النوم", "category": "electrical", "priority": "normal" }
  ]
}
```

Errors: `422` (empty/too-short/too-long description), `502` (AI provider
failed or returned an unusable response).

### `POST /api/requests`
Saves one (possibly user-edited) classified request.

Request:
```json
{ "problem": "تسريب مويه في المطبخ", "category": "plumbing", "priority": "urgent" }
```

Response `201`:
```json
{
  "id": 1,
  "problem": "تسريب مويه في المطبخ",
  "category": "plumbing",
  "priority": "urgent",
  "created_at": "2026-09-14T10:15:00Z"
}
```

Errors: `422` if `category`/`priority` aren't in the fixed lists, or
`problem` is blank/too long.

### `GET /api/requests`
Returns all saved requests, newest first.

## 14. Database

- **Engine:** SQLite (file-based, zero setup — appropriate for this
  project's scope; see [Technical Decisions](#18-technical-decisions)).
- **ORM:** SQLModel (built on SQLAlchemy 2.0 + Pydantic).
- **Table:** `request`

| Column | Type | Notes |
|---|---|---|
| `id` | integer | primary key, auto-increment |
| `problem` | string | the problem text (max 500 chars) |
| `category` | enum | one of the 7 fixed categories |
| `priority` | enum | `normal` \| `urgent` |
| `created_at` | datetime | set automatically (UTC) on insert |

- **Initialization:** `app/database/db.py::create_db_and_tables()` runs on
  every backend startup (FastAPI `lifespan`). It creates the `data/`
  folder and `app.db` file automatically if they don't exist — **no
  manual migration step is needed** for a project this size. (A real
  production system would add Alembic migrations once the schema needs to
  evolve safely against existing data — see
  [Future Improvements](#21-future-improvements).)

## 15. AI Prompt / Structured Output

The full prompt lives in `backend/app/services/prompts.py`
(`SYSTEM_PROMPT`). Summary of what it instructs the model to do:

1. Read a customer message (Arabic, English, or mixed).
2. If it describes **more than one independent problem**, split it into
   separate entries — never merge two different problems, never split one
   problem into fragments.
3. Classify each into one of exactly 7 categories (`other` if unclear —
   never invent a new category).
4. Classify each as `urgent` only when there's a real risk of damage,
   injury, or an active emergency (flooding, exposed/sparking wires, gas
   smell, dangerous AC failure); everything else is `normal`.
5. Keep `problem` text in the language the customer used (no translation).
6. **Return JSON only** — no explanations, no markdown fences.

**Enforcing structure, twice:**
- *At the provider level:* Gemini uses `responseSchema` +
  `responseMimeType: application/json`; OpenAI uses Structured Outputs
  (`response_format: json_schema`, `strict: true`). Both constrain the
  model's output at generation time.
- *At the backend level (the real safety net):* regardless of what the
  provider promises, `ai_service.py` validates every response against our
  Pydantic schema (`AnalyzeResponseOut`) before it goes anywhere near the
  frontend or database. An invalid category, a missing field, or malformed
  JSON is caught here and turned into a clean `502` error — never passed
  through.

## 16. Security Considerations

- **API keys never reach the frontend.** They are read only from
  `backend/.env` via `pydantic-settings`. The frontend's `.env` only ever
  contains `VITE_API_BASE_URL` — since Vite exposes any `VITE_`-prefixed
  variable to the browser bundle, an API key must never be prefixed that
  way (or placed in frontend code at all).
- **CORS is restricted** to the known local frontend origins
  (`http://localhost:5173`) — not `allow_origins=["*"]`.
- **Server-side validation is the source of truth.** Every field
  (`category`, `priority`, string lengths) is re-validated by FastAPI/
  Pydantic on the backend regardless of what the frontend already checked
  or what the AI returned.
- **No stack traces are ever sent to the client.** A global exception
  handler in `main.py` catches anything unhandled and returns a generic
  `500` message; specific, expected failures (bad AI response, DB error)
  return clean, short messages. Full details are only written to the
  server logs.
- **`.env` files are git-ignored**; only `.env.example` (no secrets) is
  committed.

## 17. Testing

Backend tests use **pytest** and run entirely against the **mock**
provider and an in-memory SQLite database — no API key or network access
needed.

```powershell
cd backend
.venv\Scripts\Activate.ps1
pytest -v
```

Covered (see `backend/tests/`):
- `test_analyze.py` — classification response shape/validation, correct
  category/priority for known examples, splitting one message into
  multiple requests (English and Arabic), rejecting empty/too-short
  descriptions, guarding against invalid category/priority values ever
  reaching the response.
- `test_requests.py` — creating a request, listing requests (empty state
  and populated, newest-first), rejecting invalid `category`/`priority`/
  blank `problem`/missing fields.

> **Note on this delivery:** all Python files were syntax-checked
> (`py_compile`), and the test logic was manually traced against the mock
> provider's rules. Actually *running* `pip install` + `pytest` was done
> in the environment that prepared this project, but you should run
> `pytest -v` yourself after installation to confirm on your machine —
> that's also a good, honest thing to mention in the live review ("I
> wrote and ran these tests locally").

## 18. Technical Decisions

Written the way you'd explain them to an interviewer — short and honest,
not over-engineered justifications.

- **React + Vite, TypeScript (not JavaScript):** Vite gives near-instant
  dev server startup/HMR, which matters for a short test. TypeScript was
  chosen over plain JS because the frontend and backend share an exact
  data contract (category/priority enums, request shapes) — types catch a
  typo like `"eletrical"` at compile time instead of a runtime bug, and it
  reads as more professional in review without adding real complexity for
  a project this size.
- **FastAPI (not Flask/Django):** native Pydantic integration gives
  request/response validation "for free" (critical here, since validating
  AI output is the whole point), automatic OpenAPI docs at `/docs`, and
  async support for calling external AI APIs efficiently.
- **SQLite (not PostgreSQL):** zero setup — no separate database server to
  install/run for a test project. SQLAlchemy/SQLModel is the same ORM
  either way, so switching to PostgreSQL later is a one-line
  `DATABASE_URL` change, not a rewrite.
- **SQLModel:** combines the SQLAlchemy table definition and the Pydantic
  validation model in one class, which removes boilerplate for a project
  with a single simple entity (`Request`).
- **REST, not GraphQL:** three simple resources, no complex nested
  queries — REST is the simplest thing that fits and the most common
  expectation in an interview setting.
- **Structured JSON output from the LLM:** free-text output would require
  fragile regex/string parsing. Structured output (schema-constrained at
  the provider level, then re-validated with Pydantic) makes the AI's
  response as reliable as calling any other typed API.
- **Environment variables for configuration (not hardcoded values):**
  standard 12-factor practice — lets the same code run in mock mode, with
  Gemini, or with OpenAI, and keeps secrets out of source control.
- **A separate Mock provider:** lets the whole app (frontend, backend, DB,
  tests, CI) run and be demoed with zero API keys and zero cost, and makes
  the AI Service layer's abstraction (`AIProvider` interface) obvious and
  testable.

## 19. AI Tools Used

AI assistants were used as **development tools**, not as an autonomous
author of the project:

- **Claude** — scaffolding the project structure, generating the initial
  implementation of the backend/frontend code, reviewing the API/service
  architecture, improving error handling and edge-case coverage, and
  drafting this documentation.
- **ChatGPT** — used for debugging, reviewing alternative approaches, and
  cross-checking implementation decisions.

I reviewed, understood, and tested the resulting code myself. I can
explain every file's purpose, walk through the request flow end-to-end,
and modify the code live — which is the point of the "Live Review"
sections below.

## 20. Limitations

- The mock AI provider uses simple keyword rules, not real language
  understanding (by design — see [Mock AI Mode](#11-mock-ai-mode)); only
  the real Gemini/OpenAI providers genuinely understand meaning.
- No authentication — anyone with network access to the backend can read
  or create requests (acceptable for a local test project; see
  [Future Improvements](#21-future-improvements)).
- No pagination on `GET /api/requests` — fine at test-project scale, would
  need to be added before this held thousands of rows.
- No automated evaluation dataset for measuring real AI classification
  accuracy over time (only manual/example-based testing).
- Splitting logic depends entirely on the LLM's judgment (or, in mock
  mode, on simple heuristics) — there's no guaranteed upper bound on how
  many sub-requests one message could produce.

## 21. Future Improvements

- Authentication & per-user request ownership.
- PostgreSQL for concurrent multi-user production use.
- Redis caching for repeated/similar AI classification requests.
- Rate limiting on `/api/analyze` (protects both cost and abuse).
- Monitoring/observability (structured logs, request tracing, error
  alerting).
- A small labeled evaluation dataset + automated accuracy scoring for the
  AI classifier, to catch prompt regressions.
- Technician matching/assignment logic once categories are trusted.
- Deeper multilingual support beyond Arabic/English.
- Arabic-specific prompt tuning (dialects, informal phrasing).
- Containerization (Docker) and a CI/CD pipeline (lint + test on every
  push).
- Production deployment guide (managed Postgres, HTTPS, secrets manager).

## 22. Pushing This Project to GitHub

From the project root (`ai-technician-classifier/`), in PowerShell:

```powershell
git init
git add .
git status
```

**Check the `git status` output carefully** — you should NOT see `.env`,
`node_modules/`, `__pycache__/`, or any `.db` file listed. If you do, stop
and check `.gitignore` before continuing.

```powershell
git commit -m "Initial commit: AI Technician Request Classifier"
git branch -M main
```

Now create an **empty** repository on GitHub (github.com → New repository
→ do NOT initialize it with a README, since you already have one).
GitHub will show you a remote URL like
`https://github.com/your-username/ai-technician-classifier.git` — copy it
and run:

```powershell
git remote add origin https://github.com/your-username/ai-technician-classifier.git
git push -u origin main
```

That's it — refresh the GitHub page and your project should be there.

## 23. How to Explain This Project in the Live Review

A ~3-minute spoken walkthrough you can adapt in your own words:

> "This is a small service-request classifier. A customer describes a
> problem in free text — Arabic or English — and the system uses an LLM to
> classify it by category and priority, and splits it into separate
> requests if the customer actually described more than one problem.
>
> The architecture is a standard three-tier setup: a React/Vite/TypeScript
> frontend, a FastAPI backend, and SQLite for storage. The frontend never
> talks to the AI provider directly — it only calls my own backend, which
> is the only place that holds the API key, in an environment variable,
> never committed to git.
>
> Inside the backend, I kept the AI logic in its own service layer, so the
> routes don't know or care whether I'm using Gemini, OpenAI, or a mock
> provider — that's controlled by one environment variable, `AI_PROVIDER`.
> I built a mock provider specifically so the whole app — frontend,
> backend, database, and tests — works end-to-end without needing an API
> key at all.
>
> The most important design decision was forcing the AI to return
> structured JSON matching a strict schema, instead of free text. I
> constrain it at the provider level using Gemini's response schema (or
> OpenAI's structured outputs), and then I independently re-validate the
> response with Pydantic on my backend before it's ever shown to the user
> or saved — so even if the AI misbehaves, invalid data can't get through.
>
> On the frontend, the user always reviews and can correct the AI's
> category/priority guess before confirming — the AI proposes, the human
> confirms, nothing is silently auto-saved.
>
> I kept the scope deliberately tight — no auth, no admin dashboard, no
> extra features — because the goal was a correct, clean, explainable
> implementation rather than a large surface area."

### Likely interviewer questions — short, honest answers

**Why React?**
Industry-standard, component model fits this UI (a form + a list) well,
and I wanted a build tool (Vite) with fast local iteration for a timed
test.

**Why FastAPI?**
Native Pydantic validation (critical since I'm validating untrusted AI
output), automatic interactive docs, and async support for calling
external AI APIs without blocking.

**Why SQLite?**
Zero setup for a project this size — no database server to install. It's
the same SQLAlchemy/SQLModel code either way, so moving to PostgreSQL
later is a config change, not a rewrite.

**Why did you put the API key in the backend?**
Anything shipped to the browser (including Vite env vars prefixed
`VITE_`) is publicly visible in the compiled JS bundle. A key there could
be extracted by anyone and used on my account/bill. The backend is the
only trusted environment, so it's the only place that ever sees the key.

**Why not call the AI directly from React?**
Same reason as above (key exposure), plus it means the frontend can't
enforce validation or business rules — the backend has to be the single
source of truth for what's "valid" data anyway, so it should own the AI
call too.

**How does the AI split multiple problems?**
The prompt explicitly instructs it: if the message describes more than
one independent problem, return multiple entries in the `requests` array,
one per problem, and never merge or over-split. The model reasons about
this semantically, not with keyword matching (that's how the *mock*
provider works, as a stand-in — the real providers understand meaning).

**How do you validate the AI response?**
Two layers: the provider is asked for schema-constrained output (Gemini
`responseSchema` / OpenAI `json_schema` strict mode), and then, regardless
of that, the backend parses the JSON and validates it against a Pydantic
model (`AnalyzeResponseOut`) with enum-constrained `category`/`priority`
fields. Anything that doesn't match is rejected before it reaches the
user.

**What happens if the AI returns invalid JSON?**
`json.loads()` (or the provider's parsing) fails, that's caught, logged,
and turned into a generic `AIServiceError` → the API returns `502` with a
short, user-safe message. No raw error or stack trace reaches the
frontend.

**How do you handle API failure (network down, provider outage)?**
Every provider call is wrapped in a try/except that raises a single
`AIProviderError`; `ai_service.py` catches that and raises
`AIServiceError`; the route catches that and returns `502` with a clear
message. The frontend catches the error from `fetch` and shows it in an
alert box instead of crashing.

**How would you improve this system for production?**
Add auth, move to PostgreSQL, add rate limiting on `/api/analyze` (LLM
calls cost money), add monitoring/logging aggregation, and build a small
evaluation dataset to track classification accuracy over time instead of
eyeballing it.

**Why did you use structured JSON output instead of parsing free text?**
Free text would require fragile regex/NLP parsing on my side and would
break unpredictably. Structured output makes the LLM behave like any
other typed API I'd integrate with.

**How would you prevent prompt injection?**
The user's text is only ever inserted into the prompt as *data* (wrapped
in a clearly delimited block, e.g. `"""..."""`), never concatenated into
instructions. The model's output is constrained by schema and
independently re-validated, so even if someone tried to inject
instructions into their problem description, the worst case is a
misclassified request — not code execution or a broken response — because
nothing from the AI is ever trusted enough to run, execute, or bypass
validation.

**How would you evaluate AI classification accuracy?**
Build a small labeled dataset of real-world-style descriptions with their
correct category/priority, run it through the classifier, and compute
accuracy/precision per category. Track that over time as the prompt or
model changes, instead of relying on manual spot-checks.

**How would you support Arabic better?**
Test with real regional dialects and informal phrasing (not just Modern
Standard Arabic), and potentially fine-tune or few-shot the prompt with
Arabic-specific examples if accuracy on dialectal text turns out weaker.

**How would you scale the application?**
Move the database to PostgreSQL with connection pooling, put the backend
behind multiple stateless replicas behind a load balancer (it's already
stateless — no in-memory session state), add caching for repeated/similar
AI calls, and move to async task queues if AI latency becomes a
bottleneck for request throughput.

**Why did you create an AI service layer instead of calling Gemini/OpenAI
directly in the route?**
Separation of concerns: the route shouldn't need to know which provider
is active, how to build that provider's specific request payload, or how
to parse its specific response format. This also makes the provider
trivially swappable (one env var) and testable (the mock provider is just
another implementation of the same interface).

**What would you change if the application had 1 million users?**
Realistically: PostgreSQL with read replicas, horizontal backend scaling,
a message queue between the API and the AI call (so a slow LLM response
doesn't hold an HTTP connection open), aggressive caching for repeated
inputs, rate limiting per user, and much more attention to AI provider
cost — since that becomes the dominant scaling cost, not compute.

## 24. Potential Live-Coding Changes

Five small, realistic changes an interviewer might ask for, and exactly
where to make each one.

### 1. Add a new category (e.g. "landscaping")

- `backend/app/models/enums.py` — add `LANDSCAPING = "landscaping"` to
  `Category`.
- `backend/app/services/prompts.py` — add `"landscaping"` to
  `ALLOWED_CATEGORIES` and mention it in the prompt's category list/rules.
- `frontend/src/types/index.ts` — add `"landscaping"` to the `CATEGORIES`
  array and a label in `CATEGORY_LABELS`.
- That's it — the dropdown, validation, and prompt all pick it up
  automatically since everything reads from these two lists.

### 2. Change the "urgent" logic

- The rules the AI follows live in `SYSTEM_PROMPT` in
  `backend/app/services/prompts.py` (edit the "urgent" bullet point).
- The mock provider's equivalent heuristic is `_URGENT_KEYWORDS` and the
  plumbing/leak special case in
  `backend/app/services/providers/mock_provider.py`.

### 3. Add a `DELETE /api/requests/{id}` endpoint

In `backend/app/api/routes_requests.py`, add:

```python
@router.delete("/requests/{request_id}", status_code=204)
def delete_request(request_id: int, session: Session = Depends(get_session)) -> None:
    db_request = session.get(RequestModel, request_id)
    if not db_request:
        raise HTTPException(status_code=404, detail="Request not found.")
    session.delete(db_request)
    session.commit()
```

Then add a "Delete" button in `frontend/src/pages/RequestsPage.tsx` that
calls a new `deleteRequest(id)` function in `frontend/src/services/api.ts`
and removes that item from local state on success.

### 4. Add a filter to `GET /api/requests` (e.g. `?category=plumbing`)

In `backend/app/api/routes_requests.py`:

```python
@router.get("/requests", response_model=list[RequestOut])
def list_requests(
    category: Category | None = None,
    session: Session = Depends(get_session),
) -> list[RequestModel]:
    statement = select(RequestModel).order_by(RequestModel.created_at.desc())
    if category:
        statement = statement.where(RequestModel.category == category)
    return list(session.exec(statement).all())
```

On the frontend, add a `category` query param to `getRequests()` in
`api.ts` and a `<select>` filter control in `RequestsPage.tsx`.

### 5. Add a new field (e.g. `location`, a free-text room/area)

- `backend/app/models/request.py` — add
  `location: Optional[str] = Field(default=None, max_length=100)`.
- `backend/app/schemas/request.py` — add `location: str | None = None` to
  `RequestCreateIn` and `RequestOut`.
- `frontend/src/types/index.ts` — add `location?: string` to
  `SavedRequest`/`ClassifiedProblem`.
- Add an input field in `ProblemResultCard.tsx` and display it in
  `RequestsPage.tsx`.
- Since SQLite tables aren't auto-migrated for existing data, delete
  `backend/data/app.db` during a live demo (`Remove-Item backend/data/app.db`)
  so it's recreated with the new column — mention out loud that a real
  production system would use an Alembic migration instead.

## 25. Final Checklist

- [ ] Frontend works
- [ ] Backend works
- [ ] AI works (mock)
- [ ] Mock mode works
- [ ] API key protected (backend-only, git-ignored)
- [ ] SQLite works, auto-created on first run
- [ ] Multiple problems split correctly
- [ ] User can edit category before saving
- [ ] User can edit priority before saving
- [ ] Requests saved via `POST /api/requests`
- [ ] Requests displayed via `GET /api/requests`
- [ ] Responsive on desktop / tablet / mobile
- [ ] Error handling (empty input, AI failure, network failure, DB error)
- [ ] Tests written (`backend/tests/`) — run `pytest -v` to confirm
- [ ] README complete
- [ ] `.gitignore` excludes `.env`, `node_modules/`, `__pycache__/`, `*.db`
- [ ] Ready for `git init` → GitHub push

---

*Questions or issues while running this locally: re-check
[Section 6 (Requirements)](#6-requirements) and
[Section 7 (Installation)](#7-installation) first — most setup problems
are a missing PATH entry or a forgotten `.venv` activation.*
