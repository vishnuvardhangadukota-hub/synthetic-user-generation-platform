# Generative AI Powered Synthetic User Generation Platform (Backend)

Backend implementation for **Milestone 2 Task 2**: Synthetic User Research Concepts, LLM Persona Simulation Techniques, and Behavioral Modeling Architecture.

---

## Architecture Overview

```text
Client / Future Frontend
        │
        ▼
   FastAPI REST API (/api)
   ├── /api/experiments
   ├── /api/personas
   └── /api/conversations
        │
        ▼
   Service Layer (ExperimentService, PersonaService, MemoryService, LLMService)
        │
        ├──────────────────────┬──────────────────────┐
        ▼                      ▼                      ▼
Agent Layer             Memory Layer           Database Layer
(PersonaGenAgent)       (ConsistencyManager)   (SQLAlchemy ORM + SQLite)
        │                      │                      │
        └──────────────────────┴──────────────────────┘
                               │
                               ▼
                       LLM Provider / Dev Fallback
```

### Component Details:

1. **FastAPI REST API**: Exposes clean, versioned JSON endpoints (`/api/...`) with OpenAPI / Swagger documentation (`/docs`), request validation via Pydantic, CORS support, and standardized error handling.
2. **Service Layer**: Decouples business logic and ORM database transactions for experiments, personas, memories, and LLM providers.
3. **Agent Layer**: Hosts autonomous agents. Current implementation includes the `PersonaGenerationAgent` for generating diverse synthetic user personas using structured prompts and LLM integration.
4. **Memory Layer**: Enforces persona consistency across multi-turn interactions (`ConsistencyManager` & `PersonaMemoryManager`). Partitions memory into Core Memory (permanent profile), Behavioral Memory (habits/constraints), and Opinion Memory (opinions established during chat).
5. **Database Layer**: SQLite local development database managed via SQLAlchemy 2.0 ORM models, designed for easy PostgreSQL migration.
6. **LLM Provider Abstraction**: Clean provider interface (`LLMProvider`) supporting external APIs (e.g. OpenAI/Gemini) with a robust `DeterministicFallbackGenerator` when API keys are absent.

---

## Agent & Memory Architecture Roadmap

### Active Capabilities (Milestone 2 Task 2)
* **Persona Generation Agent (CURRENT)**: Generates diverse personas varying in demographics, personality traits, behavioral patterns, decision style, and psychological profiles based on product goals.
* **Persona Memory & Consistency Module (CURRENT)**: Tracks core traits, behavioral habits, and conversational opinions to ensure responses never contradict established context or background.

### Future Scope (Upcoming Milestones)
* **Survey Agent (FUTURE)**: Administers quantitative surveys to synthetic user panels.
* **Interview Agent (FUTURE)**: Conducts automated, open-ended user research interviews.
* **Insight Extraction Agent (FUTURE)**: Synthesizes patterns and thematic insights across multiple synthetic user responses.
* **Report Agent (FUTURE)**: Generates comprehensive product research reports and executive summaries.

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

### Memory & Conversation APIs
* `POST /api/personas/{persona_id}/conversation` - Interact with a persona (multi-turn conversation with memory consistency)
* `GET /api/personas/{persona_id}/memory` - Retrieve persona core memory, behavioral memories, opinions, and history

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
uvicorn app.main:app --reload
```

Interactive Swagger documentation is available at:
👉 **[http://localhost:8000/docs](http://localhost:8000/docs)**

---

## Running Tests

Execute the automated test suite with pytest:

```bash
pytest -v
```
