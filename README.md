# TODO App built with Flask and ReactJS

This is an web app with the objective of being able to save your notes and have them stored in a database. The user is able to perform basic actions such as create, read, update and delete this data, a basic CRUD.

## Table of contents

- [Built with](#built-with)
- [Project requirements and how to use it](#project-requirements-and-how-to-use-it)
  - [Frontend](#frontend)
  - [Backend](#backend)
  - [REST API](#rest-api)
  - [API error handling](#api-error-handling)
  - [Postman collection](#postman-collection)
- [Image gallery](#image-gallery)
  - [REST API](#rest-api-preview)
  - [Frontend](#frontend-preview)

## Built with

The project was developed from scratch with Frontend and Backend technologies, for the communication between the client and the server I implemented a REST API, which is responsible for returning the necessary data in JSON format to the client:

- Frontend:
  - ReactJS
  - TypeScript
  - TailwindCSS
  - Axios
  - ShadcnUI
  - React Router Dom
  - React Hook Form
  - Zustand
  - React Query

- Backend:
  - Python (Flask)
  - SQLite (As database manager)
  - Flask Migrate (To perform migrations)
  - SQLAlchemy and Flask SQLAlchemy (Python SQL toolkit and ORM that gives application developers the full power and flexibility of SQL)
  - REST API (For communication between client and server)
  - SwaggerUI
  - Flask Smorest (Used for rest api creation and schema creation)
  - Flask JWT Extended (For the creation of JWT)
  - MVC (Software Design Pattern)

## Project requirements and how to use it

For the project you must run both development environments at the same time, both the Frontend and the Backend. In the Frontend you will find JavaScript technologies (ReactJS) and in the Backend you will find Python technologies and tools (Flask), so you must have NodeJS and Python installed on your computer (As a reference this project was developed with version 3.13.0 of Python and 22.11.0 of NodeJS).

I leave you links to NodeJS and Python for installation:
  - [NodeJS website](https://nodejs.org/en/)
  - [Python website](https://www.python.org/)

First of all download the project to start using it, do it from the terminal:

```shell
$ git clone https://github.com/Remy349/todo-app-flask-reactjs.git

$ cd todo-app-flask-reactjs
```

If you did it correctly and there were no problems, you should see these folders:

```shell
/backend
/frontend
/preview
README.md
```

### Frontend

If you already have NodeJS installed on your computer perform the following steps to run the Frontend (Remember that the Backend must be running):

1. Move to the `/frontend` folder and run the following command to install the necessary:

```shell
# This will install what you need for the Frontend (npm comes with NodeJS after installation)
$ npm install
```

2. Then you will need to run the following command to start running the Frontend:

```shell
$ npm run dev

# You will see something like this:
VITE v5.4.11  ready in 349 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

3. That's all for the Frontend, if you haven't run the Backend yet, continue with the next section (Backend)

#### Dashboard screens

The authenticated dashboard is composed of these screens (see
[`docs/FRONTEND_SCREENS.md`](./docs/FRONTEND_SCREENS.md) for the full
reference and the repeatable scaffolding workflow):

- `/dashboard` — tags filter and tasks grid.
- `/dashboard/settings` — session + API base URL management.
- `/dashboard/projects` — projects hub (CTAs + cached list).
- `/dashboard/projects/new` — single-entity project create form.
- `/dashboard/projects/new-with-tasks` — project + 1..50 tasks in one
  atomic request (field-array form backed by
  `POST /api/v1/add-project-with-tasks`).

Run the frontend tests with:

```shell
$ npm run test
```

### Backend

If you already have Python installed on your computer perform the following steps to run the Backend

1. Move to the `/backend` folder and run the following command to create a virtual development environment with Python:

```shell
# If it doesn't work this way try "python3", this will depend on how you installed Python on your computer
$ python -m venv venv
```

2. Now activate the development environment and install the necessary requirements found in the `requirements.txt` file:

```shell
# This is how it is done in Linux, in Windows it is as follows "venv\Scripts\activate"
$ . venv/bin/activate
# Now install the necessary requirements using "pip" or "pip3",
# this will depend on how you installed Python on your computer
(venv) $ pip install -r requirements.txt
```

3. Create an .env file and add an environment variable for JWT creation:

```shell
# This is an example
JWT_SECRET_KEY="c7d57142e46f169ce9dbeb8d96603e46"
```

4. Now you can start running the server:

```shell
(venv) $ flask run

# You will see something like this:
* Serving Flask app 'application.py'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 140-954-082
```

5. Visit the path where the Swagger interface is located to see all the api endpoints:

`http://localhost:5000/docs`

With this you will have your Python environment ready to work, it also has a database so you don't have to worry about that and it already has some data already entered so you can interact with the REST API.

But if you want to start blank with no previously stored data delete the database and run the following command to create a new database (This step is optional):

```shell
# This will create a new database with the necessary tables to store the data 
# if you want to know the table structure have a look at the "/flaskr/models" folder.
(venv) $ flask db upgrade
```

After you have done the previous step add some default data for the task labels. Do this by running the following command in the terminal:

```shell
python seed.py
```

### REST API

Everything related to the API is inside `flaskr/routes`. The following table summarizes the routes that were implemented:

| HTTP Method | Resource URL            | Notes                                   |
| ----------- | ----------------------- | --------------------------------------- |
| `POST`      | */api/v1/auth/login*    | Login; returns JWT (`LoginResponseSchema`) |
| `POST`      | */api/v1/auth/sign-in*  | Same as login (legacy path)            |
| `POST`      | */api/v1/auth/register* | Register user; returns user + JWT (201) |
| `GET`       | */api/v1/auth/me*      | Current user profile (**JWT required**) |
| `GET`       | */api/v1/users*         | List all users (**JWT required**)       |
| `POST`      | */api/v1/users*         | Create a new user                       |
| `GET`       | */api/v1/users/id*      | Get user by id (**JWT**, own id only)   |
| `DELETE`    | */api/v1/users/account* | Delete a user account                   |
| `GET`       | */api/v1/tags*          | Get a list of tags                      |
| `POST`      | */api/v1/tags*          | Create a new tag                        |
| `POST`      | */api/v1/add-project*   | Create a project (**JWT required**)     |
| `POST`      | */api/v1/add-project-with-tasks* | Create a project and its initial tasks atomically (**JWT required**) |
| `POST`      | */api/v1/add-task-comment* | Create a comment on an owned task (**JWT required**) |
| `POST`      | */api/v1/tasks*         | Create a new task                       |
| `GET`       | */api/v1/tasks/user*    | Get a list of all tasks on user         |
| `PUT`       | */api/v1/tasks/id*      | Update a task                           |
| `DELETE`    | */api/v1/tasks/id*      | Delete a task                           |

#### POST `/api/v1/add-project`

Creates a new project for the authenticated user.

- Authentication: `Authorization: Bearer <accessToken>`
- Content-Type: `application/json`
- Request body:
  - `name` (string, required, 1-60 chars)
  - `description` (string, optional, max 280 chars; defaults to empty string)

Example cURL:

```shell
curl -X POST "http://localhost:5000/api/v1/add-project" \
  -H "Authorization: Bearer <accessToken>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Roadmap",
    "description": "Quarterly planning board"
  }'
```

Success response (`201 Created`):

```json
{
  "id": "6800033b4f0f4e7f8e735d7a",
  "name": "Roadmap",
  "description": "Quarterly planning board",
  "createdAt": "2026-04-17T10:30:42.112000+00:00"
}
```

Error responses:
- `401` `AUTH_REQUIRED` when token is missing
- `401` `INVALID_TOKEN_SUBJECT` when JWT subject is invalid
- `409` `PROJECT_EXISTS` when the same project name already exists for that user
- `422` `VALIDATION_ERROR` when request payload fails schema validation

#### POST `/api/v1/add-task-comment`

Creates a comment on a task owned by the authenticated user.

- Authentication: `Authorization: Bearer <accessToken>`
- Content-Type: `application/json`
- Request body:
  - `taskId` (string, required, Mongo ObjectId of an owned task)
  - `body` (string, required, 1-2000 chars; trimmed server-side — all-whitespace bodies are rejected as `422`)

Example cURL:

```shell
curl -X POST "http://localhost:5000/api/v1/add-task-comment" \
  -H "Authorization: Bearer <accessToken>" \
  -H "Content-Type: application/json" \
  -d '{
    "taskId": "6708e1f1f1f1f1f1f1f1f3c1",
    "body": "Looks good, merging after CI."
  }'
```

Success response (`201 Created`):

```json
{
  "id": "6800045b4f0f4e7f8e735d7b",
  "taskId": "6708e1f1f1f1f1f1f1f1f3c1",
  "body": "Looks good, merging after CI.",
  "createdAt": "2026-04-17T10:35:01.441000+00:00"
}
```

Error responses:
- `400` `INVALID_TASK` when `taskId` is not a valid Mongo ObjectId
- `401` `AUTH_REQUIRED` when token is missing
- `401` `INVALID_TOKEN_SUBJECT` when JWT subject is invalid
- `404` `TASK_NOT_FOUND` when the task does not exist or is not owned by the caller (existence is not leaked)
- `422` `VALIDATION_ERROR` when request payload fails schema validation (missing fields or blank body)

#### POST `/api/v1/add-project-with-tasks`

Creates a project together with its initial tasks (1..50) in a single request.
The endpoint is **atomic from the caller's perspective** — if anything fails
part-way through persistence, the project (and any tasks already written) are
rolled back via compensating deletes, so clients never observe a half-applied
state. On a replica-set deployment this block can be swapped for a native
MongoDB multi-document transaction without changing the request/response
contract (see `flaskr/controllers/project_with_tasks_controller.py`).

- Authentication: `Authorization: Bearer <accessToken>`
- Content-Type: `application/json`
- Request body:
  - `name` (string, required, 1-60 chars, must not be blank after trim)
  - `description` (string, optional, max 280 chars; defaults to empty string)
  - `tasks` (array, required, 1..50 items). Each task:
    - `title` (string, required, 1-200 chars, must not be blank after trim)
    - `content` (string, optional, max 2000 chars; defaults to empty)
    - `status` (string, optional; one of `PENDING`, `IN_PROGRESS`, `COMPLETED`; defaults to `PENDING`)
    - `tagId` (string, optional; existing tag ObjectId)
- Extra validation beyond the schema:
  - Project name is unique **per user** (case- and whitespace-insensitive).
  - Task titles must be unique **within the request** (case- and whitespace-insensitive).
  - Every referenced `tagId` must exist.

Example cURL:

```shell
curl -X POST "http://localhost:5000/api/v1/add-project-with-tasks" \
  -H "Authorization: Bearer <accessToken>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Launch",
    "description": "Q2 launch plan",
    "tasks": [
      { "title": "Write spec", "status": "IN_PROGRESS" },
      { "title": "Draft UI",   "tagId": "6708e1f1f1f1f1f1f1f1f2a1" }
    ]
  }'
```

Success response (`201 Created`):

```json
{
  "id": "6800099b4f0f4e7f8e735d90",
  "name": "Launch",
  "description": "Q2 launch plan",
  "createdAt": "2026-04-17T11:02:11.912000+00:00",
  "tasks": [
    {
      "id": "6800099b4f0f4e7f8e735d91",
      "title": "Write spec",
      "content": "",
      "status": "IN_PROGRESS",
      "tagName": null,
      "createdAt": "2026-04-17T11:02:11.912000+00:00"
    },
    {
      "id": "6800099b4f0f4e7f8e735d92",
      "title": "Draft UI",
      "content": "",
      "status": "PENDING",
      "tagName": "Work",
      "createdAt": "2026-04-17T11:02:11.912000+00:00"
    }
  ]
}
```

Error responses:
- `400` `INVALID_TAG` when a task's `tagId` is not a valid Mongo ObjectId (the `details.field` pinpoints which task, e.g. `tasks[0].tagId`)
- `401` `AUTH_REQUIRED` / `INVALID_TOKEN_SUBJECT`
- `404` `TAG_NOT_FOUND` when a referenced tag does not exist
- `409` `PROJECT_EXISTS` when the caller already owns a project with the same name (case-insensitive)
- `422` `VALIDATION_ERROR` for schema failures (missing `name`, missing `tasks`, empty `tasks`, >50 tasks, missing task `title`, blank fields after trim)
- `422` `DUPLICATE_TASK_TITLE` when two tasks in the same request share a title (case-insensitive); `details.field` identifies the offending index (e.g. `tasks[1].title`)
- `500` — if a runtime DB failure occurs between entity inserts, the response is a 500 and the compensation logic removes the partially-written project and tasks before the error surfaces

### Quality Improvements vs. Previous Endpoints

Each run of the "API Addition End-to-End" workflow builds on the previous one.
See [`docs/API_CHANGELOG.md`](./docs/API_CHANGELOG.md) for the full per-run
changelog, impact metrics, and the repeatable workflow checklist. Highlights:

- **Run 3 (`/add-project-with-tasks`)** — handles **two related entities** in
  a single request. Introduces a three-phase controller structure
  (*pre-validate → persist → compensate on partial failure*), explicit
  index-scoped validation error paths (e.g. `tasks[0].tagId`), and the
  `DUPLICATE_TASK_TITLE` code for in-request collisions. Compensation-based
  atomicity is exercised directly by a test that simulates a mid-flight DB
  failure and asserts the project + any inserted tasks are rolled back.
- **Run 2 (`/add-task-comment`)** applied these improvements over the
  `/add-project` baseline:

- **DRY auth plumbing.** Introduced `flaskr.utils.resolve_user_oid()` and `flaskr.utils.parse_object_id()`. Duplicated `try/except InvalidId` blocks were removed from `ProjectController` and never copy-pasted into the new controller.
- **Single monkeypatch surface.** Controllers now call `mongo.get_db()` via `from flaskr import mongo`, so tests patch `flaskr.mongo.get_db` exactly once; adding more endpoints no longer requires editing `conftest.py`.
- **Generic in-memory DB.** `FakeDb.__getattr__` auto-provisions `FakeCollection` instances on access, so new collections (`task_comments`, `tasks`, …) work without test-fixture changes.
- **Session-scoped `app` fixture.** `create_app` runs once per session instead of per test, keeping wall-clock time flat as endpoint count grows.
- **Parametrized validation tests.** The three "missing field" cases for `/add-task-comment` are a single `pytest.mark.parametrize` block instead of three copy-pasted tests.
- **Stronger authorization semantics.** `/add-task-comment` intentionally returns `404 TASK_NOT_FOUND` (not `403`) when the task belongs to another user, avoiding existence leakage — documented explicitly above.

### API error handling

All JSON error responses use a single envelope (`error.code`, `error.message`, `error.httpStatus`, `error.details`). JWT failures use the same shape. See **[`docs/API_ERROR_HANDLING.md`](./docs/API_ERROR_HANDLING.md)** for the full policy, status/code catalog, and client guidance.

### Postman collection

Import [`postman/TodoApp-API.postman_collection.json`](./postman/TodoApp-API.postman_collection.json) into Postman (or compatible clients). The collection includes **saved example responses** (200/201/204/400/401/404/409), collection variables (`baseUrl`, `accessToken`, `userId`, `tagId`, `taskId`), and **Tests** scripts on **Register**, **Login**, **Create user**, **List tags**, and **List my tasks** to chain variables for protected routes.

Interactive OpenAPI docs are still available at `http://localhost:5000/docs` when the backend is running.

## Image gallery

### REST API Preview:

![PREVIEW](./preview/preview1.png)
![PREVIEW](./preview/preview2.png)

### Frontend Preview

![PREVIEW](./preview/preview3.png)
![PREVIEW](./preview/preview4.png)
![PREVIEW](./preview/preview5.png)
![PREVIEW](./preview/preview6.png)
![PREVIEW](./preview/preview7.png)
![PREVIEW](./preview/preview8.png)

### Developed by Santiago de Jesús Moraga Caldera - Remy349(GitHub)
