# CREST

> High-performance athletic fitness landing page — decoupled SPA (FastAPI + Tailwind).

```
crest/
├── backend/          # FastAPI + SQLAlchemy + JWT/Argon2 + SlowAPI
│   ├── app/
│   │   ├── api/      # Routers (auth, catalog, checkout, contact)
│   │   ├── core/     # config, database, security, limiter
│   │   ├── models/   # SQLAlchemy models
│   │   ├── schemas/  # Pydantic v2 schemas
│   │   ├── crud/     # database access
│   │   ├── middleware/
│   │   ├── catalog.py
│   │   └── main.py
│   ├── alembic/      # migrations
│   ├── requirements.txt
│   └── .env.example
├── frontend/         # Decoupled SPA — Tailwind CDN + vanilla JS modules
│   ├── index.html
│   ├── css/styles.css
│   ├── js/
│   │   ├── config.js   # runtime config (API URL, etc.)
│   │   ├── api.js      # fetch wrapper + token storage
│   │   ├── auth.js     # login/register state
│   │   ├── i18n.js     # AR/EN translations + RTL
│   │   ├── theme.js    # dark / light + OS detection
│   │   ├── ui.js       # drawer / modal / toast / smooth scroll
│   │   └── main.js     # boot + render + checkout flow
│   └── locales/{en,ar}.json
└── scripts/
    ├── run-backend.sh
    ├── run-frontend.sh
    └── hash-password.sh
```

## Quick start (development)

### 1. Database (MySQL)

```sql
CREATE DATABASE crest CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'crest'@'localhost' IDENTIFIED BY 'crest_secret';
GRANT ALL PRIVILEGES ON crest.* TO 'crest'@'localhost';
FLUSH PRIVILEGES;
```

### 2. Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env                  # then edit secrets / DB creds
alembic upgrade head                  # or let the dev startup create tables
uvicorn app.main:app --reload --port 8000
```

Open `http://localhost:8000/api/docs` for the interactive Swagger UI.

### 3. Frontend

```bash
cd frontend
python3 -m http.server 5500
```

Open `http://localhost:5500`. The API base URL is `http://localhost:8000/api/v1` by default — override in `frontend/js/config.js` if needed.

### Or, use the helper scripts

```bash
./scripts/run-backend.sh    # creates venv, installs deps, runs uvicorn
./scripts/run-frontend.sh   # serves SPA on :5500
```

## Architecture

| Layer       | Tech                                                          |
| ----------- | ------------------------------------------------------------- |
| Backend     | FastAPI 0.115, Pydantic 2, SQLAlchemy 2, MySQL 8 (PyMySQL)    |
| Auth        | OAuth2 Bearer + JWT (HS256). Argon2id password hashing.       |
| Rate limit  | SlowAPI (default 120/min, auth 10/min, contact 5/min)         |
| Frontend    | HTML5, Tailwind (CDN), vanilla JS modules, Google Fonts      |
| Localization| AR / EN JSON dictionaries, full RTL support, auto-detect    |
| Themes      | Dark (default) / Light, OS-preference auto-detect, persisted  |

## Security checklist

- **Pydantic validation** on every request body.
- **Argon2id** hashing via `passlib` (configurable to bcrypt in `app/core/security.py`).
- **JWT** access (30 min) + refresh (14 days) tokens; `type` claim prevents substitution.
- **HttpOnly + SameSite=Lax** cookies for tokens (in addition to JSON body).
- **CORS** restricted to configured frontend origins via `FRONTEND_ORIGINS`.
- **CSP / HSTS / X-Frame-Options / Referrer-Policy / Permissions-Policy** security headers.
- **Rate limiting** via `slowapi` on auth + contact endpoints to mitigate brute force and spam.
- **SQL injection** prevented — all queries use SQLAlchemy parameterized expressions.
- **XSS prevention** — `bleach` sanitization on contact payloads; HTML escaping on every render.
- **Generic error messages** on auth (no user enumeration).
- **Trusted host middleware** as defense-in-depth.

## Endpoints

All endpoints are versioned under `/api/v1`.

| Method | Path                          | Auth | Description                                |
| ------ | ----------------------------- | ---- | ------------------------------------------ |
| GET    | `/health`                     | —    | Liveness probe                             |
| POST   | `/auth/register`              | —    | Create account, return token pair          |
| POST   | `/auth/login`                 | —    | Email + password → token pair              |
| POST   | `/auth/refresh`               | —    | Exchange refresh token for a new access    |
| POST   | `/auth/logout`                | —    | Clear auth cookies                         |
| GET    | `/auth/me`                    | ✅   | Current user profile                       |
| PATCH  | `/auth/me`                    | ✅   | Update profile (name, language)            |
| POST   | `/auth/me/password`           | ✅   | Change password                            |
| GET    | `/programs`                   | —    | List training programs                     |
| GET    | `/programs/{id}`              | —    | Single program                             |
| GET    | `/packs`                      | —    | List subscription packs                    |
| GET    | `/packs/{id}`                 | —    | Single pack                                |
| POST   | `/checkout`                   | ✅   | Create a checkout session                  |
| POST   | `/contact`                    | —    | Submit contact / support message           |

Open `http://localhost:8000/api/docs` for live try-it-out.

## Frontend architecture

The SPA is intentionally framework-free — every concern is isolated in a
single-file ES module that attaches itself to `window.CREST_*`.

- **`config.js`** — runtime config (API base URL, storage keys).
- **`api.js`** — fetch wrapper. Centralizes JSON parsing, Authorization header, 401 → `auth:logout` event.
- **`auth.js`** — login/register state. Persists the user in `localStorage`, refreshes on boot.
- **`i18n.js`** — fetches `locales/{lang}.json`, applies `[data-i18n]` attributes, swaps `<html dir>`.
- **`theme.js`** — toggles `html.light`, syncs label, respects OS preference until the user overrides.
- **`ui.js`** — drawer, modal, toast, smooth scroll, IntersectionObserver nav highlight.
- **`main.js`** — boots the rest, renders programs/packs, wires checkout → auth → checkout flow, contact form.

### Checkout flow

1. User clicks "Select" on a program or "Choose" on a pack.
2. If the user is **not** authenticated, the SPA stashes the pending selection in `sessionStorage`, opens the auth modal, and prompts login/register.
3. On successful authentication, the SPA resumes the checkout by calling `POST /api/v1/checkout`.
4. The backend returns a `CheckoutSession` (in production this would redirect to a payment gateway).

## Customization

- **Add a program / pack** — append to `backend/app/catalog.py` (seed source).
- **Change colors** — edit the CSS variables at the top of `frontend/css/styles.css` and the `tailwind.config` block inside `frontend/index.html`. Default palette: Primary `#8B0000` (dark red), Secondary `#0EA5E9` (sky blue). Dark mode page `#191970`, card `#00BFFF`, text `#F8FAFC` / `#94A3B8`. Light mode page `#F0FFFF`, card `#00BFFF` with `#E2E8F0` border.
- **Change translations** — edit `frontend/locales/en.json` and `ar.json`; no rebuild required.
- **Theme colors** for both modes live in the `:root` and `html.light` blocks of `styles.css`.

## Production notes

- Replace the dev `Base.metadata.create_all()` startup hook with `alembic upgrade head`.
- Set `COOKIE_SECURE=true` and serve over HTTPS.
- Set `SECRET_KEY` to a long random value (e.g. `openssl rand -hex 64`).
- Restrict `FRONTEND_ORIGINS` to the production frontend origin(s).
- Put the API behind a reverse proxy (nginx / Caddy) for TLS termination.
- Wire `POST /checkout` to a real payment provider (Stripe Checkout, Tap, etc.).
