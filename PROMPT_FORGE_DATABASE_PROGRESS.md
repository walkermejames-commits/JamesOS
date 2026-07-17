# JamesOS Prompt Forge Database Progress

## Delivered in this database batch

Prompt Forge now has a relational SQLite foundation alongside the original JSON seed library.

### Database coverage

- immutable versioned prompt components
- component tags
- versioned templates
- ordered template-component relationships
- required template variables
- prompt build history
- exact component snapshots for each build
- deterministic SHA-256 content hashes
- reusable prompt test cases and test runs
- outcome and instruction-following ratings
- import batches and quarantined import items
- schema version ledger
- practical indexes for catalogue, build history, tests, ratings and duplicate detection

### Files

- `state/prompt_forge/schema.sql`
- `prompt_forge_db.py`
- `tests/test_prompt_forge_db.py`

### Initial seed behaviour

`python prompt_forge_db.py` performs a repeat-safe migration from:

- `state/prompt_forge/components.json`
- `state/prompt_forge/templates.json`

It also discovers template variables, creates baseline test cases, validates foreign keys and duplicate active component content, assembles test builds, and records test results.

### Trust model

Imported prompts do not become trusted components automatically.

`trust_status` values:

- `internal`
- `imported_unreviewed`
- `reviewed`
- `certified`

`source_kind` values:

- `internal`
- `prompts_chat`
- `manual_import`
- `generated`

External material enters `forge_import_items` with a review decision. It must be accepted and mapped deliberately before it can become an active component.

## Next Codex implementation prompt

```text
Continue Prompt Forge on branch feature/prompt-forge-v1 in walkermejames-commits/JamesOS.

Inspect the existing repository and the new relational files before editing:

- prompt_forge.py
- prompt_forge_db.py
- state/prompt_forge/schema.sql
- state/prompt_forge/components.json
- state/prompt_forge/templates.json
- tests/test_prompt_forge_db.py

Do not replace the SQLite design or remove JSON backward compatibility.

Implement the Prompt Forge CLI and controlled import batch.

Required CLI commands in james.py:

1. forge-init
   - migrate and seed the SQLite database
   - print component, template, variable and test counts
   - exit non-zero on validation or test failure

2. forge-list [--type TYPE] [--tag TAG] [--status STATUS]
   - list components from SQLite
   - show ID, version, type, trust status, source kind and tags

3. forge-templates
   - list active templates and required variables

4. forge-build TEMPLATE_ID key=value ...
   - reject malformed key=value arguments
   - reject missing required variables
   - assemble from the exact stored component versions
   - save Markdown under state/prompt_forge/builds/
   - update forge_builds.output_path
   - print build ID and SHA-256 hash

5. forge-test
   - run all active forge_test_cases
   - persist forge_test_runs
   - print passed and failed totals
   - exit non-zero on failure

6. forge-validate
   - run foreign-key, duplicate-content, empty-template, unresolved-variable and missing-build-file checks

7. forge-history [TEMPLATE_ID]
   - show recent builds and ratings

Controlled prompts.chat import:

- add scripts/import_prompts_chat.py
- accept local JSON or CSV input only in this batch
- do not fetch the internet from the application
- create forge_import_batches and forge_import_items
- normalise whitespace before hashing
- detect duplicate content against imports and active components
- never activate imported material automatically
- require an explicit review decision before mapping to forge_components
- preserve original raw content and source reference

Add review commands:

- forge-import-list [BATCH_ID]
- forge-import-review IMPORT_ITEM_ID accept|reject COMPONENT_TYPE [COMPONENT_ID]

On acceptance:

- create a new draft component with trust_status imported_unreviewed
- preserve the import relationship and content hash
- do not add the component to a template automatically

Add tests proving:

- CLI initialisation is repeat-safe
- missing variables block builds
- builds preserve exact component versions
- build files and database hashes agree
- duplicate imported prompts are marked duplicate
- imported prompts never become active automatically
- rejection preserves the raw import item
- acceptance creates a draft imported_unreviewed component
- malformed imports fail without partial commits
- CLI returns non-zero on failed validation or tests

Run:

python -m unittest discover -s tests -p "test_*.py" -v
python prompt_forge_db.py
python james.py forge-init
python james.py forge-validate
python james.py forge-test

Update PROMPT_FORGE_V1.md with exact commands and migration guidance.

Return files changed, database counts, tests run, test results, limitations and the next implementation slice.
Do not touch unrelated project-control files.
```

## Recommended following slice

After CLI and imports, build the Prompt Forge review desk:

- side-by-side component version comparison
- template editor
- build replay
- rating capture
- test-result dashboard
- model-specific performance comparison
- approval workflow for imported prompts

That is the point where Prompt Forge becomes a reusable JamesOS product rather than only a developer utility.
