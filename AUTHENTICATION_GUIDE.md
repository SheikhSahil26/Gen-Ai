# Authentication Implementation Guide

This guide describes how to add account registration, sign-in, sign-out, and per-user authorization to the Common Goods application. It is based on the code in this repository and is intended to be followed as an implementation plan.

The guide does not modify or replace either project README. It also does not implement authentication code by itself.

## Recommended approach

Use **email/password authentication with Argon2id password hashes and opaque server-side sessions in secure cookies**.

This fits the existing FastAPI and PostgreSQL architecture. A server-side session is easy to revoke at logout and avoids putting reusable credentials in browser storage. The project already depends on `pwdlib[argon2]`, which can hash and verify passwords. A server-side session also means you do not need to add JWT signing, verification, rotation, and revocation logic for this first implementation.

For the deployed app, use the frontend and API on the same site, for example `app.example.com` and `api.example.com`. They are different origins, so CORS still applies, but they are same-site for cookie policy. If you use unrelated default hostnames such as `*.vercel.app` and `*.onrender.com`, browser third-party-cookie rules can interfere with cookie authentication. Consider a reverse proxy so the browser talks to one origin, or set up custom subdomains under the same domain.

```mermaid
sequenceDiagram
    actor Shopper
    participant Browser as React app
    participant API as FastAPI
    participant DB as PostgreSQL
    Shopper->>Browser: Register or sign in
    Browser->>API: POST /api/v1/auth/register or /login
    API->>DB: Find/create User; verify Argon2 password hash
    API->>DB: Store SHA-256 hash of random session secret
    API-->>Browser: Set HttpOnly Secure session cookie
    Browser->>API: Chat/cart/orders request with cookie
    API->>DB: Resolve session and active User
    API->>API: Use authenticated user ID for route and agent tools
    API-->>Browser: User-scoped response
```

## What exists today

- `models/user.py` already has `username`, `email`, and `hashed_password` columns.
- `pwdlib[argon2]` is already in the Python dependencies and the seed script uses `PasswordHash`.
- `auth/user_context.py` currently returns the fixed user ID `1`.
- Cart and order routes call `get_user_id()` without receiving an authenticated request user.
- Agent tools in `tools/shopping_tools.py` and `tools/order_tools.py` also call the fixed-ID helper directly.
- `api/routes/chat.py` has no authentication dependency.
- The frontend sends no credentials and has no sign-in or registration screen.
- The current `users` schema has no uniqueness constraints for email or username.

Authentication is incomplete until both direct HTTP routes **and** agent tools receive the authenticated user's ID. Protecting only the cart endpoint would still leave the chatbot able to read or change data under the fixed user identity.

## Target architecture

### User record

Keep the existing `users` table and add database-level uniqueness for normalized email and username. Normalize email by trimming whitespace and lowercasing before lookup or insert. Consider whether usernames should also be case-insensitive.

Never return `hashed_password` in API responses. Store only an Argon2id hash. Do not encrypt or log plaintext passwords. OWASP recommends adaptive password hashing such as Argon2id; FastAPI's current security tutorial uses `pwdlib` and PyJWT as supported building blocks. [OWASP Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html), [FastAPI security tutorial](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/)

### Session record

Add an `auth_sessions` table with fields similar to:

| Field | Purpose |
| --- | --- |
| `id` | Session row primary key |
| `user_id` | Foreign key to `users.id`, cascade delete |
| `token_hash` | Unique SHA-256 hash of the random session secret; never store the raw secret |
| `created_at` | Session creation time |
| `expires_at` | Absolute expiration time |
| `last_seen_at` | Optional recent-use tracking |
| `revoked_at` | Null while active; set on logout/revocation |

Generate a high-entropy random session token with Python's `secrets` module. Send the raw token only as a cookie, and save only its SHA-256 hash in PostgreSQL. Set a fixed session lifetime and expire/revoke inactive or old sessions according to a documented policy. A periodic cleanup task can delete expired rows later.

### Cookie settings

For production, set a cookie such as `__Host-cg_session` with:

- `HttpOnly`: browser JavaScript cannot read the secret.
- `Secure`: send it only over HTTPS.
- `SameSite=Lax`: reduce cross-site request forgery exposure.
- `Path=/`: required for the `__Host-` cookie prefix.
- No `Domain` attribute: keep it host-only.
- A bounded `Max-Age` matching session expiration.

For local HTTP development, `Secure` must be disabled through an explicit development setting. Never disable it in production. OWASP advises keeping session credentials out of `localStorage` and `sessionStorage`; those stores are readable by JavaScript running on the page. [OWASP Session Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html)

Cookie authentication needs CSRF protection for state-changing requests. Check the `Origin` header against the configured frontend origin on `POST`, `PUT`, `PATCH`, and `DELETE` requests. Keep `SameSite=Lax`, use an exact CORS allowlist, and add a CSRF token/header pattern if your deployment or cookie settings require it. CORS alone is not a CSRF defense.

## Step-by-step implementation

### Step 1 — Add uniqueness and session schema

1. Update `src/ecommerce_ai/models/user.py` so emails and usernames have database-backed uniqueness. Prefer unique indexes on normalized values, such as `lower(email)`, so `Person@example.com` and `person@example.com` cannot become separate accounts.
2. Before adding unique indexes, check the existing database for duplicates and resolve them deliberately. Do not silently delete user rows or their dependent orders.
3. Add an `AuthSession` model in a new file such as `src/ecommerce_ai/models/auth_session.py`. Include the fields above, a foreign key to `users`, and indexes for `token_hash`, `user_id`, and session expiration.
4. Export the new model from `models/__init__.py` so Alembic sees it.
5. Create a new Alembic revision. Review its upgrade and downgrade operations, then apply it to a development database with `uv run alembic upgrade head`.
6. Do not edit the already-applied initial migration to add authentication fields; add a new migration so existing databases can upgrade safely.

### Step 2 — Create authentication schemas and services

Create focused modules, for example:

```text
src/ecommerce_ai/auth/
    __init__.py
    passwords.py       # Argon2 hash and verify helpers
    sessions.py        # random token, cookie, expiry and revocation helpers
    dependencies.py    # get_current_user dependency
src/ecommerce_ai/schemas/auth.py
src/ecommerce_ai/services/auth.py
src/ecommerce_ai/api/routes/auth.py
```

Keep the route handlers small. Put user lookup, registration, password verification, session creation, and revocation in the service layer or repository layer, following the project's existing route/service/repository structure.

### Step 3 — Implement registration

`POST /api/v1/auth/register` should:

1. Validate username, email, and password with Pydantic.
2. Normalize username/email consistently.
3. Hash the password with Argon2id using `PasswordHash.recommended()` from `pwdlib`.
4. Insert the user, relying on database uniqueness to protect against simultaneous duplicate registrations.
5. Convert uniqueness conflicts into a safe client response. Do not return a traceback or database constraint details.
6. Create a session and set the session cookie, or require the newly registered user to sign in. Pick one behavior and document it.

For a public production service, add email verification and a password reset flow before relying on email addresses as verified identities. Rate-limit registration and login routes.

### Step 4 — Implement login, current-user lookup, and logout

Add these routes:

| Method | Path | Behavior |
| --- | --- | --- |
| `POST` | `/api/v1/auth/register` | Create an account |
| `POST` | `/api/v1/auth/login` | Verify credentials, create session, set cookie |
| `GET` | `/api/v1/auth/me` | Return the current user's safe public profile |
| `POST` | `/api/v1/auth/logout` | Revoke current session and clear cookie |

For login, use the same generic response for an unknown email and an incorrect password (for example, “Invalid email or password”) to avoid revealing which accounts exist. After verifying the password, generate a new random session token, store only its hash, and set the cookie.

`get_current_user` should read the cookie, hash its token, query for a matching non-revoked and unexpired session, load the linked user, and reject missing/invalid sessions with HTTP 401. It should return the `User` or a small authenticated-user object. The session's user ID—not a value sent by the browser—is the identity for all operations.

Logout should mark the database session revoked and clear the cookie using the same cookie name/path/security attributes. Return success even if the browser had no valid session, so logout can be safely retried.

### Step 5 — Replace the fixed ID with authenticated identity

Delete the fixed-ID behavior from `auth/user_context.py`; there must not be a fallback to user `1` if authentication is missing.

For direct API routes, add `current_user: User = Depends(get_current_user)` and use `current_user.id` for cart and order service calls. Keep product catalog access protected too if the requirement is that no part of the platform is usable before sign-in.

Agent tools need explicit identity injection. Do not let tools read a global fixed ID or accept `user_id` from the LLM as an argument. One straightforward fit for this project is:

1. Make `get_main_graph` depend on `get_current_user`.
2. Pass that user's ID to `build_graph(..., user_id=current_user.id)`.
3. Pass the ID into `create_shopping_tools(...)` and `create_order_tools(...)` when the graph is built.
4. Close over that trusted ID in each tool and pass it to the service. Remove calls to `get_user_id()` from the tools.
5. Continue using repository methods that filter rows by `user_id`; verify ownership again for order IDs, cart IDs, addresses, and any other object reference.

The top-level graph currently is created per API request by `get_main_graph`, so binding tools to the authenticated request's user ID fits its current construction pattern. Do not cache a user-bound graph globally where requests from different users could share it.

### Step 6 — Protect conversations as user data

The request currently accepts a `conversation_id` from the browser and uses it as the LangGraph thread ID. A user could guess or submit another thread ID unless the backend enforces ownership.

For this first implementation, namespace thread IDs on the server, for example `thread_id = f"user:{current_user.id}:{conversation_id}"`. Never trust a user ID or ownership value sent by the frontend. For durable production chat history, create a conversation table that stores `conversation_id` and `user_id`, validate ownership on every turn, and use a persistent checkpointer. The current `InMemorySaver` loses state on process restart; authentication does not change that limitation.

### Step 7 — Add the frontend authentication gate

1. Add sign-in and registration views.
2. On app startup, call `/api/v1/auth/me`. Render the storefront only after the user is authenticated; otherwise render the auth screen.
3. Add an auth provider or a small auth hook with `user`, `loading`, `login`, `register`, and `logout` state/actions.
4. Update `frontend/src/api/client.js` to send `credentials: "include"` on requests. The cookie is HttpOnly, so JavaScript should not read or save it.
5. On HTTP 401, clear client user state and show the sign-in screen.
6. On logout, reset chat and commerce state and clear the saved conversation. The current chat hook writes messages and conversation IDs to local storage; either stop persisting messages or scope/clear them by user so one account cannot see another account's browser history.
7. Keep sign-up/login forms accessible and show useful validation errors without echoing passwords.

### Step 8 — Configure CORS, cookie origin, and CSRF controls

Configure backend settings for the exact frontend origin, e.g. `https://app.example.com`. Since cookies are used, set `allow_credentials=True`; do not use wildcard origins. Add `credentials: "include"` to browser requests. FastAPI's CORS guide explains that credentialed requests require explicit origins, methods, and headers. [FastAPI CORS guide](https://fastapi.tiangolo.com/tutorial/cors/)

Require HTTPS in production. Validate `Origin` for state-changing browser requests, and implement a CSRF token/header if requests can originate from untrusted same-site subdomains or if cookie policy requires it. Keep local CORS origins under an explicit development configuration.

### Step 9 — Audit seed data and deployment secrets

The development seed script creates users with the password `password123` and truncates tables before seeding. Do not run it on a production database. Remove or rotate these accounts before any public deployment; if you retain them in an isolated demo database, label them as sample credentials and expect the records to be shared.

Do not commit `.env`, session secrets, database passwords, or password reset keys. With opaque DB-backed sessions there is no JWT signing secret, but cookie security still depends on HTTPS, safe session generation, and correct expiry/revocation. Log auth success/failure metadata without recording passwords, cookies, session tokens, or request authorization headers.

### Step 10 — Verify security and account isolation

Use two separate accounts and verify all of these behaviors:

| Scenario | Expected result |
| --- | --- |
| No cookie calls `/auth/me`, chat, cart, or orders | `401 Unauthorized` |
| Correct login | Cookie is set; `/auth/me` returns safe profile fields |
| Wrong password or unknown email | Same generic error; no cookie |
| Duplicate normalized email or username | Registration rejected without a server traceback |
| Password in database/API response | Only a password hash exists in DB; hash is never returned |
| User A reads cart/orders | Only User A's rows are returned |
| User A tries User B's order or conversation ID | Access denied or isolated to User A's own namespace |
| Logout then reuse old cookie | Request is rejected |
| Expired session | Request is rejected and cookie is cleared |
| Browser tries API from unapproved origin | CORS/Origin controls reject it |
| User A logs out on a shared browser | User A's saved client chat state is cleared |

Add backend tests for registration, login, session validation/revocation, unauthorized routes, and cross-user access. Add frontend coverage for the auth gate, expired session, and logout cleanup.

## Request flow after implementation

```text
Browser submits login
  → FastAPI validates credentials and checks Argon2id password hash
  → API stores hashed random session secret in auth_sessions
  → API sets HttpOnly Secure SameSite cookie

Browser calls chat/cart/orders with that cookie
  → get_current_user resolves session and loads User
  → route uses User.id directly
  → chat graph is built with that User.id bound into shopping/order tools
  → service/repository queries are scoped to the same User.id
  → API returns only that user's data
```

## Suggested implementation order

Build and verify each slice before moving to the next:

1. User uniqueness + `auth_sessions` model + Alembic migration.
2. Password service and registration/login/logout/`me` endpoints.
3. `get_current_user` dependency and unauthorized route behavior.
4. User ID propagation through chat graph and tool factories; remove the fixed ID.
5. Frontend auth gate and cookie-aware API client.
6. CORS, cookie, CSRF, session expiry, and account-isolation verification.
7. Only then deploy with a separate database and remove demo credentials.

## Primary references

- [FastAPI OAuth2 and password hashing guide](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/)
- [FastAPI CORS guide](https://fastapi.tiangolo.com/tutorial/cors/)
- [OWASP Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
- [OWASP Session Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
