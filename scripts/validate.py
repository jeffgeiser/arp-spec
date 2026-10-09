#!/usr/bin/env python3
"""Validate the ARP JSON Schemas and example payloads.

Checks:
  1. Every schema/*.json is valid JSON and a valid JSON Schema for the draft
     it declares in "$schema".
  2. Every schema has a unique "$id".
  3. Every examples/*.json validates against its schema (mapping below).
  4. Every schema and every example is covered by the mapping, so a new file
     can't silently skip validation.

Usage: pip install -r requirements-dev.txt && python scripts/validate.py
Exit code 0 on success, 1 on any failure.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from jsonschema import validators

ROOT = Path(__file__).resolve().parent.parent

# example file -> schema file
EXAMPLES = {
    "01-sense-fleet-context.json": "fleet-context.json",
    "02-score-response.json": "score-response.json",
    "03-commit-intent.json": "workload-intent.json",
    "04-reconcile-receipt.json": "reconcile-receipt.json",
}


def load(path: Path):
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def main() -> int:
    errors: list[str] = []
    schemas: dict[str, dict] = {}
    ids: dict[str, str] = {}

    for path in sorted((ROOT / "schema").glob("*.json")):
        try:
            schema = load(path)
        except json.JSONDecodeError as e:
            errors.append(f"schema/{path.name}: invalid JSON: {e}")
            continue
        cls = validators.validator_for(schema)
        try:
            cls.check_schema(schema)
        except Exception as e:  # jsonschema.SchemaError
            errors.append(f"schema/{path.name}: invalid schema: {e.message if hasattr(e, 'message') else e}")
            continue
        sid = schema.get("$id")
        if not sid:
            errors.append(f"schema/{path.name}: missing $id")
        elif sid in ids:
            errors.append(f"schema/{path.name}: duplicate $id (also in {ids[sid]})")
        else:
            ids[sid] = path.name
        schemas[path.name] = schema
        print(f"ok   schema/{path.name}")

    example_files = {p.name for p in (ROOT / "examples").glob("*.json")}
    for name in sorted(example_files - EXAMPLES.keys()):
        errors.append(f"examples/{name}: no schema mapping in scripts/validate.py")
    for name in sorted(set(schemas) - set(EXAMPLES.values())):
        errors.append(f"schema/{name}: no example validates against it")

    for example, schema_name in EXAMPLES.items():
        path = ROOT / "examples" / example
        if not path.exists():
            errors.append(f"examples/{example}: missing")
            continue
        if schema_name not in schemas:
            errors.append(f"examples/{example}: schema {schema_name} missing or invalid")
            continue
        try:
            instance = load(path)
        except json.JSONDecodeError as e:
            errors.append(f"examples/{example}: invalid JSON: {e}")
            continue
        validator = validators.validator_for(schemas[schema_name])(schemas[schema_name])
        found = sorted(validator.iter_errors(instance), key=lambda e: list(e.path))
        for err in found:
            where = "/".join(str(p) for p in err.path) or "(root)"
            errors.append(f"examples/{example}: {where}: {err.message}")
        if not found:
            print(f"ok   examples/{example} against schema/{schema_name}")

    if errors:
        print("\nFAILED:", file=sys.stderr)
        for e in errors:
            print(f"  {e}", file=sys.stderr)
        return 1
    print("\nAll schemas and examples are valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
