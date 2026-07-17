#!/usr/bin/env python3
"""SQLite persistence for JamesOS Prompt Forge.

Dependency-free, repeat-safe, and designed to coexist with the v1 JSON store.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
import uuid
from pathlib import Path
from typing import Any, Iterable

BASE = Path(__file__).parent
FORGE_DIR = BASE / "state" / "prompt_forge"
DB_PATH = FORGE_DIR / "prompt_forge.sqlite3"
SCHEMA_PATH = FORGE_DIR / "schema.sql"
COMPONENTS_JSON = FORGE_DIR / "components.json"
TEMPLATES_JSON = FORGE_DIR / "templates.json"


def content_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


class PromptForgeRepository:
    def __init__(self, db_path: Path | str = DB_PATH) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def migrate(self) -> None:
        if not SCHEMA_PATH.exists():
            raise FileNotFoundError(f"Missing Prompt Forge schema: {SCHEMA_PATH}")
        with self.connect() as connection:
            connection.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))

    def seed_from_json(self) -> dict[str, int]:
        self.migrate()
        components = json.loads(COMPONENTS_JSON.read_text(encoding="utf-8")).get("components", [])
        templates = json.loads(TEMPLATES_JSON.read_text(encoding="utf-8")).get("templates", [])
        counts = {"components": 0, "templates": 0, "template_components": 0, "variables": 0, "tests": 0}
        with self.connect() as connection:
            for component in components:
                text = str(component["content"]).strip()
                connection.execute(
                    """
                    INSERT INTO forge_components(
                        component_id, version, component_type, name, content,
                        status, trust_status, source_kind, content_hash, change_note
                    ) VALUES (?, ?, ?, ?, ?, 'active', 'internal', 'internal', ?, ?)
                    ON CONFLICT(component_id, version) DO UPDATE SET
                        component_type=excluded.component_type,
                        name=excluded.name,
                        content=excluded.content,
                        content_hash=excluded.content_hash,
                        updated_at=CURRENT_TIMESTAMP
                    """,
                    (
                        component["component_id"], int(component.get("version", 1)),
                        component["component_type"], component["name"], text,
                        content_hash(text), "Seeded from components.json",
                    ),
                )
                counts["components"] += 1
                connection.execute(
                    "DELETE FROM forge_component_tags WHERE component_id=? AND component_version=?",
                    (component["component_id"], int(component.get("version", 1))),
                )
                for tag in sorted(set(component.get("tags", []))):
                    connection.execute(
                        "INSERT INTO forge_component_tags(component_id, component_version, tag) VALUES (?, ?, ?)",
                        (component["component_id"], int(component.get("version", 1)), str(tag)),
                    )

            component_versions = {
                row["component_id"]: row["version"]
                for row in connection.execute(
                    "SELECT component_id, MAX(version) AS version FROM forge_components GROUP BY component_id"
                )
            }
            for template in templates:
                template_id = template["template_id"]
                version = int(template.get("version", 1))
                target_model = template_id.split(".", 1)[0] if "." in template_id else None
                connection.execute(
                    """
                    INSERT INTO forge_templates(
                        template_id, version, name, description, target_model,
                        output_name, status
                    ) VALUES (?, ?, ?, ?, ?, ?, 'active')
                    ON CONFLICT(template_id, version) DO UPDATE SET
                        name=excluded.name,
                        description=excluded.description,
                        target_model=excluded.target_model,
                        output_name=excluded.output_name,
                        updated_at=CURRENT_TIMESTAMP
                    """,
                    (
                        template_id, version, template["name"],
                        template.get("description", ""), target_model,
                        template.get("output_name", template_id),
                    ),
                )
                counts["templates"] += 1
                connection.execute(
                    "DELETE FROM forge_template_components WHERE template_id=? AND template_version=?",
                    (template_id, version),
                )
                for position, component_id in enumerate(template.get("component_ids", [])):
                    component_version = component_versions.get(component_id)
                    if component_version is None:
                        raise ValueError(f"Template {template_id} references missing component {component_id}")
                    connection.execute(
                        """
                        INSERT INTO forge_template_components(
                            template_id, template_version, position,
                            component_id, component_version, required
                        ) VALUES (?, ?, ?, ?, ?, 1)
                        """,
                        (template_id, version, position, component_id, component_version),
                    )
                    counts["template_components"] += 1
                variables = self._extract_variables(
                    connection, template_id, version
                )
                for variable in variables:
                    connection.execute(
                        """
                        INSERT OR IGNORE INTO forge_template_variables(
                            template_id, template_version, variable_name,
                            description, required
                        ) VALUES (?, ?, ?, ?, 1)
                        """,
                        (template_id, version, variable, f"Value for {{{{{variable}}}}}"),
                    )
                    counts["variables"] += 1
                test_id = f"seed.{template_id}.required-sections"
                required_markers = ["# ROLE", "# TASK", "# VALIDATION", "# OUTPUT CONTRACT"]
                connection.execute(
                    """
                    INSERT INTO forge_test_cases(
                        test_case_id, name, template_id, template_version,
                        variables_json, expected_contains_json,
                        forbidden_contains_json, expected_min_length, active
                    ) VALUES (?, ?, ?, ?, ?, ?, '[]', 200, 1)
                    ON CONFLICT(test_case_id) DO UPDATE SET
                        variables_json=excluded.variables_json,
                        expected_contains_json=excluded.expected_contains_json,
                        active=1
                    """,
                    (
                        test_id, f"{template['name']} contains required sections",
                        template_id, version,
                        canonical_json({name: f"TEST_{name.upper()}" for name in variables}),
                        canonical_json(required_markers),
                    ),
                )
                counts["tests"] += 1
        return counts

    @staticmethod
    def _extract_variables(
        connection: sqlite3.Connection, template_id: str, template_version: int
    ) -> list[str]:
        variables: set[str] = set()
        rows = connection.execute(
            """
            SELECT c.content
            FROM forge_template_components tc
            JOIN forge_components c
              ON c.component_id=tc.component_id AND c.version=tc.component_version
            WHERE tc.template_id=? AND tc.template_version=?
            ORDER BY tc.position
            """,
            (template_id, template_version),
        )
        for row in rows:
            text = row["content"]
            start = 0
            while True:
                left = text.find("{{", start)
                if left < 0:
                    break
                right = text.find("}}", left + 2)
                if right < 0:
                    break
                name = text[left + 2:right].strip()
                if name:
                    variables.add(name)
                start = right + 2
        return sorted(variables)

    def catalogue(self) -> list[dict[str, Any]]:
        self.migrate()
        with self.connect() as connection:
            return [dict(row) for row in connection.execute(
                """
                SELECT component_id, version, component_type, name, status,
                       trust_status, source_kind, content_hash, updated_at
                FROM forge_components
                ORDER BY component_type, component_id, version DESC
                """
            )]

    def assemble(self, template_id: str, variables: dict[str, str]) -> tuple[str, str]:
        self.migrate()
        with self.connect() as connection:
            template = connection.execute(
                """
                SELECT * FROM forge_templates
                WHERE template_id=? AND status='active'
                ORDER BY version DESC LIMIT 1
                """,
                (template_id,),
            ).fetchone()
            if template is None:
                raise KeyError(f"Unknown active template: {template_id}")
            required = connection.execute(
                """
                SELECT variable_name, default_value, required
                FROM forge_template_variables
                WHERE template_id=? AND template_version=?
                """,
                (template_id, template["version"]),
            ).fetchall()
            resolved = dict(variables)
            missing: list[str] = []
            for item in required:
                if not resolved.get(item["variable_name"]):
                    if item["default_value"] is not None:
                        resolved[item["variable_name"]] = item["default_value"]
                    elif item["required"]:
                        missing.append(item["variable_name"])
            if missing:
                raise ValueError("Missing template variables: " + ", ".join(sorted(missing)))
            rows = connection.execute(
                """
                SELECT tc.position, c.component_id, c.version, c.content, c.content_hash
                FROM forge_template_components tc
                JOIN forge_components c
                  ON c.component_id=tc.component_id AND c.version=tc.component_version
                WHERE tc.template_id=? AND tc.template_version=? AND c.status='active'
                ORDER BY tc.position
                """,
                (template_id, template["version"]),
            ).fetchall()
            sections: list[str] = []
            for row in rows:
                text = row["content"]
                for key, value in resolved.items():
                    text = text.replace("{{" + key + "}}", str(value))
                sections.append(text.strip())
            prompt = "\n\n".join(sections).strip() + "\n"
            build_id = "build-" + uuid.uuid4().hex
            rendered_hash = content_hash(prompt)
            connection.execute(
                """
                INSERT INTO forge_builds(
                    build_id, template_id, template_version, target_model,
                    variables_json, rendered_prompt, rendered_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    build_id, template_id, template["version"], template["target_model"],
                    canonical_json(resolved), prompt, rendered_hash,
                ),
            )
            for row in rows:
                connection.execute(
                    """
                    INSERT INTO forge_build_components(
                        build_id, position, component_id, component_version, content_hash
                    ) VALUES (?, ?, ?, ?, ?)
                    """,
                    (build_id, row["position"], row["component_id"], row["version"], row["content_hash"]),
                )
            return build_id, prompt

    def validate_database(self) -> list[str]:
        self.migrate()
        errors: list[str] = []
        with self.connect() as connection:
            foreign_key_errors = list(connection.execute("PRAGMA foreign_key_check"))
            for row in foreign_key_errors:
                errors.append(f"Foreign key failure: {tuple(row)}")
            duplicates = connection.execute(
                """
                SELECT content_hash, COUNT(*) AS count
                FROM forge_components
                WHERE status='active'
                GROUP BY content_hash HAVING COUNT(*) > 1
                """
            ).fetchall()
            for row in duplicates:
                errors.append(f"Duplicate active component content hash: {row['content_hash']}")
            broken_templates = connection.execute(
                """
                SELECT t.template_id, t.version
                FROM forge_templates t
                LEFT JOIN forge_template_components tc
                  ON tc.template_id=t.template_id AND tc.template_version=t.version
                WHERE t.status='active'
                GROUP BY t.template_id, t.version
                HAVING COUNT(tc.component_id)=0
                """
            ).fetchall()
            for row in broken_templates:
                errors.append(f"Active template has no components: {row['template_id']} v{row['version']}")
        return errors

    def run_seed_tests(self) -> dict[str, int]:
        self.migrate()
        totals = {"passed": 0, "failed": 0}
        with self.connect() as connection:
            cases = connection.execute(
                "SELECT * FROM forge_test_cases WHERE active=1 ORDER BY test_case_id"
            ).fetchall()
        for case in cases:
            variables = json.loads(case["variables_json"])
            build_id, prompt = self.assemble(case["template_id"], variables)
            failures: list[str] = []
            if len(prompt) < case["expected_min_length"]:
                failures.append(f"Prompt shorter than {case['expected_min_length']} characters")
            for marker in json.loads(case["expected_contains_json"]):
                if marker not in prompt:
                    failures.append(f"Missing required marker: {marker}")
            for marker in json.loads(case["forbidden_contains_json"]):
                if marker in prompt:
                    failures.append(f"Contains forbidden marker: {marker}")
            passed = not failures
            with self.connect() as connection:
                connection.execute(
                    """
                    INSERT INTO forge_test_runs(
                        test_run_id, test_case_id, build_id, passed, failure_details
                    ) VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        "test-run-" + uuid.uuid4().hex, case["test_case_id"], build_id,
                        1 if passed else 0, "\n".join(failures) if failures else None,
                    ),
                )
            totals["passed" if passed else "failed"] += 1
        return totals


def initialise() -> dict[str, Any]:
    repository = PromptForgeRepository()
    seeded = repository.seed_from_json()
    errors = repository.validate_database()
    tests = repository.run_seed_tests() if not errors else {"passed": 0, "failed": 0}
    return {"database": str(repository.db_path), "seeded": seeded, "errors": errors, "tests": tests}


if __name__ == "__main__":
    result = initialise()
    print(json.dumps(result, indent=2))
    raise SystemExit(1 if result["errors"] or result["tests"]["failed"] else 0)
