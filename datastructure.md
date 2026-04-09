# Data Structures (Database Schema)

This repo already uses **SQLite + SQLAlchemy + Flask-Migrate** in `backend/`. This document defines a **new DB-backed feature** ("Projects + Comments + User Preferences") and the data structures needed to implement it.

## Feature: Projects + Task comments + User preferences

### Why this feature
- **Projects**: group tasks into higher-level buckets (Work/School/etc.) without overloading tags.
- **Comments**: keep lightweight discussion/notes per task.
- **Preferences**: store per-user UI settings (e.g., default project, default status filter).

## Data structures (3–4)

### 1) `Project`
- **Table**: `projects`
- **Purpose**: user-owned container that tasks can belong to.
- **Fields**
  - `id` (PK, int)
  - `name` (string(60), required)
  - `color` (string(24), optional) – e.g. `"slate"`, `"#22c55e"`
  - `created_at` (datetime, required; default now)
  - `user_id` (FK → `users.id`, required)
- **Relationships**
  - `UserModel.projects` 1→N `ProjectModel`
  - `ProjectModel.tasks` 1→N `TaskModel` (optional association on task)

### 2) `TaskComment`
- **Table**: `task_comments`
- **Purpose**: store comments/notes attached to tasks.
- **Fields**
  - `id` (PK, int)
  - `body` (string(1000), required)
  - `created_at` (datetime, required; default now)
  - `task_id` (FK → `tasks.id`, required)
  - `user_id` (FK → `users.id`, required) – author
- **Relationships**
  - `TaskModel.comments` 1→N `TaskCommentModel`
  - `UserModel.task_comments` 1→N `TaskCommentModel`

### 3) `UserPreference`
- **Table**: `user_preferences`
- **Purpose**: per-user preferences (1 row per user).
- **Fields**
  - `id` (PK, int)
  - `user_id` (FK → `users.id`, unique, required)
  - `default_project_id` (FK → `projects.id`, optional)
  - `default_task_status` (string(20), optional) – `"PENDING" | "IN_PROGRESS" | "COMPLETED"`
  - `created_at` (datetime, required; default now)
  - `updated_at` (datetime, required; default now; update on change)
- **Relationships**
  - `UserModel.preferences` 1→1 `UserPreferenceModel`

### 4) (Optional) `AuditEvent`
- **Table**: `audit_events`
- **Purpose**: simple audit trail for important actions (sign-in, create task, delete task).
- **Fields**
  - `id` (PK, int)
  - `event_type` (string(40), required) – e.g. `"TASK_CREATED"`
  - `payload` (string, optional) – JSON-as-string for quick logging
  - `created_at` (datetime, required; default now)
  - `user_id` (FK → `users.id`, optional)

## Folder structure (backend)

New files added for this feature:
- `backend/flaskr/models/project_model.py`
- `backend/flaskr/models/task_comment_model.py`
- `backend/flaskr/models/user_preference_model.py`
- `backend/flaskr/models/audit_event_model.py` (optional, included as starter)

Existing files updated to wire relationships:
- `backend/flaskr/models/user_model.py`
- `backend/flaskr/models/task_model.py`
- `backend/flaskr/models/__init__.py`

## Migration workflow (how to apply)

After adding models, generate/apply migrations:

```bash
cd backend
flask --app application db migrate -m "add projects comments preferences audit"
flask --app application db upgrade
```

