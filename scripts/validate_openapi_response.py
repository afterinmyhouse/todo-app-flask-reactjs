#!/usr/bin/env python3
"""
Contract check for OpenAPI snippet:

  paths:
    /user:
      get:
        responses:
          '200':
            content:
              application/json:
                schema:
                  type: object
                  required: [id, username]
                  properties:
                    id: { type: integer }
                    username: { type: string }

Install: pip install -r scripts/requirements-contract.txt
Run:     python scripts/validate_openapi_response.py [path/to/response.json]
          (omit path to run built-in valid + invalid demos)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from jsonschema import Draft7Validator

# JSON Schema derived from the 200 response body above (Draft-7 compatible).
USER_200_SCHEMA: dict = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "GET /user 200 application/json",
    "type": "object",
    "required": ["id", "username"],
    "properties": {
        "id": {"type": "integer"},
        "username": {"type": "string"},
    },
    "additionalProperties": True,
}


def validate(instance: object) -> bool:
    validator = Draft7Validator(USER_200_SCHEMA)
    errors = sorted(validator.iter_errors(instance), key=lambda e: list(e.path))
    if not errors:
        print("PASS")
        return True
    print("FAIL")
    for err in errors:
        loc = "/".join(str(p) for p in err.absolute_path) or "(root)"
        print(f"  [{loc}] {err.message}")
        if err.context:
            for sub in err.context:
                sloc = "/".join(str(p) for p in sub.absolute_path) or "(root)"
                print(f"    [{sloc}] {sub.message}")
    return False


def main() -> int:
    if len(sys.argv) > 1:
        raw = Path(sys.argv[1]).read_text(encoding="utf-8")
        instance = json.loads(raw)
        ok = validate(instance)
        print(json.dumps(instance, indent=2))
        return 0 if ok else 1

    print("--- demo: valid payload ---")
    ok1 = validate({"id": 1, "username": "alice"})
    print("--- demo: invalid payload (wrong types + missing field) ---")
    ok2 = validate({"id": "not-int"})
    return 0 if ok1 and not ok2 else 1


if __name__ == "__main__":
    raise SystemExit(main())
