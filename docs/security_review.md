# Security Review – Backend Authentication Flow

**Scope:** Flask backend under `backend/`, covering JWT issuance (`/api/v1/auth/login`, `/auth/sign-in`, `/auth/register`), JWT consumption (`@jwt_required()`, `get_jwt_identity()`), password storage, related user routes, and global JWT/CORS wiring.

**Out of scope:** Frontend token storage (localStorage vs cookies), TLS termination, infrastructure hardening—only noted where they amplify backend risks.

---

## Architecture Summary

| Component | Role |
|-----------|------|
| `AuthController` | Validates credentials against MongoDB `users`, returns JWT via `create_access_token(identity=str(user["_id"]))`. |
| `flask_jwt_extended` | HS256-style signed JWTs; expiry from `JWT_ACCESS_TOKEN_EXPIRES` (4 hours). |
| `config.Config` | `JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")`; no default. |
| `extensions.py` | Normalizes JWT error responses to JSON envelope. |
| `UserController.create` | Used by `/auth/register` and unauthenticated `POST /api/v1/users`. |
| `werkzeug.security` | `generate_password_hash` / `check_password_hash` for passwords. |

---

## Identified Issues

### 1. Missing or weak `JWT_SECRET_KEY` (critical)

- **Description:** `JWT_SECRET_KEY` is read from the environment with no startup guarantee it is set or strong. If unset, Flask-JWT-Extended behavior is unsafe for production (weak or predictable signing material depending on version/fallback).
- **Why it is a vulnerability:** Anyone who can forge or brute-force signing material can mint valid tokens for arbitrary user ids (`sub`), gaining full API access without credentials.
- **Impact:** Complete authentication bypass, data breach, account takeover.

### 2. No rate limiting on authentication endpoints (high)

- **Description:** `POST /auth/login`, `/auth/sign-in`, and `/auth/register` accept unlimited requests per IP or identity.
- **Why it is a vulnerability:** Enables online password guessing, credential stuffing, and registration abuse without meaningful cost to the attacker.
- **Impact:** Account compromise, service degradation, storage/ops cost from mass fake signups.

### 3. Login timing and workload skew (medium)

- **Description:** `AuthController.login` looks up the user by email, then verifies the password only if a row exists (`user is None or check_password(...)`). When the user does not exist, the handler skips `check_password_hash` (expensive KDF work).
- **Why it is a vulnerability:** Response time and CPU patterns can correlate with “email exists in database,” weakening the uniform “Incorrect credentials” message for **user enumeration**.
- **Impact:** Targeted phishing or password attacks against known-valid emails.

### 4. Weak password policy on registration (medium)

- **Description:** `PlainRegisterSchema` allows `password` with `validate.Length(min=1)` only—no complexity or maximum bound aligned with hash DoS limits.
- **Why it is a vulnerability:** Users can choose trivial passwords; extremely long passwords can stress hashing (mitigated somewhat by Werkzeug, but policy is still weak).
- **Impact:** Faster offline cracking if hashes leak; weaker account resistance to guessing.

### 5. Account / email enumeration on registration (medium)

- **Description:** `UserController.create` returns distinct `409` responses for `USERNAME_TAKEN` vs `EMAIL_TAKEN` with different `details.field`.
- **Why it is a vulnerability:** Attackers learn whether a username or email is already registered before attempting login or social engineering.
- **Impact:** Privacy loss; more effective targeted attacks.

### 6. Duplicate registration surface (`POST /users` without JWT) (medium)

- **Description:** `POST /api/v1/users` invokes `UserController.create` with **no** `@jwt_required()`, same as public `/auth/register`.
- **Why it is a vulnerability:** Doubles unauthenticated signup attack surface; any middleware or monitoring applied only to `/auth/register` may be bypassed.
- **Impact:** Inconsistent security posture; harder governance of self-signup.

### 7. Email normalization inconsistency (medium)

- **Description:** Registration validates `email` with Marshmallow `Email`, but login uses `PlainSignInSchema` with `email = fields.Str` (no format validation) and stores/query emails as provided. MongoDB comparisons are case-sensitive and do not normalize `+tag` semantics.
- **Why it is a vulnerability:** Users may accidentally create near-duplicate accounts (`User@x.com` vs `user@x.com`) or fail login while believing the account exists; some addresses may be surprising to downstream systems.
- **Impact:** Support burden, possible logic bugs, slight aid to confusion-based attacks.

### 8. Long-lived access token without refresh or revocation (medium)

- **Description:** Single access token, `timedelta(hours=4)`, no refresh token, no server-side denylist on logout or password change.
- **Why it is a vulnerability:** Stolen token remains valid until expiry; compromised sessions cannot be cut short without rotating global signing keys (invalidating all users).
- **Impact:** Extended window for abuse after XSS, malware, or device theft.

### 9. CORS defaults not tightened in code (low–medium, context-dependent)

- **Description:** `cors.init_app(app)` is called without explicit `resources` / `origins`. Default behavior allows broad cross-origin access patterns typical of development defaults.
- **Why it is a vulnerability:** In production, overly permissive CORS can combine with other flaws (e.g., token exfiltration via malicious sites) to increase exposure.
- **Impact:** Depends on deployment; should be explicitly restricted to trusted frontend origins when using browser clients.

### 10. OpenAPI / Swagger exposure (informational)

- **Description:** `OPENAPI_SWAGGER_UI_PATH = "/docs"` advertises auth endpoints and shapes.
- **Why it is a concern:** Aids attackers in mapping the API; not a direct auth bypass.
- **Impact:** Slightly reduced obscurity; disable or protect in production if desired.

---

## Implemented Mitigation (Issue #1)

**Goal:** Fail closed in non-test environments unless a sufficiently long `JWT_SECRET_KEY` is configured, so the application never runs in a dangerously ambiguous signing state.

**Steps (already applied in codebase):**

1. After `app.config.from_object(...)`, evaluate `app.config.get("TESTING")` and `app.config.get("JWT_SECRET_KEY")`.
2. If **not** in `TESTING` mode, require a non-empty secret whose string length is at least **32** characters (aligned with common HMAC key guidance).
3. If the check fails, raise `RuntimeError` with an actionable message pointing to `secrets.token_urlsafe(32)`.
4. Keep tests passing by ensuring the test app config sets `TESTING = True` (existing `_TestConfig` in `conftest.py`) so short dev secrets like `test-secret` remain valid only under tests.

**Reference implementation** (`backend/flaskr/__init__.py`):

```python
    jwt_secret = app.config.get("JWT_SECRET_KEY")
    if not app.config.get("TESTING"):
        if not jwt_secret or len(str(jwt_secret).strip()) < 32:
            raise RuntimeError(
                "JWT_SECRET_KEY must be set to a strong value (at least 32 characters). "
                'Generate one with: python -c "import secrets; print(secrets.token_urlsafe(32))"'
            )
```

**Operational checklist:**

1. Add `JWT_SECRET_KEY` to `.env` (never commit `.env`).
2. Use a cryptographically random value (≥ 32 characters).
3. Rotate the key if leaked; understand rotation invalidates all outstanding JWTs until clients re-authenticate.

---

## Recommended Next Steps (Other Issues)

| Priority | Issue | Action |
|----------|-------|--------|
| High | Rate limiting | Add `Flask-Limiter` (or API gateway limits) keyed by IP + optional `email` for login/register; return `429` with backoff headers. |
| Medium | Timing enumeration | Always run a **dummy** `check_password_hash` on a fixed stored sentinel when the user is missing (constant-time compare path length), or use a single “verify” abstraction that takes constant wall time. |
| Medium | Password policy | Raise `min` length (e.g. 12+), add optional complexity rules, and cap max length (e.g. 128) to match KDF limits. |
| Medium | Enumeration on register | Return generic `409` (“Registration could not be completed”) without revealing which field collided; log specifics server-side only. |
| Medium | `/users` POST | Require admin JWT or remove public `POST /users` in favor of `/auth/register` only. |
| Medium | Email handling | Normalize with `email.lower().strip()` before storage and lookup; consider canonicalization policy for `+` addresses. |
| Medium | Token lifecycle | Introduce short-lived access tokens + refresh tokens (httpOnly, Secure, SameSite cookies) or opaque server-side sessions; add logout denylist if needed. |
| Low | CORS | Set `origins=[...]` explicitly for known frontends; avoid `*` with credentials. |

---

## Summary

The authentication design correctly uses password hashing, uniform login error messaging, and JWT for stateless auth. The highest-severity gap was **unenforced signing key strength and presence** in runnable (non-test) configurations; that is now mitigated in `create_app`. Remaining items—especially **rate limiting**, **timing-safe login**, and **token lifecycle**—should be prioritized based on threat model and exposure (public internet vs internal).

**Document version:** 1.0  
**Related code:** `backend/flaskr/controllers/auth_controller.py`, `backend/flaskr/routes/auth_route.py`, `backend/config.py`, `backend/flaskr/extensions.py`, `backend/flaskr/__init__.py`
