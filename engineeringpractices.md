# Engineering Practices

This document summarizes **how this repo is built today** (stack, conventions, style guide), based on the current code layout and configs.

## Tech stack overview

### Frontend (`frontend/`)
- **Runtime/build**: Vite + TypeScript
- **UI**: React 18
- **Styling**: TailwindCSS (+ `tailwindcss-animate`), CSS variables theme tokens (shadcn-style)
- **UI primitives**: Radix UI components (Dialog, Select, Slot, Alert Dialog, Tabs, etc.)
- **State**: Zustand (with `persist`, stored under key `"session"`)
- **Forms**: React Hook Form + Zod (+ `@hookform/resolvers`)
- **Data fetching/cache**: TanStack React Query
- **HTTP**: Axios (centralized client in `src/services/api/client.ts`; export **`API_BASE_URL`** for display/config UIs)
- **Toasts**: Sonner
- **Icons**: `lucide-react`
- **Testing**: Vitest + Testing Library (`@testing-library/react`, `user-event`, `jest-dom`)

### Backend (`backend/`)
- **Runtime**: Python 3.13 (declared in `Pipfile`)
- **Web**: Flask
- **API layer**: Flask-Smorest (Blueprints + Marshmallow schemas)
- **Auth**: Flask-JWT-Extended (JWT access tokens)
- **Primary app data**: **MongoDB** via `pymongo` (`backend/flaskr/mongo.py`) for users, tags, and tasks (`MONGO_URI`, `MONGO_DB_NAME` in `backend/config.py` / `.env`).
- **SQL stack (also present)**: SQLAlchemy + Flask-SQLAlchemy + Flask-Migrate (Alembic) — used for relational models/migrations; **not** the store for the todo API collections above.
- **CORS**: Flask-CORS
- **Local SQL file**: SQLite (`backend/data.db`) for SQLAlchemy-managed tables.
- **Dev tooling (declared)**: Black + Flake8

## Project structure (practical)

### Frontend
- **Routing**: `react-router-dom` with `createBrowserRouter` in `frontend/src/routes/routes.tsx`
  - Public area: `frontend/src/routes/landing/**`
  - Protected area: `frontend/src/routes/dashboard/**` guarded in `frontend/src/routes/dashboard/root.tsx`
- **API calls**: `frontend/src/services/api/*`
  - Use the shared `api` axios instance from `@/services/api/client.ts` (and **`API_BASE_URL`** when you need the base URL string).
  - Prefer **`@/`** imports in app code (including `import { api } from "@/services/api/client"` in sibling API modules).
  - Avoid duplicating `VITE_API_BASE_URL ?? "http://localhost:5000"` outside `client.ts`.
- **Server state**: `frontend/src/services/queries/*` and `frontend/src/services/mutations/*` (React Query wrappers)
- **State**: `frontend/src/stores/*` (Zustand)
- **UI primitives**: `frontend/src/components/ui/*` (shadcn-style components)

### Backend
- **App factory**: `backend/flaskr/__init__.py` exposes `create_app`
- **Entry**: `backend/application.py` creates the Flask app
- **Routes**: `backend/flaskr/routes/*_route.py` (Flask-Smorest `Blueprint` + `MethodView`)
- **Controllers**: `backend/flaskr/controllers/*_controller.py` (business logic + DB interactions)
- **Schemas**: `backend/flaskr/schemas/*` (Marshmallow)
- **SQLAlchemy models**: `backend/flaskr/models/*_model.py` (for SQL tables / migrations)
- **Mongo access**: `backend/flaskr/mongo.py` — single shared `MongoClient`; settings from **`config.Config`** (same env as Flask)

## Style guide (repo conventions)

### General
- **Prefer small, single-responsibility modules**: routes/controllers/schemas separated on backend; UI/queries/mutations separated on frontend.
- **No hard-coded environment values** inside components when possible (reuse `API_BASE_URL` / `api` defaults).
- **Accessibility**: when using icon-only buttons/links, include `aria-label`/`title`.

### TypeScript / React
- **File naming**: mostly `kebab-case` for folders; `kebab-case.tsx` for leaf components under routes; UI components in `components/ui/*.tsx`.
- **Component naming**: `PascalCase` exports (`DashboardHomePage`, `CreateDialog`, `TaskCard`).
- **Hooks**: `useX` naming (`useSEO`, `useGetTagsQuery`).
- **Types**: central domain types in `frontend/src/types/types.ts`.
- **Imports**:
  - Prefer `@/` alias for `frontend/src/*` (configured via `tsconfig` + `vite` alias).
  - Group imports by source: app imports, then external libs.
- **Avoid** `as unknown as` component casts at route boundaries when props can be aligned with `Dispatch<SetStateAction<...>>` or shared prop types.
- **Styling**:
  - Prefer Tailwind utility classes.
  - Compose class strings with `cn()` when conditional.
  - Keep layout primitives consistent: `space-y-*`, `gap-*`, responsive `md:`/`lg:` breakpoints.

### Python / Flask
- **Route style**: Flask-Smorest class-based views:
  - `@bp.route(...)`
  - `@bp.arguments(Schema)`
  - `@bp.response(code, Schema?)`
- **Auth**: protect endpoints with `@jwt_required()`, identify user with `get_jwt_identity()`.
- **Errors**: use **`api_abort(...)`** from `flaskr.errors` so responses match **`docs/API_ERROR_HANDLING.md`** (`error.code`, `error.message`, `error.httpStatus`, `error.details`). JWT loaders use the same envelope via `flaskr/extensions.py`.
- **DB patterns**:
  - **Mongo**: validate ids with `bson.ObjectId` and catch **`bson.errors.InvalidId`** where appropriate; avoid bare `except Exception` for parse errors.
  - **SQLAlchemy**: read via `select(Model)` or `db.session.query(...)`; rollback on `SQLAlchemyError` where SQL sessions are used.

## Testing guidance

### Frontend
- **Unit/UI tests**: Vitest + Testing Library.
  - Keep tests near the component (`*.test.tsx`).
  - Mock network via the shared API client (`@/services/api/client`) or introduce MSW if you want higher-fidelity integration tests.
  - Prefer real assertions on success/error paths over placeholder `expect(true).toBe(true)` skeleton tests.

### Backend (optional extension)
- Pytest is not yet wired in, but is a natural fit to test controllers + routes (especially auth + protected endpoints).

## Local development practices

### Environment variables
- **Backend**: `backend/.env` must define `JWT_SECRET_KEY=...` (loaded in `backend/config.py`). Optional: `MONGO_URI`, `MONGO_DB_NAME`.
- **Frontend (optional)**: `VITE_API_BASE_URL` can be set to point to the backend; defaults to `http://localhost:5000` (see `client.ts` / `API_BASE_URL`).

### Commands
- Frontend: `npm run dev`, `npm run build`, `npm test`, `npm run lint`
- Backend: `flask --app application run --debug`, `flask --app application db upgrade`, `python seed.py`

## Known issues / improvement opportunities (observed)
- **Security**: token is persisted in local storage (`zustand persist`); acceptable for demos but consider hardened storage/refresh strategy for production.
- **Public tags API**: `GET`/`POST` `/api/v1/tags` are unauthenticated by design for now; lock down if you expose sensitive data.
- **SQL vs Mongo**: two persistence styles coexist; new features should state clearly which store they target.
