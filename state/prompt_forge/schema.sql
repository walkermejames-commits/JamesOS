PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS forge_schema_versions (
    version INTEGER PRIMARY KEY,
    description TEXT NOT NULL,
    applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS forge_components (
    component_id TEXT NOT NULL,
    version INTEGER NOT NULL CHECK (version > 0),
    component_type TEXT NOT NULL CHECK (component_type IN (
        'role','context','task','constraint','output_contract',
        'zip_rule','validation_rule','model_adapter'
    )),
    name TEXT NOT NULL,
    content TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft','active','deprecated','rejected')),
    trust_status TEXT NOT NULL DEFAULT 'internal' CHECK (trust_status IN ('internal','imported_unreviewed','reviewed','certified')),
    source_kind TEXT NOT NULL DEFAULT 'internal' CHECK (source_kind IN ('internal','prompts_chat','manual_import','generated')),
    source_reference TEXT,
    author TEXT,
    change_note TEXT,
    content_hash TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (component_id, version)
);

CREATE TABLE IF NOT EXISTS forge_component_tags (
    component_id TEXT NOT NULL,
    component_version INTEGER NOT NULL,
    tag TEXT NOT NULL,
    PRIMARY KEY (component_id, component_version, tag),
    FOREIGN KEY (component_id, component_version)
      REFERENCES forge_components(component_id, version) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS forge_templates (
    template_id TEXT NOT NULL,
    version INTEGER NOT NULL CHECK (version > 0),
    name TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    target_model TEXT,
    output_name TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft','active','deprecated','rejected')),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (template_id, version)
);

CREATE TABLE IF NOT EXISTS forge_template_components (
    template_id TEXT NOT NULL,
    template_version INTEGER NOT NULL,
    position INTEGER NOT NULL CHECK (position >= 0),
    component_id TEXT NOT NULL,
    component_version INTEGER NOT NULL,
    required INTEGER NOT NULL DEFAULT 1 CHECK (required IN (0,1)),
    PRIMARY KEY (template_id, template_version, position),
    UNIQUE (template_id, template_version, component_id, component_version),
    FOREIGN KEY (template_id, template_version)
      REFERENCES forge_templates(template_id, version) ON DELETE CASCADE,
    FOREIGN KEY (component_id, component_version)
      REFERENCES forge_components(component_id, version)
);

CREATE TABLE IF NOT EXISTS forge_template_variables (
    template_id TEXT NOT NULL,
    template_version INTEGER NOT NULL,
    variable_name TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    required INTEGER NOT NULL DEFAULT 1 CHECK (required IN (0,1)),
    default_value TEXT,
    validation_pattern TEXT,
    PRIMARY KEY (template_id, template_version, variable_name),
    FOREIGN KEY (template_id, template_version)
      REFERENCES forge_templates(template_id, version) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS forge_builds (
    build_id TEXT PRIMARY KEY,
    template_id TEXT NOT NULL,
    template_version INTEGER NOT NULL,
    target_model TEXT,
    variables_json TEXT NOT NULL,
    rendered_prompt TEXT NOT NULL,
    rendered_hash TEXT NOT NULL,
    output_path TEXT,
    status TEXT NOT NULL DEFAULT 'built' CHECK (status IN ('built','tested','approved','rejected','superseded')),
    created_by TEXT NOT NULL DEFAULT 'jamesos',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (template_id, template_version)
      REFERENCES forge_templates(template_id, version)
);

CREATE TABLE IF NOT EXISTS forge_build_components (
    build_id TEXT NOT NULL,
    position INTEGER NOT NULL,
    component_id TEXT NOT NULL,
    component_version INTEGER NOT NULL,
    content_hash TEXT NOT NULL,
    PRIMARY KEY (build_id, position),
    FOREIGN KEY (build_id) REFERENCES forge_builds(build_id) ON DELETE CASCADE,
    FOREIGN KEY (component_id, component_version)
      REFERENCES forge_components(component_id, version)
);

CREATE TABLE IF NOT EXISTS forge_test_cases (
    test_case_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    template_id TEXT NOT NULL,
    template_version INTEGER NOT NULL,
    variables_json TEXT NOT NULL,
    expected_contains_json TEXT NOT NULL DEFAULT '[]',
    forbidden_contains_json TEXT NOT NULL DEFAULT '[]',
    expected_min_length INTEGER NOT NULL DEFAULT 1,
    active INTEGER NOT NULL DEFAULT 1 CHECK (active IN (0,1)),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (template_id, template_version)
      REFERENCES forge_templates(template_id, version)
);

CREATE TABLE IF NOT EXISTS forge_test_runs (
    test_run_id TEXT PRIMARY KEY,
    test_case_id TEXT NOT NULL,
    build_id TEXT,
    passed INTEGER NOT NULL CHECK (passed IN (0,1)),
    failure_details TEXT,
    run_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (test_case_id) REFERENCES forge_test_cases(test_case_id),
    FOREIGN KEY (build_id) REFERENCES forge_builds(build_id)
);

CREATE TABLE IF NOT EXISTS forge_ratings (
    rating_id TEXT PRIMARY KEY,
    build_id TEXT NOT NULL,
    model_name TEXT,
    outcome_score INTEGER CHECK (outcome_score BETWEEN 0 AND 100),
    instruction_following_score INTEGER CHECK (instruction_following_score BETWEEN 0 AND 100),
    completeness_score INTEGER CHECK (completeness_score BETWEEN 0 AND 100),
    hallucination_risk_score INTEGER CHECK (hallucination_risk_score BETWEEN 0 AND 100),
    notes TEXT,
    rated_by TEXT NOT NULL,
    rated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (build_id) REFERENCES forge_builds(build_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS forge_import_batches (
    import_batch_id TEXT PRIMARY KEY,
    source_kind TEXT NOT NULL,
    source_reference TEXT,
    imported_count INTEGER NOT NULL DEFAULT 0,
    accepted_count INTEGER NOT NULL DEFAULT 0,
    rejected_count INTEGER NOT NULL DEFAULT 0,
    duplicate_count INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL CHECK (status IN ('started','completed','failed')),
    notes TEXT,
    started_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TEXT
);

CREATE TABLE IF NOT EXISTS forge_import_items (
    import_item_id TEXT PRIMARY KEY,
    import_batch_id TEXT NOT NULL,
    external_id TEXT,
    title TEXT,
    raw_content TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    decision TEXT NOT NULL DEFAULT 'pending' CHECK (decision IN ('pending','accepted','rejected','duplicate')),
    mapped_component_id TEXT,
    mapped_component_version INTEGER,
    review_notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (import_batch_id) REFERENCES forge_import_batches(import_batch_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_forge_components_type_status
  ON forge_components(component_type, status);
CREATE INDEX IF NOT EXISTS idx_forge_components_hash
  ON forge_components(content_hash);
CREATE INDEX IF NOT EXISTS idx_forge_component_tags_tag
  ON forge_component_tags(tag);
CREATE INDEX IF NOT EXISTS idx_forge_templates_model_status
  ON forge_templates(target_model, status);
CREATE INDEX IF NOT EXISTS idx_forge_builds_template_created
  ON forge_builds(template_id, template_version, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_forge_builds_hash
  ON forge_builds(rendered_hash);
CREATE INDEX IF NOT EXISTS idx_forge_test_runs_case_time
  ON forge_test_runs(test_case_id, run_at DESC);
CREATE INDEX IF NOT EXISTS idx_forge_ratings_build
  ON forge_ratings(build_id);
CREATE INDEX IF NOT EXISTS idx_forge_import_items_hash
  ON forge_import_items(content_hash);

INSERT OR IGNORE INTO forge_schema_versions(version, description)
VALUES (1, 'Prompt Forge component, template, build, test, rating and import schema');
