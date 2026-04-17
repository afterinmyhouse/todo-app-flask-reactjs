# Frontend screens

Purpose of this doc:

- Give a single reference for every dashboard screen: its route, data
  shape, dependencies, and tests.
- Codify the repeatable **"scaffold a new screen"** workflow we use so
  additions stay consistent as the frontend grows.

The routing tree is wired in [`frontend/src/routes/routes.tsx`](../frontend/src/routes/routes.tsx).
All screens below live under the authenticated `/dashboard` root and
share its `Navbar` + toast layout.

---

## Screen index

| Route                                    | File                                                                                     | Purpose                                                                |
| ---------------------------------------- | ---------------------------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| `/dashboard`                             | `routes/dashboard/page.tsx`                                                              | Home — tags filter + tasks grid.                                       |
| `/dashboard/settings`                    | `routes/dashboard/settings/page.tsx`                                                     | Session + API base URL management.                                     |
| `/dashboard/projects`                    | `routes/dashboard/projects/page.tsx`                                                     | Projects hub — lists cached projects, CTAs for both create flows.      |
| `/dashboard/projects/new`                | `routes/dashboard/projects/new/page.tsx`                                                 | Simple project create form → `POST /api/v1/add-project`.               |
| `/dashboard/projects/new-with-tasks`     | `routes/dashboard/projects/new-with-tasks/page.tsx`                                      | Multi-entity form (project + 1..50 tasks) → `POST /api/v1/add-project-with-tasks`. |

The three project screens were added together in the
[UI Screen Addition x3 task](#scaffolding-workflow) and are the
reference implementations for the workflow below.

---

## 1. Projects hub — `/dashboard/projects`

- **File:** [`frontend/src/routes/dashboard/projects/page.tsx`](../frontend/src/routes/dashboard/projects/page.tsx)
- **Components:**
  - `_components/project-card.tsx` — compact read-only card.
  - `_components/empty-state.tsx` — empty state with two CTAs; has
    `role="region"` + labelled heading so tests can target it.
- **Data:** `useGetProjectsQuery()` — cache-only today, seeded by the
  create mutations (see
  [`services/queries/projects.ts`](../frontend/src/services/queries/projects.ts)).
  When a `GET /api/v1/projects` endpoint lands, swap the placeholder
  `queryFn` and every consumer updates automatically.
- **Props/data shape:** `Project[]` (see `src/types/types.ts`).
- **Empty state:** rendered when the cached list is empty; both CTAs
  deep-link to the create screens.
- **Tests:** [`page.test.tsx`](../frontend/src/routes/dashboard/projects/page.test.tsx)
  — empty state rendering + cache-seeded rendering.

## 2. New Project — `/dashboard/projects/new`

- **File:** [`frontend/src/routes/dashboard/projects/new/page.tsx`](../frontend/src/routes/dashboard/projects/new/page.tsx)
- **Component:** `_components/form.tsx::NewProjectForm`.
- **Contract:** `POST /api/v1/add-project`. Zod schema
  (`src/schemas/project-schema.ts::CreateProjectSchema`) mirrors the
  backend's `PlainCreateProjectSchema`, so most errors surface
  client-side without a round trip.
- **Behavior:**
  1. Submits via `useCreateProjectMutation`.
  2. Mutation success seeds the shared `["projects"]` cache and
     navigates to `/dashboard/projects`.
  3. Mutation failure → `toast.error(getApiErrorMessage(...))`.
- **Tests:** [`_components/form.test.tsx`](../frontend/src/routes/dashboard/projects/new/_components/form.test.tsx)
  — renders, blocks blank submit, calls API + navigates on success.

## 3. New Project With Tasks — `/dashboard/projects/new-with-tasks`

- **File:** [`frontend/src/routes/dashboard/projects/new-with-tasks/page.tsx`](../frontend/src/routes/dashboard/projects/new-with-tasks/page.tsx)
- **Components:**
  - `_components/form.tsx::NewProjectWithTasksForm` — owns the field
    array (`useFieldArray`), submission, and navigation.
  - `_components/task-rows.tsx::TaskRows` — purely presentational list
    of task rows; accepts `control`, `fields`, `canRemove`, `disabled`,
    `onRemove`. Keeping this split contains re-renders and makes each
    row targetable via `data-testid="task-row-N"` in tests.
- **Contract:** `POST /api/v1/add-project-with-tasks`. Zod schema
  (`CreateProjectWithTasksSchema`) mirrors the backend:
  - Array length 1..50.
  - Per-row `title` required.
  - Case-insensitive duplicate-title check via `superRefine` — same
    rule as the backend `DUPLICATE_TASK_TITLE` error, caught before
    we hit the network.
- **API mapping:** `createProjectWithTasksAPI` strips empty `tagId`
  strings from the payload so the backend's "tag must exist" check
  never fires for omitted tags.
- **Atomicity:** backed by the server's compensation pattern; a
  partial failure leaves nothing behind, and the UI simply surfaces
  the server error via `toast.error`.
- **Tests:** [`_components/form.test.tsx`](../frontend/src/routes/dashboard/projects/new-with-tasks/_components/form.test.tsx)
  — initial state, append/remove rows, validation blocking submit,
  valid payload + navigation.

---

## Shared conventions

- **Forms** use `react-hook-form` + `zodResolver` + the shadcn `Form`
  primitives (`FormField`, `FormItem`, `FormControl`, `FormMessage`).
- **Mutations** live under `src/services/mutations/*`; they own cache
  invalidation (`tasks`) and cache seeding (`projects`).
- **Queries** live under `src/services/queries/*` and use stable
  `queryKey` tuples exported for test setup.
- **Schemas** live under `src/schemas/*`; keep them aligned with the
  backend Marshmallow/`Plain*Schema` definitions.
- **Types** are centralized in `src/types/types.ts`.
- **Testing:** every form/page has a colocated `*.test.tsx`. Use
  [`src/test/render.tsx::renderWithProviders`](../frontend/src/test/render.tsx)
  to get the same `QueryClientProvider` + `MemoryRouter` shell the
  app uses, with retries disabled so failed mutations surface
  immediately.
- **SEO:** each page calls `useSEO("<Title> | TodoApp")`.
- **Navigation:** cross-links between the two create screens live in
  the page headers. The Navbar (`routes/dashboard/_components/navbar.tsx`)
  gets an entry per top-level section.

---

## Scaffolding workflow

Use this checklist whenever you add a new dashboard screen. It is the
process we followed for the three screens above and keeps file layout,
tests, and docs aligned.

1. **Types.** Add the server-exchanged types to `src/types/types.ts`.
2. **Schema.** Add a Zod schema under `src/schemas/` mirroring the
   backend's `Plain*Schema` (keeps most errors client-side).
3. **API client.** Add a function under `src/services/api/` that
   accepts the Zod-typed form data and returns the typed response.
   Map optional empty strings to `undefined` at this boundary.
4. **Query / Mutation.** Add a query hook under
   `src/services/queries/` and/or a mutation hook under
   `src/services/mutations/`. Seed caches on success instead of
   invalidating when the backend lacks a list endpoint.
5. **Screen files.** Create `routes/dashboard/<section>/page.tsx`
   for the page shell and `routes/dashboard/<section>/_components/`
   for extracted pieces (forms, cards, empty states). Keep the page
   presentational; put submit/mutation logic in a form component so
   the test can render it in isolation.
6. **Route.** Register the new path in
   `routes/dashboard` children in `src/routes/routes.tsx`.
7. **Navbar.** Add a link when the screen is a top-level section.
8. **Tests.** Colocate a `*.test.tsx` that uses
   `renderWithProviders`, mocks `react-router-dom::useNavigate`, the
   relevant `@/services/api/*` module, and `sonner::toast`. Cover
   render, blocked-submit on invalid input, and success → navigate.
9. **Docs.** Add a screen entry to this file and, if the screen
   introduces a new frontend pattern (field arrays, optimistic
   caching, etc.), note it under **Shared conventions** so the next
   author picks it up.
10. **Verify.** Run `pnpm --filter frontend test` (or
    `npm --prefix frontend run test`), `npm --prefix frontend run build`
    (runs `tsc -b`), and `npm --prefix frontend run lint`.

---

## Where this intersects the backend

- The three project screens surface the endpoints delivered across the
  three backend "API Addition End-to-End" runs documented in
  [`API_CHANGELOG.md`](./API_CHANGELOG.md):
  - Run 1 — `POST /api/v1/add-project` (simple create).
  - Run 2 — `POST /api/v1/add-task-comment` (not yet surfaced on
    the frontend; a future Task Detail screen is the natural home).
  - Run 3 — `POST /api/v1/add-project-with-tasks` (multi-entity
    atomic create).
- The frontend Zod schemas intentionally mirror the backend
  `plain_schema.py` definitions; keep them in lockstep when
  validation rules change.
