# JamesOS Prompt Forge v1

Prompt Forge is a dependency-free prompt component store and assembler for JamesOS.

## Purpose

Prompt Forge turns repeated prompt-writing into a small composition system. A finished prompt is assembled from reusable, versioned components instead of copied from a growing text graveyard.

## Component types

- `role`
- `context`
- `task`
- `constraint`
- `output_contract`
- `zip_rule`
- `validation_rule`
- `model_adapter`

## Storage

Prompt Forge v1 stores data in:

```text
state/prompt_forge/components.json
state/prompt_forge/templates.json
state/prompt_forge/builds/
```

This matches the current JamesOS local-first, dependency-free architecture.

## Engine

`prompt_forge.py` provides:

- component validation
- duplicate-ID checks
- template-reference checks
- variable substitution using `{{variable_name}}`
- deterministic prompt assembly
- saved Markdown builds
- component catalogue output

Run validation with:

```bash
python prompt_forge.py
```

Example assembly from Python:

```python
from prompt_forge import PromptForge

forge = PromptForge()
prompt = forge.assemble(
    "codex.production_task",
    {
        "project_name": "Evidence Transcript Core",
        "repository": "walkermejames-commits/evidence-transcript-core",
        "module": "ECS source matching",
        "objective": "Complete Batch 002",
        "architecture": "Electron, FastAPI, SQLite",
        "task": "Match SHPO statutory records against exact official sources."
    },
)
print(prompt)
```

## Starter library

The seed library includes:

- production engineer role
- JamesOS project context
- variable task block
- safe-extension constraints
- delivery summary contract
- standard ZIP packaging contract
- strict validation rules
- Codex adapter
- Grok research adapter

Starter templates:

- `codex.production_task`
- `grok.research_pack`

## Data principles

1. Components have stable IDs and explicit versions.
2. Templates reference component IDs rather than copying component text.
3. Model-specific behaviour belongs in adapters.
4. Validation and packaging remain separate reusable blocks.
5. Generated prompts are saved, making prompt history inspectable.
6. Imported prompt libraries should enter as untrusted source material, not overwrite JamesOS components.

## Next build slice

Integrate commands into `james.py`:

```text
python james.py forge-list
python james.py forge-validate
python james.py forge-build TEMPLATE_ID key=value ...
```

Then add prompt build history, component provenance, ratings, test cases, and an import adapter for prompts.chat.
