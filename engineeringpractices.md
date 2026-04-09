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
- **HTTP**: Axios (centralized client in `src/services/api/client.ts`)
- **Toasts**: Sonner
- **Icons**: `lucide-react`
- **Testing**: Vitest + Testing Library (`@testing-library/react`, `user-event`, `jest-dom`)

### Backend (`backend/`)
- **Runtime**: Python 3.13 (declared in `Pipfile`)
- **Web**: Flask
- **API layer**: Flask-Smorest (Blueprints + Marshmallow schemas)
- **Auth**: Flask-JWT-Extended (JWT access tokens)
- **DB/ORM**: SQLAlchemy + Flask-SQLAlchemy
- **Migrations**: Flask-Migrate (Alembic)
- **CORS**: Flask-CORS
- **Local DB**: SQLite (`backend/data.db`)
- **Dev tooling (declared)**: Black + Flake8

## Project structure (practical)

### Frontend
- **Routing**: `react-router-dom` with `createBrowserRouter` in `frontend/src/routes/routes.tsx`
  - Public area: `frontend/src/routes/landing/**`
  - Protected area: `frontend/src/routes/dashboard/**` guarded in `frontend/src/routes/dashboard/root.tsx`
- **API calls**: `frontend/src/services/api/*`
  - Use the shared `api` axios instance from `frontend/src/services/api/client.ts`
  - Avoid hardcoding backend URLs in feature components
- **Server state**: `frontend/src/services/queries/*` and `frontend/src/services/mutations/*` (React Query wrappers)
- **State**: `frontend/src/stores/*` (Zustand)
- **UI primitives**: `frontend/src/components/ui/*` (shadcn-style components)

### Backend
- **App factory**: `backend/flaskr/__init__.py` exposes `create_app`
- **Entry**: `backend/application.py` creates the Flask app
- **Routes**: `backend/flaskr/routes/*_route.py` (Flask-Smorest `Blueprint` + `MethodView`)
- **Controllers**: `backend/flaskr/controllers/*_controller.py` (business logic + DB interactions)
- **Schemas**: `backend/flaskr/schemas/*` (Marshmallow)
- **Models**: `backend/flaskr/models/*_model.py` (SQLAlchemy)

## Style guide (repo conventions)

### General
- **Prefer small, single-responsibility modules**: routes/controllers/schemas separated on backend; UI/queries/mutations separated on frontend.
- **No hard-coded environment values** inside components when possible.
- **Accessibility**: when using icon-only buttons/links, include `aria-label`/`title`.

### TypeScript / React
- **File naming**: mostly `kebab-case` for folders; `kebab-case.tsx` for leaf components under routes; UI components in `components/ui/*.tsx`.
- **Component naming**: `PascalCase` exports (`DashboardHomePage`, `CreateDialog`, `TaskCard`).
- **Hooks**: `useX` naming (`useSEO`, `useGetTagsQuery`).
- **Types**: central domain types in `frontend/src/types/types.ts`.
- **Imports**:
  - Prefer `@/` alias for `frontend/src/*` (configured via `tsconfig` + `vite` alias).
  - Group imports by source: app imports, then external libs.
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
- **Errors**: use `flask_smorest.abort(status, message="...")` for API errors.
- **DB patterns**:
  - Read via `select(Model)` or `db.session.query(...)`
  - Rollback on `SQLAlchemyError`

## Testing guidance

### Frontend
- **Unit/UI tests**: Vitest + Testing Library.
  - Keep tests near the component (`*.test.tsx`).
  - Mock network via the shared API client (`@/services/api/client`) or introduce MSW if you want higher-fidelity integration tests.

### Backend (optional extension)
- Pytest is not yet wired in, but is a natural fit to test controllers + routes (especially auth + protected endpoints).

## Local development practices

### Environment variables
- **Backend**: `backend/.env` must define `JWT_SECRET_KEY=...` (loaded in `backend/config.py`).
- **Frontend (optional)**: `VITE_API_BASE_URL` can be set to point to the backend; defaults to `http://localhost:5000`.

### Commands
- Frontend: `npm run dev`, `npm run build`, `npm test`, `npm run lint`
- Backend: `flask --app application run --debug`, `flask --app application db upgrade`, `python seed.py`

## Known issues / improvement opportunities (observed)
- **Backend bug risk**: `TaskController.get_all_on_user()` uses `.where(user_id == user_id)` which is a no-op filter; it likely meant to filter tasks by the authenticated user id.
- **Debug output**: `print(data)` exists in `backend/flaskr/controllers/task_controller.py`; consider removing or gating behind debug.
- **Security**: token is persisted in local storage (`zustand persist`); acceptable for demos but consider hardened storage/refresh strategy for production.

