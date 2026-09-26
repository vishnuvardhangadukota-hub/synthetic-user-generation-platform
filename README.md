# Generation of AI Powered Synthetic Users for Product Research

A Generative AI-powered Synthetic User Generation Platform for product research, persona simulation, survey execution, interview roleplaying, insight extraction, and product usage scoring.

---

## 🌟 Overview

The platform enables product researchers, designers, and managers to define a product, target audience, and research objectives. The system generates diverse synthetic user personas with consistent demographic, behavioral, personality, and psychological characteristics, executes automated surveys, conducts multi-turn interview conversations, synthesizes qualitative insights, and computes product adoption scoring.

---

## 🏗️ System Architecture

```text
Client / Future Frontend
        │
        ▼
   FastAPI REST API (/api)
   ├── /api/experiments
   ├── /api/personas
   ├── /api/surveys
   ├── /api/insights
   └── /api/usage-score
        │
        ▼
   Service Layer (Experiment, Persona, Memory, Survey, Insight, UsageScore, LLM Services)
        │
        ├──────────────────────┬──────────────────────┐
        ▼                      ▼                      ▼
Agent Layer             Memory Layer           Database Layer
(PersonaGenAgent,       (ConsistencyManager,   (SQLAlchemy ORM + SQLite)
 InsightExtractionAgent) PersonaMemoryManager)
        │                      │                      │
        └──────────────────────┴──────────────────────┘
                               │
                               ▼
                       LLM Provider / Dev Fallback
```

---

## 🚀 Key Features

* **Experiment Workspace**: Create, manage, and configure product research experiments.
* **Persona Generation Agent**: Automatically generates realistic and diverse synthetic user personas across demographics, occupations, behavioral patterns, price sensitivities, and decision-making styles.
* **Survey Mode**: Define surveys and questions (rating, yes/no, short-answer, opinion, open-ended), run surveys across all experiment personas, and view side-by-side response comparisons.
* **Interview Mode**: Interactive multi-turn conversations with personas while preserving persona core traits, background habits, and established opinions to prevent contradictions.
* **Insight Extraction Agent**: Analyzes stored survey and interview responses to extract recurring themes, sentiment distributions, agreement/disagreement patterns, behavioral trends, supporting response references, and simulation disclaimers.
* **Product Usage Scoring**: Calculates persona product adoption likelihood ("Would Use This Product"), aggregates scores across demographic/behavioral segments (age, occupation), and discloses transparent calculation methodology and limitations.
* **LLM Abstraction & Fallback**: Modular interface supporting OpenAI/Gemini/Custom LLMs with an automatic `DeterministicFallbackGenerator` for keyless local development.
* **REST API & Swagger Documentation**: Independent FastAPI backend exposing REST APIs and live interactive Swagger documentation at `/docs`.

---

## 📁 Repository Structure

```text
.
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI Application Entrypoint & Middleware
│   │   ├── config.py            # Environment Configuration
│   │   ├── api/
│   │   │   └── routes/          # REST API Route Controllers
│   │   │       ├── experiments.py
│   │   │       ├── personas.py
│   │   │       ├── conversations.py
│   │   │       ├── surveys.py
│   │   │       ├── insights.py
│   │   │       └── analytics.py
│   │   ├── agents/
│   │   │   ├── persona_generation_agent.py
│   │   │   └── insight_extraction_agent.py
│   │   ├── memory/              # Persona Memory & Consistency Module
│   │   │   ├── persona_memory.py
│   │   │   └── consistency_manager.py
│   │   ├── models/              # SQLAlchemy Database Models
│   │   ├── schemas/             # Pydantic Schemas & Data Validators
│   │   ├── services/            # Business & DB Service Layer
│   │   ├── database/            # Database Connection & Session Management
│   │   └── utils/               # Prompts & Response Validation Utilities
│   │
│   ├── tests/                   # Pytest Backend Test Suite
│   ├── requirements.txt         # Python Package Dependencies
│   ├── .env.example             # Environment File Template
│   └── README.md                # Detailed Backend Technical Docs
└── README.md                    # Project Root Documentation
```

---

## ⚡ Quick Start Guide

### 1. Prerequisites
- Python 3.11+
- Pip package manager

### 2. Installation & Setup

```bash
# Navigate to the backend directory
cd backend

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
```

*(Note: Setting `LLM_API_KEY` in `.env` is optional. If omitted, the system seamlessly uses the local `DeterministicFallbackGenerator`.)*

### 3. Run Application Server

```bash
python -m uvicorn app.main:app --reload
```

Interactive Swagger API documentation will be available at:
👉 **[http://localhost:8000/docs](http://localhost:8000/docs)**

---

## 🧪 Running Tests

Execute the backend test suite:

```bash
cd backend
python -m pytest -v
```

---

## 📄 License

This project is licensed under the MIT License.
