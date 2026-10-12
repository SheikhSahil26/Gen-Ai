# Common Goods frontend

A responsive React and Vite shopping assistant that uses the FastAPI backend for chat, cart totals, and order history. Components, API client, and hooks are separated under `src/components`, `src/api`, and `src/hooks`.

## Start

Start the backend at `http://localhost:8000`, then run:

```bash
cd frontend
npm install
npm run dev
```

Open <http://localhost:5173>. Vite proxies `/api` requests to the backend. To use another backend URL, copy `.env.example` to `.env` and set `VITE_API_BASE_URL`.

Chat calls `POST /api/v1/chat` with `message` and `conversation_id`. The cart and orders panels load from `GET /api/v1/cart` and `GET /api/v1/orders`. The conversation ID is retained in local storage so checkout confirmation can continue the same conversation after a page refresh while the backend process remains available.

When the assistant presents an order preview and asks for confirmation, the UI displays explicit **Confirm & place order** and **Cancel** actions. The confirmation action sends a clear affirmative message through the same chat conversation; the backend still enforces its human confirmation workflow.
