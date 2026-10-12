# Multi-Agent E-Commerce Assistant

An e-commerce shopping assistant that lets a customer search a product catalog, manage a cart or wishlist, check orders, and ask support questions in one natural-language conversation. A React storefront chat sends each message to a FastAPI API; a LangGraph supervisor classifies the request and delegates work to focused agents that use the application database and, for support questions, a retrieval-augmented knowledge base.

The repository includes both the web interface and backend. The UI is branded **Common Goods**.

<p align="center">
  <img src="docs/images/product-results-ui.jpg" alt="Common Goods assistant showing product search results beside the shopping bag" width="100%" />
</p>

<p align="center"><em>Product search results and the shopping bag are available side by side.</em></p>

## Contents

- [What it does](#what-it-does)
- [How a request flows](#how-a-request-flows)
- [Agent orchestration](#agent-orchestration)
- [Technology stack](#technology-stack)
- [Screenshots](#screenshots)
- [Repository layout](#repository-layout)
- [Run locally](#run-locally)
- [API overview](#api-overview)
- [Configuration](#configuration)
- [Current implementation notes](#current-implementation-notes)

## What it does

The assistant is designed to make common store tasks feel like a conversation instead of a set of separate forms. A shopper can ask a question such as “Find me a gaming laptop under ₹70,000,” then continue with “Add the second one to my cart.” The backend identifies the task, calls the relevant agent, and grounds catalog and commerce answers in application data.

Current capabilities include:

- **Product discovery:** search and list catalog items, retrieve product details, check stock, and compare products.
- **Shopping:** view and update the cart, manage quantities, remove items, and use a wishlist.
- **Orders:** inspect order history and details, track shipments, and access order actions supported by the order service. Checkout previews require an explicit confirmation in the UI.
- **Customer support:** retrieve relevant passages from the support policy, validate whether the material can answer the question, and escalate when it cannot be resolved confidently.
- **Conversation continuity:** the frontend keeps a conversation ID and sends it with later messages; the API uses it as the LangGraph thread ID.
- **Commerce panels:** review cart totals and order history beside the chat.

## How a request flows

```mermaid
sequenceDiagram
    actor Shopper
    participant UI as React / Vite UI
    participant API as FastAPI chat endpoint
    participant Graph as LangGraph supervisor
    participant Agent as Specialist agent
    participant Data as PostgreSQL / support knowledge

    Shopper->>UI: Send a natural-language message
    UI->>API: POST /api/v1/chat (message, conversation_id)
    API->>Graph: Invoke graph with HumanMessage and thread_id
    Graph->>Graph: Classify intents and build ordered task queue
    loop Each planned task
        Graph->>Agent: Route current task to specialist
        Agent->>Data: Call tools / retrieve support passages
        Data-->>Agent: Catalog, cart, order, or policy results
        Agent-->>Graph: Add answer and complete task
    end
    Graph-->>API: Final assistant message and intent metadata
    API-->>UI: JSON response with same conversation_id
    UI-->>Shopper: Render reply and refresh commerce panels
```

At a high level, the request moves through these stages:

1. The chat UI sends the message and its conversation ID to `POST /api/v1/chat`.
2. The API creates a LangGraph state containing the user message and invokes the graph using that ID as the thread key.
3. The intent classifier returns one or more intents. The classifier preserves the user's requested order where possible; the graph turns those intents into a task queue.
4. The supervisor selects the first queued task and routes to the matching worker. Each worker can call its tools and application services before returning a response.
5. The worker marks the task complete and returns control to the supervisor. The supervisor repeats until the queue is empty.
6. The API returns the latest assistant message, conversation ID, primary intent, and classifier confidence. The UI renders the response and refreshes the cart and order panels.

## Agent orchestration

The top-level graph is built in `src/ecommerce_ai/graph/graph.py`. It has a classifier, a supervisor, and five possible workers. Multi-intent requests can therefore pass through more than one worker in sequence, using shared conversation messages and graph state.

```mermaid
flowchart TD
    U[Incoming user message] --> C[Intent classifier<br/>Ollama structured output]
    C --> Q[Create ordered task queue]
    Q --> S[Supervisor selects next task]
    S -->|product| P[Product agent]
    S -->|shopping| H[Shopping agent]
    S -->|order| O[Order agent]
    S -->|support| SU[Support agent]
    S -->|unknown| UN[Clarification agent]
    P --> S
    H --> S
    O --> S
    SU --> S
    UN --> S
    S -->|queue empty| E[Return final response]

    P -. tools .-> DB[(PostgreSQL catalog)]
    H -. tools .-> DB
    O -. tools .-> DB
    SU -. retrieve policy .-> V[(Chroma support index)]
```

Each specialist is itself a small LangGraph workflow:

| Agent | Example responsibilities | Data / tools |
| --- | --- | --- |
| **Product** | Search products, list the catalog, explain details, check availability, compare options | Product services and PostgreSQL-backed product tools |
| **Shopping** | View or modify cart and wishlist | Shopping and product services, PostgreSQL-backed tools |
| **Order** | Review past orders, look up order details, track shipments, perform supported order actions | Order service and PostgreSQL-backed tools |
| **Support** | Understand a support request, retrieve policy passages, validate grounding, answer or escalate | Support policy, Hugging Face sentence embeddings, Chroma vector store, Ollama model |
| **Unknown** | Respond when a request does not map cleanly to a supported commerce intent | Dedicated unknown-request agent |

Product, shopping, and order agents use a model/tool loop: the model decides whether it needs a tool, the tool runner executes the call, and the model receives the result before answering. The support graph follows a retrieval and validation path: understand the query → retrieve policy → validate relevance → answer and validate, or escalate.

## Technology stack

| Area | Technology | How it is used |
| --- | --- | --- |
| Frontend | React 18, JavaScript, Vite | Single-page shopping assistant, chat, cart and order views, local dev server and API proxy |
| UI utilities | `lucide-react`, `react-markdown`, `remark-gfm` | Icons and Markdown rendering in assistant messages |
| Backend API | Python 3.13+, FastAPI, Uvicorn | Async HTTP API, health endpoint, chat and commerce routes |
| Agent orchestration | LangGraph, LangChain Core | Typed graph state, supervisor routing, specialist subgraphs, message and tool handling |
| Language model | Ollama via `langchain-ollama`, `gpt-oss:120b-cloud` | Intent classification and specialist reasoning / tool selection |
| Structured data | PostgreSQL, SQLAlchemy async, Psycopg 3 | Products, variants, carts, orders, users, support records, and related application data |
| Schema migrations | Alembic | Versioned relational schema migrations |
| Retrieval-augmented support | Chroma, LangChain Chroma, Hugging Face `sentence-transformers/all-MiniLM-L6-v2` | Persist support-policy vectors locally and retrieve relevant passages for support responses |
| Settings | Pydantic Settings, `python-dotenv` | Load database and optional LangSmith values from environment / `.env` |
| Observability | LangSmith (optional) | Trace LangChain runs when configured with a key; tracing setting defaults to enabled |
| Development | `uv`, npm, pytest | Python environment and dependency management, frontend packages, repository test suite |

## Screenshots

These screenshots are stills from the repository's `demo-video/` recording. They show the real frontend rather than a mockup.

### Product discovery

The assistant returns a structured catalog comparison with price, discount, and stock details, while the current bag remains visible.

![A shopper views laptops in a product results table while the bag panel stays open](docs/images/product-results-ui.jpg)

### Order and purchase history

The assistant can answer purchase-history questions in the chat using order data.

![Purchase history response in the Common Goods shopping assistant](docs/images/order-history-ui.jpg)

### Cart beside the conversation

The commerce panel shows selected products, quantities, savings, and the estimated total.

![Chat and shopping bag panel in the Common Goods UI](docs/images/chat-and-cart-ui.jpg)

## Repository layout

```text
.
├── frontend/                         # React + Vite client
│   └── src/
│       ├── api/                      # HTTP client for chat, cart, and orders
│       ├── components/
│       │   ├── chat/                 # Conversation, composer, checkout approval
│       │   ├── commerce/             # Cart and orders panels
│       │   ├── layout/               # App shell, sidebar, top bar
│       │   └── shared/               # Shared visual components
│       ├── hooks/                    # Chat and commerce state / API hooks
│       ├── utils/                    # Checkout and display helpers
│       ├── App.jsx                   # UI composition and panel state
│       └── styles.css                # Application styles
├── src/ecommerce_ai/
│   ├── agents/                       # Product, shopping, order, support, unknown agents
│   ├── api/                          # FastAPI routers, dependencies, and routes
│   ├── auth/                         # Current development user context
│   ├── classifiers/                  # Multi-intent classifier
│   ├── config/                       # Environment-backed settings
│   ├── db/                           # Async SQLAlchemy engine and base
│   ├── graph/                        # Shared state, supervisor, routing, main graph
│   ├── memory/                       # In-memory LangGraph checkpointer
│   ├── models/                       # SQLAlchemy database models
│   ├── rag/                          # Support document loading, embeddings, Chroma retrieval
│   ├── repositories/                 # Database access layer
│   ├── schemas/                      # Pydantic request and response schemas
│   ├── services/                     # Product, shopping, order, and support operations
│   ├── tools/                        # Agent-callable functions and tool runner
│   └── main.py                       # FastAPI application and lifespan
├── src/multi_ai_agent/               # Python package entry point
├── alembic/                          # Database migration environment and revisions
├── data/chroma/                      # Local persistent Chroma data directory
├── docs/images/                      # README UI screenshots
├── knowledge/support/                # Source support policy for retrieval
├── scripts/                          # Seed, inspection, and manual development scripts
├── tests/                            # Pytest tests
├── .env.example                      # Backend environment template
├── langgraph.json                    # LangGraph CLI configuration
├── pyproject.toml                    # Python project and uv dependencies
└── requirements.txt                  # Broad pip dependency list
```

`frontend/node_modules`, build output, Python virtual environments, caches, and generated runtime files are intentionally omitted from the layout above.

## Run locally

### Prerequisites

- Python **3.13 or newer**
- [`uv`](https://docs.astral.sh/uv/) for the backend environment
- Node.js and npm for the frontend
- PostgreSQL
- Ollama configured to serve `gpt-oss:120b-cloud` (this project uses that model name in its agents)

### 1. Configure the backend

From the repository root, create a local environment file and update its database URL:

```bash
cp .env.example .env
```

Set `DATABASE_URL` to a reachable PostgreSQL database. For example:

```dotenv
DATABASE_URL=postgresql+psycopg://postgres:password@localhost:5432/multi_ai_agent
```

Install the Python project and apply the database migrations:

```bash
uv sync
uv run alembic upgrade head
```

For a local demo, the repository includes `scripts/seed.py`:

```bash
uv run python scripts/seed.py
```

**The seed script truncates all tables in the configured database before inserting demo rows. Use it only with a disposable development database.**

Ensure Ollama is running and the configured model is available before sending a chat request. The support agent also loads the sentence-transformer embedding model and the support policy from `knowledge/support/support_policy.md`; the local Chroma store lives under `data/chroma/`.

### 2. Start the API

From the repository root:

```bash
uv run uvicorn ecommerce_ai.main:app --app-dir src --reload
```

The API is available at `http://localhost:8000`. Check `http://localhost:8000/health` or open the interactive API docs at `http://localhost:8000/docs`.

### 3. Start the frontend

In another terminal:

```bash
cd frontend
npm install
npm run dev
```

Open [`http://localhost:5173`](http://localhost:5173). Vite proxies `/api` requests to `http://127.0.0.1:8000`. To target a different backend, copy `frontend/.env.example` to `frontend/.env` and set `VITE_API_BASE_URL`.

### Example requests

- “Show me laptops under ₹70,000.”
- “Compare the Lenovo and ASUS gaming laptops.”
- “Add the first laptop to my cart and show me the total.”
- “Where is my latest order?”
- “What is your return policy?”

When the assistant presents an order preview, review it and use the UI's **Confirm & place order** or **Cancel** action. The confirmation is sent as a follow-up in the same conversation.

## API overview

The frontend uses the versioned API base path `/api/v1`.

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Service health check |
| `POST` | `/api/v1/chat` | Send a message to the agent graph |
| `GET` | `/api/v1/cart` | Return cart contents and INR totals |
| `GET` | `/api/v1/orders?limit=20` | Return recent order history |

Example chat request:

```json
{
  "message": "Show me laptops under 70000",
  "conversation_id": "optional-stable-conversation-id"
}
```

If `conversation_id` is omitted, the server creates one. The response includes `message`, `conversation_id`, `intent`, and `intent_confidence`; pass the returned ID on subsequent turns to continue that conversation.

## Configuration

| Variable | Required | Description |
| --- | --- | --- |
| `DATABASE_URL` | Yes | PostgreSQL connection URL using the Psycopg driver, e.g. `postgresql+psycopg://...` |
| `LANGSMITH_TRACING` | No | Enable or disable LangSmith tracing; defaults to `true` |
| `LANGSMITH_API_KEY` | No | LangSmith API key for sending traces |
| `LANGSMITH_PROJECT` | No | Trace project name; defaults to `multi-ai-agent` |
| `LANGSMITH_ENDPOINT` | No | LangSmith endpoint; defaults to `https://api.smith.langchain.com` |
| `VITE_API_BASE_URL` | No | Frontend API base URL; otherwise frontend uses Vite's `/api` proxy |

`LANGCHAIN_TRACING_V2`, `LANGCHAIN_API_KEY`, `LANGCHAIN_PROJECT`, and `LANGCHAIN_ENDPOINT` aliases are also accepted by backend settings. Keep credentials in local environment files and out of source control.

## Current implementation notes

- The chat thread checkpointer is **in memory**. A conversation can continue while the API process is running, but its checkpoint is lost when the process restarts.
- `src/ecommerce_ai/auth/user_context.py` currently returns a fixed development user ID (`1`). The auth module describes JWT-based identity as future work; the included endpoints should be treated as a local/demo setup rather than production authentication.
- The support agent grounds answers in the policy document stored at `knowledge/support/support_policy.md`; it is not a general-purpose web search.
- The default model identifier is `gpt-oss:120b-cloud` through Ollama. Model access and any Ollama account/provider setup are outside this repository.
- LangSmith is optional. Add an API key if you want traces in your own LangSmith project.

## Development

The Python project declares its runtime dependencies in `pyproject.toml` and the frontend in `frontend/package.json`. The repo also contains tests under `tests/` and several manual scripts under `scripts/` for local development and inspection.

```bash
# Backend test suite
uv run pytest

# Frontend production build
cd frontend && npm run build
```

---

Built as a practical demonstration of a tool-using, multi-agent e-commerce workflow with a conversational storefront interface.
