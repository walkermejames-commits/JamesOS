import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from prompt_forge_db import PromptForgeRepository, content_hash


class PromptForgeDatabaseTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tempdir.name) / "forge.sqlite3"
        self.repository = PromptForgeRepository(self.db_path)
        self.seed_counts = self.repository.seed_from_json()

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_seed_is_repeat_safe(self) -> None:
        second = self.repository.seed_from_json()
        self.assertEqual(self.seed_counts["components"], second["components"])
        with self.repository.connect() as connection:
            component_count = connection.execute(
                "SELECT COUNT(*) FROM forge_components"
            ).fetchone()[0]
            template_count = connection.execute(
                "SELECT COUNT(*) FROM forge_templates"
            ).fetchone()[0]
        self.assertEqual(component_count, self.seed_counts["components"])
        self.assertEqual(template_count, self.seed_counts["templates"])

    def test_schema_has_no_foreign_key_failures(self) -> None:
        self.assertEqual(self.repository.validate_database(), [])
        with self.repository.connect() as connection:
            self.assertEqual(list(connection.execute("PRAGMA foreign_key_check")), [])

    def test_catalogue_contains_version_and_provenance(self) -> None:
        catalogue = self.repository.catalogue()
        self.assertGreaterEqual(len(catalogue), 9)
        first = catalogue[0]
        self.assertIn("version", first)
        self.assertIn("trust_status", first)
        self.assertIn("source_kind", first)
        self.assertEqual(len(first["content_hash"]), 64)

    def test_assemble_requires_all_variables(self) -> None:
        with self.assertRaises(ValueError) as error:
            self.repository.assemble("codex.production_task", {"project_name": "Evidence Core"})
        self.assertIn("Missing template variables", str(error.exception))

    def test_assemble_records_build_provenance(self) -> None:
        variables = {
            "project_name": "Evidence Transcript Core",
            "repository": "walkermejames-commits/evidence-transcript-core",
            "module": "ECS Batch 002",
            "objective": "Match statutory sources",
            "architecture": "Electron, FastAPI, SQLite",
            "task": "Complete controlled source matching.",
        }
        build_id, prompt = self.repository.assemble("codex.production_task", variables)
        self.assertIn("# ROLE", prompt)
        self.assertIn("# TASK", prompt)
        self.assertNotIn("{{project_name}}", prompt)
        with self.repository.connect() as connection:
            build = connection.execute(
                "SELECT * FROM forge_builds WHERE build_id=?", (build_id,)
            ).fetchone()
            components = connection.execute(
                "SELECT COUNT(*) FROM forge_build_components WHERE build_id=?", (build_id,)
            ).fetchone()[0]
        self.assertEqual(build["rendered_hash"], content_hash(prompt))
        self.assertGreater(components, 0)
        self.assertEqual(json.loads(build["variables_json"])["module"], "ECS Batch 002")

    def test_seed_test_cases_pass(self) -> None:
        result = self.repository.run_seed_tests()
        self.assertGreaterEqual(result["passed"], 2)
        self.assertEqual(result["failed"], 0)

    def test_duplicate_active_component_content_is_reported(self) -> None:
        with self.repository.connect() as connection:
            original = connection.execute(
                "SELECT * FROM forge_components ORDER BY component_id LIMIT 1"
            ).fetchone()
            connection.execute(
                """
                INSERT INTO forge_components(
                    component_id, version, component_type, name, content,
                    status, trust_status, source_kind, content_hash
                ) VALUES ('duplicate.test', 1, 'context', 'Duplicate', ?,
                          'active', 'internal', 'internal', ?)
                """,
                (original["content"], original["content_hash"]),
            )
        errors = self.repository.validate_database()
        self.assertTrue(any("Duplicate active component" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
