# Production-Style Deployment Guide

This guide takes the current Common Goods project from local development to a public portfolio deployment. It aims for a sensible, recruiter-ready setup without introducing Kubernetes or a large cloud platform.

## Deployment target

The suggested layout is:

| Component | Hosting choice | Why |
| --- | --- | --- |
| React/Vite frontend | Vercel static site | Simple build and deploys from GitHub; preview links for changes |
| FastAPI backend | Render Web Service | Runs as a persistent Python process and gives the API a public HTTPS URL |
| PostgreSQL | Supabase managed Postgres | Managed database, separate from the application process |
| Support vector store | Qdrant Cloud | Hosted vector search; keeps support vectors outside the API container filesystem |
| Language model | Ollama Cloud API through its OpenAI-compatible endpoint | The deployed API cannot use an Ollama server on your laptop |

The application now connects to Qdrant. A one-time migration script copies documents from the local Chroma collection into a new Qdrant collection, re-embedding them with the existing embedding model. Keep one API instance for the first deployment because LangGraph conversation checkpoints are still in memory; Qdrant itself is hosted separately.

```mermaid
flowchart LR
    Browser --> Vercel[React static site]
    Vercel -->|HTTPS /api/v1| Render[FastAPI service]
    Render -->|PostgreSQL TLS| DB[(Supabase Postgres)]
    Render -->|HTTPS + API key| Qdrant[(Qdrant Cloud)]
    Render -->|HTTPS + API key| Ollama[Ollama Cloud model API]
```

## Read this before making it public

The current app is a demo, not a store ready for real customer data:

- `src/ecommerce_ai/auth/user_context.py` returns user ID `1` for every visitor. Anyone who can use a public deployment shares that demo identity, cart, and order history. Use only synthetic data and describe the site as a shared demo until real authentication and per-user authorization are implemented.
- `InMemorySaver` stores LangGraph conversation checkpoints in the API process. Restarts clear them; multiple API instances do not share them. Use one API instance for the first demo and expect conversations to reset after a restart or redeploy.
- The health endpoint only confirms that FastAPI responds. It does not test PostgreSQL, Qdrant, or the model.
- The Qdrant collection must exist and contain documents before the API starts. The migration script below creates/populates it from the local Chroma database.
- Do not connect the demo to real customer data, accept real payments, or use production credentials in the demo seed script. `scripts/seed.py` resets/truncates the configured database.

For the recruiter demo, create a separate database containing fake products, users, and orders. Add a visible “Demo data only” note in the deployed site/README. Before using this for real customers, authentication, conversation persistence, operational checks, and privacy/security review are release blockers.

## Step 1 — Prepare the source repository

The Python project root is the folder containing this file, `pyproject.toml`, and `uv.lock`. In your workspace it is the inner `ecommerce-multi-ai-agent-main` directory.

1. Check that `.env` is ignored and no API keys or database passwords are committed. The current `.gitignore` ignores `.env`.
2. Review your local changes before pushing. This checkout has other modified files and Chroma data; do not use `git add .` unless you have inspected every change and intend to publish it. Add only files you want in the deployment.
3. Push the intended project version to a GitHub repository. Vercel and Render will deploy from that repository.
4. Keep `uv.lock` committed so Render can reproduce the Python environment.

The source tree has no Dockerfile or Render Blueprint right now, so this guide uses dashboard-managed services and build/start commands.

## Step 2 — Make the model reachable from the deployed API

All current agents construct `ChatOllama(model="gpt-oss:120b-cloud", ...)` without a remote base URL. In deployment, this points at an Ollama server inside the Render service (normally `localhost:11434`), where no Ollama server is installed. The code will fail on the first chat request even if it works on your laptop.

For this deployment, use the Ollama Cloud API with its OpenAI-compatible endpoint. Ollama documents `https://ollama.com/v1` as the cloud OpenAI-compatible base URL and requires a cloud API key. [Ollama API introduction](https://github.com/ollama/ollama/blob/main/docs/api/introduction.mdx)

Before deployment, make a small model-provider change:

1. Add the LangChain OpenAI-compatible client dependency: `uv add langchain-openai`.
2. Add a shared model factory (for example, `src/ecommerce_ai/llm.py`) that creates the configured chat model using `ChatOpenAI`, `base_url="https://ollama.com/v1"`, `api_key` from the environment, and model name `gpt-oss:120b-cloud`.
3. Use that factory in `classifiers/intent_classifier.py` and the product, shopping, order, support, and unknown agents instead of constructing `ChatOllama` directly. Those agents need async invocation, and the commerce agents need tool calling, so confirm the selected Ollama model supports both through the compatibility API.
4. Run the classifier and one tool-using agent locally against the cloud API before proceeding.
5. Add the API key to Render as `OLLAMA_API_KEY`. Do not commit it or expose it in a Vite variable.

This is a required application change for a Render deployment. Do not deploy first and expect the local Ollama process on your PC to be reachable from Render.

## Step 3 — Create the managed PostgreSQL database

1. Create a Supabase project in a region near the API service.
2. In the database connection panel, copy a connection string suitable for a persistent backend. Supabase recommends a direct connection for a persistent backend when its network supports it; its session pooler is the alternative for an IPv4-only backend. Use the actual URL Supabase supplies rather than constructing the pooler hostname yourself. [Supabase connection guide](https://supabase.com/docs/guides/database/connecting-to-postgres)
3. Convert the scheme to the driver this app expects if necessary. The app uses Psycopg 3; it expects `postgresql+psycopg://...` (not a browser/frontend URL or Supabase anon key).
4. Keep the password private. You will enter the URL in Render's backend environment settings.

Do not expose the database port publicly if the provider offers network restrictions. Use TLS and take a backup before any schema changes.

## Step 4 — Create and populate the demo database

The schema is managed by Alembic. The first migration is in `alembic/versions/`.

1. Create an isolated database for this demo, not a database with real user data.
2. From the project root, set `DATABASE_URL` in a temporary PowerShell session to the new database URL and run:

   ```powershell
   $env:DATABASE_URL = "postgresql+psycopg://USER:PASSWORD@HOST:PORT/DATABASE"
   uv run alembic upgrade head
   ```

3. If you want demo catalog/orders, run the seed script only against this disposable database:

   ```powershell
   uv run python scripts/seed.py
   ```

   The seed script clears existing tables. Verify the URL carefully before running it.
4. Clear the temporary environment variable when finished:

   ```powershell
   Remove-Item Env:DATABASE_URL
   ```

You can also run migrations as a Render pre-deploy command on a plan that supports that feature. For the first deploy, applying the migration once from your development machine is easier to observe. Render documents pre-deploy commands for release tasks such as migrations. [Render deploys](https://render.com/docs/deploys)

## Step 5 — Create Qdrant and migrate Chroma

The local Chroma collection is `ecommerce_support` under `./data/chroma`. I checked this workspace and found 48 records in it. `scripts/migrate_chroma_to_qdrant.py` copies those records to Qdrant using the same `sentence-transformers/all-MiniLM-L6-v2` embeddings and stable point IDs. It does not delete or modify Chroma and refuses to overwrite a Qdrant collection that already exists.

1. Create a Qdrant Cloud cluster and copy its cluster URL and API key.
2. Add the following values to your local `.env` (keep the API key private):

   ```dotenv
   QDRANT_URL=https://YOUR-CLUSTER-URL
   QDRANT_API_KEY=YOUR_QDRANT_SECRET
   QDRANT_COLLECTION=ecommerce_support
   ```

3. From the project root, run the migration:

   ```powershell
   uv run python scripts/migrate_chroma_to_qdrant.py
   ```

   It should report 48 migrated documents. If the destination collection already exists, choose a new `QDRANT_COLLECTION` name and rerun; the script deliberately does not delete destination data.
4. Run the support retrieval check against Qdrant:

   ```powershell
   uv run python scripts/test_support_rag.py
   ```

   Confirm a support-policy query returns relevant passages. Keep the local Chroma directory as a rollback/source copy until the hosted app is verified.

If the collection has not been populated, use a one-time indexing script built from the existing `load_support_document()` and `split_support_documents()` functions. Do not re-index on every API request or each worker startup.

## Step 6 — Deploy the FastAPI backend to Render

1. Create a **Web Service** in Render and connect your GitHub repository.
2. Set **Root Directory** to the project folder containing `pyproject.toml` and `uv.lock`. If your Git repository root is the outer workspace, this may be `ecommerce-multi-ai-agent-main`.
3. Set the Python runtime to 3.13 or newer, matching `pyproject.toml`.
4. Use these commands:

   **Build command**

   ```bash
   uv sync --frozen --no-dev
   ```

   **Start command**

   ```bash
   uv run python -m uvicorn ecommerce_ai.main:app --app-dir src --host 0.0.0.0 --port $PORT
   ```

   Render supports `uv` when a `uv.lock` file is in the service root. [Render first deploy](https://render.com/docs/your-first-deploy)

5. Add backend environment variables in Render (Settings → Environment):

   | Variable | Value |
   | --- | --- |
   | `DATABASE_URL` | The isolated Supabase Postgres URL with `postgresql+psycopg://` scheme |
   | `QDRANT_URL` | Qdrant Cloud cluster URL |
   | `QDRANT_API_KEY` | Qdrant Cloud secret key |
   | `QDRANT_COLLECTION` | The collection populated in Step 5, e.g. `ecommerce_support` |
   | `OLLAMA_API_KEY` | The Ollama Cloud key used by your model factory |
   | `LANGSMITH_TRACING` | `false` unless you intentionally configure LangSmith |
   | `LANGSMITH_API_KEY` | Optional; only if tracing is enabled |
   | `LANGSMITH_PROJECT` | Optional project label, e.g. `common-goods-demo` |

   Environment variables are entered in the host dashboard and kept out of Git. [Render environment variables](https://render.com/docs/configure-environment-variables)

6. Set the health check path to `/health`. Remember this endpoint only checks that the API responds; it does not verify its dependencies.
7. Keep one backend instance while the in-memory LangGraph checkpointer is in use. Qdrant data is remote and does not need a Render disk.
8. Deploy. Check the build and runtime logs. Open `https://YOUR-API.onrender.com/health`; it should return `{"status":"ok","service":"ecommerce-agent-api"}`.
9. Open `https://YOUR-API.onrender.com/docs` and confirm the API docs load. You can disable public docs later by configuring FastAPI docs URLs.

## Step 7 — Allow the production frontend origin

The checked-in CORS middleware only allows `localhost:5173` and `127.0.0.1:5173`. A separately hosted frontend will be blocked by browsers until its exact origin is allowed.

Before deploying the frontend, add its production origin (for example `https://common-goods-demo.vercel.app`) to `allow_origins` in `src/ecommerce_ai/main.py`, deploy that API change, and include any Vercel preview origin only if you deliberately want preview deployments to access this demo API. Avoid a wildcard origin for a credentialed API.

## Step 8 — Deploy the React frontend to Vercel

1. Import the same GitHub repository into Vercel as a new project.
2. Set **Root Directory** to `frontend`.
3. Configure the build command as `npm run build`; output directory is `dist` (Vercel usually detects Vite automatically).
4. Add this environment variable for the Production environment:

   ```text
   VITE_API_BASE_URL=https://YOUR-API.onrender.com/api/v1
   ```

   `VITE_` variables are baked into the frontend build and visible in the browser. Only put the public API URL there, never a database password, model key, or Qdrant key.

5. Deploy. Vercel supports Vite and can create preview URLs for Git-based changes. [Vite on Vercel](https://vercel.com/docs/frameworks/frontend/vite)
6. Copy the final Vercel production origin and confirm it exactly matches the CORS origin deployed in Step 7.

## Step 9 — Verify the full deployed flow

Use only synthetic demo records. Check in this order:

1. `GET https://YOUR-API.onrender.com/health` returns HTTP 200.
2. Load the Vercel page. Check the browser console for CORS errors.
3. Search for a catalog item. Confirm the result comes from the seeded PostgreSQL catalog.
4. Add a result to the cart, then open/refresh the cart panel and verify totals.
5. Open the orders panel and confirm it shows the demo orders.
6. Ask a support-policy question. Confirm it retrieves policy passages from Qdrant; inspect Render logs if it times out or escalates unexpectedly.
7. Start checkout and verify it shows an order preview. Confirm only through the explicit approval button and verify an order is created in the demo database.
8. Send a second message with the same conversation and verify the thread works. Restart/redeploy the API once and note that the in-memory checkpoint is expected to be lost.
9. Check Render logs for database/model errors and Vercel logs for build errors. Never paste secret values into logs or screenshots.

## Step 10 — Make the deployment recruiter-ready

- Add the live frontend URL and backend API/docs links to the original README or portfolio page (do not replace existing project documentation).
- Include a short screen recording showing product search, cart, checkout confirmation, order lookup, and policy support.
- Add a visible “Demo data only” label and sample prompts.
- Explain the architecture and limitations honestly: shared demo identity, in-memory chat checkpoint, Qdrant Cloud support retrieval, and no real payment provider.
- Keep a staging/demo database separate from any personal or production data.
- Review service usage and billing after the first day. Hosted LLM calls and managed compute/database plans may incur charges.

## When to call it production-ready

This deployment is production-shaped infrastructure suitable for a portfolio demo. Do not call it ready for real shoppers until you have implemented and verified at least:

1. Authentication plus per-user authorization (replace the fixed user ID).
2. Persistent LangGraph checkpoints (PostgreSQL saver or another shared store).
3. A repeatable support-policy indexing process, with clear update/version handling for the Qdrant collection.
4. Dependency-aware readiness checks and request/error monitoring.
5. Rate limits, data-retention decisions, and a real payment provider with server-side verification if checkout is to charge money.
6. Automated release checks, tested migrations, backups, and a rollback procedure.

## Links to platform documentation

- [Render FastAPI deployment](https://render.com/docs/deploy-fastapi)
- [Render monorepo/root-directory deployment settings](https://render.com/docs/your-first-deploy)
- [Qdrant LangChain integration](https://qdrant.tech/documentation/frameworks/langchain/)
- [Render health checks](https://render.com/docs/health-checks)
- [Supabase Postgres connection methods](https://supabase.com/docs/guides/database/connecting-to-postgres)
- [Vite on Vercel](https://vercel.com/docs/frameworks/frontend/vite)
- [Ollama API and cloud model access](https://github.com/ollama/ollama/blob/main/docs/api/introduction.mdx)
