#!/usr/bin/env python3
"""JamesOS Prompt Forge v1.

Dependency-free prompt component store and assembler.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

BASE = Path(__file__).parent
FORGE_DIR = BASE / "state" / "prompt_forge"
COMPONENTS_FILE = FORGE_DIR / "components.json"
TEMPLATES_FILE = FORGE_DIR / "templates.json"
BUILDS_DIR = FORGE_DIR / "builds"

ALLOWED_TYPES = {
    "role",
    "context",
    "task",
    "constraint",
    "output_contract",
    "zip_rule",
    "validation_rule",
    "model_adapter",
}


@dataclass(frozen=True)
class Component:
    component_id: str
    component_type: str
    name: str
    content: str
    version: int = 1
    active: bool = True
    tags: tuple[str, ...] = ()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Component":
        component_type = str(data.get("component_type", "")).strip()
        if component_type not in ALLOWED_TYPES:
            raise ValueError(f"Invalid component_type: {component_type}")
        component_id = str(data.get("component_id", "")).strip()
        name = str(data.get("name", "")).strip()
        content = str(data.get("content", "")).strip()
        if not component_id or not name or not content:
            raise ValueError("component_id, name and content are required")
        return cls(
            component_id=component_id,
            component_type=component_type,
            name=name,
            content=content,
            version=int(data.get("version", 1)),
            active=bool(data.get("active", True)),
            tags=tuple(str(tag) for tag in data.get("tags", [])),
        )


class PromptForge:
    def __init__(self) -> None:
        self.ensure_store()
        self.components = self._load_json(COMPONENTS_FILE, {"components": []})["components"]
        self.templates = self._load_json(TEMPLATES_FILE, {"templates": []})["templates"]

    @staticmethod
    def _load_json(path: Path, default: dict[str, Any]) -> dict[str, Any]:
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(default, indent=2) + "\n", encoding="utf-8")
            return default
        return json.loads(path.read_text(encoding="utf-8"))

    @staticmethod
    def ensure_store() -> None:
        BUILDS_DIR.mkdir(parents=True, exist_ok=True)

    def validate(self) -> list[str]:
        errors: list[str] = []
        seen_ids: set[str] = set()
        for raw in self.components:
            try:
                component = Component.from_dict(raw)
                if component.component_id in seen_ids:
                    errors.append(f"Duplicate component_id: {component.component_id}")
                seen_ids.add(component.component_id)
            except (TypeError, ValueError) as exc:
                errors.append(str(exc))
        template_ids: set[str] = set()
        for template in self.templates:
            template_id = str(template.get("template_id", "")).strip()
            if not template_id:
                errors.append("Template missing template_id")
            elif template_id in template_ids:
                errors.append(f"Duplicate template_id: {template_id}")
            template_ids.add(template_id)
            for component_id in template.get("component_ids", []):
                if component_id not in seen_ids:
                    errors.append(f"Template {template_id} references missing component {component_id}")
        return errors

    def get_component(self, component_id: str) -> Component:
        for raw in self.components:
            if raw.get("component_id") == component_id:
                return Component.from_dict(raw)
        raise KeyError(f"Unknown component: {component_id}")

    def assemble(self, template_id: str, variables: dict[str, str] | None = None) -> str:
        variables = variables or {}
        template = next((item for item in self.templates if item.get("template_id") == template_id), None)
        if template is None:
            raise KeyError(f"Unknown template: {template_id}")
        sections: list[str] = []
        for component_id in template.get("component_ids", []):
            component = self.get_component(component_id)
            if not component.active:
                continue
            text = component.content
            for key, value in variables.items():
                text = text.replace("{{" + key + "}}", str(value))
            sections.append(text.strip())
        prompt = "\n\n".join(sections).strip() + "\n"
        output_name = str(template.get("output_name", template_id)) + ".md"
        (BUILDS_DIR / output_name).write_text(prompt, encoding="utf-8")
        return prompt

    def catalogue(self) -> list[dict[str, Any]]:
        return [
            {
                "component_id": item.get("component_id"),
                "component_type": item.get("component_type"),
                "name": item.get("name"),
                "version": item.get("version", 1),
                "active": item.get("active", True),
            }
            for item in self.components
        ]


if __name__ == "__main__":
    forge = PromptForge()
    problems = forge.validate()
    if problems:
        print("Prompt Forge validation failed:")
        for problem in problems:
            print("-", problem)
        raise SystemExit(1)
    print(f"Prompt Forge ready: {len(forge.components)} components, {len(forge.templates)} templates")
