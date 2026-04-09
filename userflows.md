# User Flows

This document describes the **user-facing flows** implemented in the current app (frontend + backend), including key screens and APIs involved.

## 1) Create account (Sign up)

- **User goal**: Create a new account so they can sign in and manage tasks.
- **Entry point (UI)**: Landing page `/` (tabbed auth UI).
- **Frontend**
  - Form UI: `frontend/src/routes/landing/home/_components/create-account/form.tsx`
  - Validation: `frontend/src/schemas/auth-schema.ts` (`CreateAccountFormSchema`)
  - Request: `POST /api/v1/users` using shared API client (`frontend/src/services/api/client.ts`)
  - Feedback: success toast + form reset; error toast via Axios error message.
- **Backend**
  - Route: `backend/flaskr/routes/user_route.py` → `POST /users`
  - Controller: `backend/flaskr/controllers/user_controller.py` → `UserController.create`
  - Model: `backend/flaskr/models/user_model.py`
  - Behavior:
    - Rejects duplicate username/email (409)
    - Hashes password (`flaskr/utils.py` → `generate_password`)

## 2) Sign in (Login)

- **User goal**: Authenticate and access the dashboard.
- **Entry point (UI)**: Landing page `/` → Sign In tab.
- **Frontend**
  - Form UI: `frontend/src/routes/landing/home/_components/sign-in/form.tsx`
  - Validation: `frontend/src/schemas/auth-schema.ts` (`SignInFormSchema`)
  - Request: `POST /api/v1/auth/sign-in`
  - On success:
    - Persist token in Zustand store: `frontend/src/stores/auth-store.ts` (`signIn(token)`)
    - Navigate to `/dashboard`
  - Route guards:
    - If logged in: landing root redirects to `/dashboard` (`frontend/src/routes/landing/root.tsx`)
    - If not logged in: dashboard root redirects to `/` (`frontend/src/routes/dashboard/root.tsx`)
- **Backend**
  - Route: `backend/flaskr/routes/auth_route.py` → `POST /auth/sign-in`
  - Controller: `backend/flaskr/controllers/auth_controller.py` → `AuthController.sign_in`
  - Behavior:
    - Looks up user by email
    - Verifies password (`flaskr/utils.py` → `check_password`)
    - Returns `{ "token": "<jwt>" }`

## 3) View dashboard (Tags + Tasks)

- **User goal**: See available tags and their tasks.
- **Entry point (UI)**: `/dashboard`
- **Frontend**
  - Page: `frontend/src/routes/dashboard/page.tsx`
  - Tags:
    - Component: `frontend/src/routes/dashboard/_components/tags/section.tsx`
    - Query: `frontend/src/services/queries/tags.ts` → `getTagsAPI`
    - API: `GET /api/v1/tags`
  - Tasks:
    - Component: `frontend/src/routes/dashboard/_components/tasks/section.tsx`
    - Query: `frontend/src/services/queries/tasks.ts` → `getTasksOnUserAPI`
    - API: `GET /api/v1/tasks/user` (JWT required)
  - Layout behavior:
    - Tags show as a horizontal scroll row on mobile; grid on md+.
    - Tasks render in a responsive grid.

## 4) Filter tasks by tag (client-side)

- **User goal**: Focus on tasks for a specific tag.
- **Frontend**
  - State: `selectedTag` in `frontend/src/routes/dashboard/page.tsx`
  - Interaction: click a tag chip (or “All”) in `tags/section.tsx`
  - Filtering: client-side `tasks.filter(t => t.tagName === selectedTag)` in `tasks/section.tsx`
- **Backend**
  - No additional API needed (currently all filtering is on client).

## 5) Create task

- **User goal**: Add a new task.
- **Frontend**
  - CTA: `CreateDialog` in `frontend/src/routes/dashboard/_components/tasks/create-dialog.tsx`
  - Form: `frontend/src/routes/dashboard/_components/tasks/create-form.tsx`
  - Validation: `frontend/src/schemas/task-schema.ts`
  - Mutation: `frontend/src/services/mutations/tasks.ts` → `createTaskAPI`
  - API: `POST /api/v1/tasks` (JWT required)
- **Backend**
  - Route: `backend/flaskr/routes/task_route.py` → `POST /tasks`
  - Controller: `backend/flaskr/controllers/task_controller.py` → `TaskController.create`

## 6) View task details

- **User goal**: Read the full task content and metadata.
- **Frontend**
  - Trigger: click task title (opens dialog)
  - Dialog: `frontend/src/routes/dashboard/_components/tasks/show-dialog.tsx`
- **Backend**
  - No extra request (uses already-fetched list data).

## 7) Edit task

- **User goal**: Update title/content/status.
- **Frontend**
  - Trigger: pencil icon dialog
  - Dialog: `frontend/src/routes/dashboard/_components/tasks/edit-dialog.tsx`
  - Form: `frontend/src/routes/dashboard/_components/tasks/edit-form.tsx`
  - Mutation: `updateTaskAPI` → `PUT /api/v1/tasks/:taskId` (JWT required)
- **Backend**
  - Route: `backend/flaskr/routes/task_route.py` → `PUT /tasks/<task_id>`
  - Controller: `TaskController.update`

## 8) Delete task

- **User goal**: Remove a task.
- **Frontend**
  - Trigger: delete action in task details dialog
  - Dialog: `frontend/src/routes/dashboard/_components/tasks/delete-dialog.tsx`
  - Mutation: `deleteTaskAPI` → `DELETE /api/v1/tasks/:taskId` (JWT required)
- **Backend**
  - Route: `backend/flaskr/routes/task_route.py` → `DELETE /tasks/<task_id>`
  - Controller: `TaskController.delete`

## 9) Logout + session handling

- **User goal**: End session.
- **Frontend**
  - Navbar logout: `frontend/src/routes/dashboard/_components/navbar.tsx`
  - Store: `frontend/src/stores/auth-store.ts` (`logout()`)
  - Redirect: back to `/`
- **Backend**
  - Stateless JWT: logout is client-side (no server token revocation implemented).

## 10) Settings page

- **User goal**: Inspect session/runtime info and manage local session.
- **Frontend**
  - Route: `/dashboard/settings`
  - Page: `frontend/src/routes/dashboard/settings/page.tsx`
  - Actions:
    - Logout
    - Clear local session (`localStorage.removeItem("session")`)
    - Open backend Swagger docs (`<apiBaseUrl>/docs`)

