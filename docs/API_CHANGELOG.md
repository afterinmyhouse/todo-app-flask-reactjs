# API Additions Changelog

This file tracks endpoint additions implemented via the "API Addition End-to-End"
GenAI workflow. Each entry records the new endpoint plus the concrete quality
and speed improvements made over the previous iteration, so the pattern keeps
getting better instead of just repeating itself.

## Run 1 — `POST /api/v1/add-project`

Baseline pattern established:

- `flask-smorest` `Blueprint` + `MethodView` per resource.
- JWT-protected route via `@jwt_required()`.
- Marshmallow `Plain*Schema` → `*Schema` split (mirrors existing codebase convention).
- Controller persists to MongoDB via `flaskr.mongo.get_db()`.
- Errors flow through `flaskr.errors.api_abort` with the single JSON envelope.
- First-ever backend pytest suite (`backend/tests/`) with an in-memory fake
  Mongo collection, `Authorization` header fixture, and five test cases
  (success, duplicate, validation, missing auth, invalid token subject).
- README gained a per-endpoint section with cURL + response examples.
- Postman collection gained a `Projects` folder with saved examples.

Known rough edges that Run 2 addressed:

1. The `try/except InvalidId` block for parsing the JWT subject was
   duplicated in every controller.
2. `conftest.py` hard-coded a `FakeProjectsCollection`; adding a new
   endpoint meant editing the fixture.
3. The `fake_db` fixture monkeypatched `project_controller.get_db`
   directly — every new controller would need its own `setattr` line.
4. The `app` fixture was function-scoped; it was cheap at 5 tests but
   scales linearly.
5. Three near-identical "missing required field" tests could be collapsed.

## Run 2 — `POST /api/v1/add-task-comment`

New endpoint lets the authenticated user comment on a task they own.

### Behavior

- Request: `{ "taskId": "<ObjectId>", "body": "<1..2000 chars>" }`.
- Validates ObjectId format (`400 INVALID_TASK`).
- Verifies task ownership via a single `find_one({_id, user_id})` query.
  Returns `404 TASK_NOT_FOUND` when the task is absent *or* owned by
  another user — chosen deliberately to avoid leaking existence.
- Trims body and rejects all-whitespace input as `422 VALIDATION_ERROR`.
- Persists `{task_id, user_id, body, created_at}` to the
  `task_comments` collection.
- Returns `201` with `{id, taskId, body, createdAt}`.

### Quality improvements over Run 1

| Area | Run 1 | Run 2 | Impact |
|---|---|---|---|
| Auth plumbing | Inline `try/except InvalidId` per controller | `resolve_user_oid()` + `parse_object_id()` in `flaskr.utils` | ~12 lines of duplicated code removed; any future controller reuses the helpers |
| Mongo patching for tests | `monkeypatch.setattr(project_controller, "get_db", ...)` — per-controller | Controllers call `mongo.get_db()`; tests patch `flaskr.mongo.get_db` once | Adding a new endpoint requires zero changes to `conftest.py` |
| Fake collections | Hand-written `FakeProjectsCollection` | `FakeDb.__getattr__` auto-provisions `FakeCollection` on access | New collections (`tasks`, `task_comments`, …) work out of the box |
| `app` fixture scope | function | session | Constant-time suite startup as endpoint count grows |
| Validation tests | 1 hand-written test per missing field | `pytest.mark.parametrize` over 3 cases with readable `ids=` | Fewer LOC, richer output |
| Authorization semantics | Not applicable (resource was per-user only by construction) | Explicit `404` on cross-user access, documented in README | Prevents existence-leak side channel |
| OpenAPI docs | Generic route docstring | Action-describing docstring ("Create a comment on a task owned by the caller") | Swagger UI renders useful summary |

### Measured impact

- Test count: 5 → 15 across both endpoints.
- Suite runtime: ~0.06s (session-scoped app keeps this flat).
- Net code delta in shared infra: `flaskr/utils.py` +2 helpers, `tests/conftest.py` reduced boilerplate per endpoint to zero.

## Repeatable Workflow for Future Endpoints

Use this checklist when adding the next `POST /add-*` endpoint — it captures
the pattern both runs converged on.

1. **Plan**
   - Pick the resource, the auth requirement, the uniqueness rules, and the
     authorization semantics (own-only? 404 vs 403 on cross-tenant access?).
   - Identify the new Mongo collection name.
   - Identify any new `ErrorCode` constants needed (e.g. `INVALID_TASK`,
     `<RESOURCE>_EXISTS`).

2. **Schema**
   - Add `PlainCreate<Resource>Schema` in `flaskr/schemas/plain_schema.py`
     with Marshmallow `validate.Length`, `data_key` for camelCase over the
     wire, and `load_default` for optional fields.
   - Re-export `Create<Resource>Schema` and a dump-only `<Resource>Schema`
     in `flaskr/schemas/schema.py`.

3. **Controller**
   - `from flaskr import mongo` and call `mongo.get_db()` (never
     `from flaskr.mongo import get_db` at module level — it breaks patching).
   - Use `resolve_user_oid()` for JWT subject parsing.
   - Use `parse_object_id(value, http_status=..., error_code=..., ...)` for
     any ObjectId field in the payload.
   - Combine existence + ownership checks into one `find_one` query when
     possible, and prefer `404` over `403` unless the resource is public.
   - Trim user-supplied strings; reject all-whitespace input as `422`.

4. **Route**
   - `Blueprint` + `MethodView` under `/api/v1/add-<resource>`.
   - Stack: `@jwt_required()` → `@bp.arguments(...)` → `@bp.response(201, <Schema>)`.
   - Register the blueprint in `flaskr/__init__.py`.

5. **Errors**
   - Add any new `ErrorCode` constants; keep messages short and stable —
     clients match on `code`, not `message`.

6. **Tests**
   - Reuse the shared `client`, `fake_db`, and `auth_header` fixtures.
   - At minimum cover: success, authorization failure, missing-auth,
     invalid-token-subject, validation (parametrized), and any
     resource-specific conflict/ownership case.

7. **Docs**
   - Add a row to the route table in `README.md`.
   - Add a per-endpoint subsection with cURL + success + error-code list.
   - Append an entry to this file summarizing what got better.

8. **Postman**
   - Add a folder named after the resource with a `Create <resource>`
     request, saved `201` example, plus the relevant error examples
     (`401`, `404`, `409`, `422`).

9. **Verify**
   - `python -m pytest tests -q`
   - `ReadLints` over touched files.
   - `python -c "import json, pathlib; json.loads(pathlib.Path('postman/TodoApp-API.postman_collection.json').read_text(encoding='utf-8'))"`
