# Generative AI Powered Synthetic User Generation Platform (Backend)

Complete backend implementation for **Milestone 2** & **Milestone 3**: Synthetic User Research Concepts, LLM Persona Simulation, Survey Mode, Multi-Turn Interviews, Insight Extraction, and Product Usage Scoring.

---

## Architecture Overview

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

### Component Details:

1. **FastAPI REST API**: Exposes versioned REST JSON endpoints (`/api/...`) with OpenAPI / Swagger documentation (`/docs`), request validation via Pydantic, CORS support, and standardized error handling.
2. **Service Layer**: Decouples business logic and ORM database transactions for experiments, personas, memories, surveys, insights, usage scores, and LLM providers.
3. **Agent Layer**:
   - `PersonaGenerationAgent`: Generates diverse synthetic user personas using structured prompts and LLM integration.
   - `InsightExtractionAgent`: Analyzes stored survey and interview responses to extract recurring themes, sentiment distribution, agreement/disagreement patterns, behavioral trends, supporting references, and limitations.
4. **Memory Layer**: Enforces persona consistency across multi-turn interactions (`ConsistencyManager` & `PersonaMemoryManager`). Partitions memory into Core Memory (permanent profile), Behavioral Memory (habits/constraints), and Opinion Memory (opinions established during chat).
5. **Database Layer**: SQLite local development database managed via SQLAlchemy 2.0 ORM models (`experiments`, `personas`, `persona_memories`, `conversations`, `surveys`, `survey_questions`, `survey_responses`, `insight_reports`, `usage_score_reports`).
6. **LLM Provider Abstraction**: Clean provider interface (`LLMProvider`) supporting external APIs (e.g. OpenAI/Gemini) with a robust `DeterministicFallbackGenerator` when API keys are absent.

---

## API Reference

### Experiment Workspace APIs
* `POST /api/experiments` - Create a research experiment
* `GET /api/experiments` - List all experiments
* `GET /api/experiments/{experiment_id}` - Get experiment details
* `PUT /api/experiments/{experiment_id}` - Update experiment
* `DELETE /api/experiments/{experiment_id}` - Delete experiment

### Persona APIs
* `POST /api/experiments/{experiment_id}/personas/generate` - Generate synthetic personas
* `GET /api/experiments/{experiment_id}/personas` - List experiment personas
* `GET /api/personas/{persona_id}` - Get persona details
* `DELETE /api/personas/{persona_id}` - Delete persona

### Survey Mode APIs
* `POST /api/experiments/{experiment_id}/surveys` - Create a survey for an experiment
* `GET /api/experiments/{experiment_id}/surveys` - List all surveys for an experiment
* `POST /api/surveys/{survey_id}/questions` - Add a question to a survey (rating, yes_no, short_answer, opinion, open_ended)
* `POST /api/surveys/{survey_id}/run` - Execute survey across all experiment personas using persona attributes & memory
* `GET /api/surveys/{survey_id}/responses` - Get survey responses grouped by question for side-by-side persona comparison

### Interview & Memory APIs
* `POST /api/personas/{persona_id}/conversation` - Interact with a persona (multi-turn conversation with memory consistency)
* `GET /api/personas/{persona_id}/memory` - Retrieve persona core memory, behavioral memories, opinions, and history

### Insight Extraction APIs
* `POST /api/experiments/{experiment_id}/insights` - Synthesize survey & interview responses into a structured insight report
* `GET /api/experiments/{experiment_id}/insights` - Get the latest generated insight report for an experiment

### Product Usage Scoring APIs
* `POST /api/experiments/{experiment_id}/usage-score` - Evaluate "Would Use This Product" scores, adoption %, and segment breakdowns (age, occupation)
* `GET /api/experiments/{experiment_id}/usage-score` - Get the latest usage score report for an experiment

---

## Quick Start & Local Execution

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Environment Configuration

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

*(Optional: Set `LLM_API_KEY` in `.env`. If omitted, the backend automatically uses the `DeterministicFallbackGenerator`.)*

### 3. Run Application Server

```bash
python -m uvicorn app.main:app --reload
```

Interactive Swagger documentation is available at:
👉 **[http://localhost:8000/docs](http://localhost:8000/docs)**

---

## Running Tests

Execute the full automated test suite with pytest:

```bash
python -m pytest -v
```
