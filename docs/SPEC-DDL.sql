-- AIGate — Database DDL v0.1 (data/aigate.db)

CREATE TABLE IF NOT EXISTS projects (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  intended_purpose TEXT,
  domain TEXT,
  status TEXT NOT NULL DEFAULT 'DRAFT',
  features_json TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS documents (
  id TEXT PRIMARY KEY,
  project_id TEXT REFERENCES projects(id),
  filename TEXT NOT NULL,
  mime_type TEXT,
  original_path TEXT NOT NULL,
  original_sha256 TEXT NOT NULL,
  language TEXT,
  status TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS policies (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  rules_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS document_versions (
  id TEXT PRIMARY KEY,
  document_id TEXT NOT NULL REFERENCES documents(id),
  kind TEXT NOT NULL CHECK (kind IN ('EXTRACTED','MASKED','PSEUDONYMIZED','SEMANTIC')),
  zone INTEGER NOT NULL CHECK (zone IN (0,1,2)),
  path TEXT NOT NULL,
  sha256 TEXT NOT NULL,
  policy_id TEXT REFERENCES policies(id),
  privacy_snapshot_json TEXT,
  utility_score REAL,
  privacy_score REAL,
  reid_risk REAL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS detected_entities (
  id TEXT PRIMARY KEY,
  document_version_id TEXT NOT NULL REFERENCES document_versions(id),
  entity_type TEXT NOT NULL,
  category TEXT NOT NULL,
  detector TEXT NOT NULL CHECK (detector IN ('REGEX','DICT','NER','LLM','MERGE','METADATA','OCR')),
  confidence REAL NOT NULL,
  span_start INTEGER,
  span_end INTEGER,
  value_hash TEXT NOT NULL,
  action TEXT,
  action_reason TEXT,
  reviewed_by_user INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS anonymization_events (
  id TEXT PRIMARY KEY,
  source_version_id TEXT NOT NULL REFERENCES document_versions(id),
  result_version_id TEXT NOT NULL REFERENCES document_versions(id),
  strategy TEXT NOT NULL,
  entities_processed INTEGER,
  entities_blocked INTEGER,
  diff_json TEXT,
  validator_pass INTEGER NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS llm_providers (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  endpoint TEXT NOT NULL,
  model TEXT NOT NULL,
  privacy_class TEXT NOT NULL CHECK (privacy_class IN ('LOCAL','TRUSTED','EXTERNAL','UNKNOWN','BLOCKED')),
  privacy_class_locked INTEGER NOT NULL DEFAULT 0,
  endpoint_verified_local INTEGER,
  country TEXT,
  transfer_mechanism TEXT,
  training_policy_tier TEXT,
  max_risk_allowed TEXT NOT NULL,
  params_json TEXT
);

CREATE TABLE IF NOT EXISTS llm_requests (
  id TEXT PRIMARY KEY,
  provider_id TEXT NOT NULL REFERENCES llm_providers(id),
  document_version_id TEXT REFERENCES document_versions(id),
  prompt_hash TEXT NOT NULL,
  prompt_text TEXT,
  gate_result TEXT NOT NULL CHECK (gate_result IN ('PASS','REVIEW','BLOCK')),
  gate_findings_json TEXT,
  created_at TEXT NOT NULL,
  CHECK (prompt_text IS NULL OR gate_result = 'PASS')
);

CREATE TABLE IF NOT EXISTS llm_responses (
  id TEXT PRIMARY KEY,
  request_id TEXT NOT NULL REFERENCES llm_requests(id),
  response_text TEXT,
  postflight_result TEXT NOT NULL CHECK (postflight_result IN ('CLEAN','LEAK_SUSPECT','BLOCKED')),
  postflight_findings_json TEXT,
  latency_ms INTEGER,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS knowledge_versions (
  id TEXT PRIMARY KEY,
  published_at TEXT NOT NULL,
  notes TEXT,
  approved_by_human INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS regulatory_sources (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  authority TEXT NOT NULL,
  legal_weight TEXT NOT NULL CHECK (legal_weight IN
    ('PRIMARY_LAW','OFFICIAL_GUIDANCE','SUPERVISORY_OPINION','IMPLEMENTATION_GUIDANCE','AIGATE_INTERPRETATION')),
  url TEXT,
  version_label TEXT,
  retrieved_at TEXT
);

CREATE TABLE IF NOT EXISTS regulatory_chunks (
  id TEXT PRIMARY KEY,
  source_id TEXT NOT NULL REFERENCES regulatory_sources(id),
  article TEXT,
  paragraph TEXT,
  text TEXT NOT NULL,
  language TEXT NOT NULL,
  topics_json TEXT,
  effective_from TEXT,
  effective_to TEXT,
  kb_version TEXT NOT NULL REFERENCES knowledge_versions(id),
  embedding_id INTEGER
);

CREATE TABLE IF NOT EXISTS rules (
  id TEXT PRIMARY KEY,
  framework TEXT NOT NULL,
  category TEXT NOT NULL,
  severity TEXT NOT NULL,
  title TEXT NOT NULL,
  condition_json TEXT NOT NULL,
  question_ids_json TEXT,
  controls_json TEXT,
  action TEXT NOT NULL,
  human_review INTEGER NOT NULL,
  source_refs_json TEXT NOT NULL,
  effective_from TEXT,
  effective_to TEXT,
  kb_version TEXT NOT NULL REFERENCES knowledge_versions(id)
);

CREATE TABLE IF NOT EXISTS questions (
  id TEXT PRIMARY KEY,
  text TEXT NOT NULL,
  answer_type TEXT NOT NULL,
  options_json TEXT,
  triggers_json TEXT
);

CREATE TABLE IF NOT EXISTS evidence (
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL REFERENCES projects(id),
  claim TEXT NOT NULL,
  evidence_text TEXT,
  evidence_doc_id TEXT REFERENCES documents(id),
  provided_by TEXT,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS assessments (
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL REFERENCES projects(id),
  kb_version TEXT NOT NULL REFERENCES knowledge_versions(id),
  gdpr_status TEXT NOT NULL,
  aiact_class TEXT NOT NULL,
  summary_json TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS assessment_findings (
  id TEXT PRIMARY KEY,
  assessment_id TEXT NOT NULL REFERENCES assessments(id),
  rule_id TEXT NOT NULL REFERENCES rules(id),
  status TEXT NOT NULL CHECK (status IN ('MET','NOT_MET','UNKNOWN','REVIEW')),
  confidence REAL,
  evidence_ids_json TEXT,
  missing_info_json TEXT,
  explanation TEXT
);

CREATE TABLE IF NOT EXISTS audit_events (
  seq INTEGER PRIMARY KEY AUTOINCREMENT,
  ts TEXT NOT NULL,
  component TEXT NOT NULL,
  action TEXT NOT NULL,
  object_type TEXT,
  object_id TEXT,
  input_hash TEXT,
  output_hash TEXT,
  rule_id TEXT,
  risk TEXT,
  detail_json TEXT,
  prev_hash TEXT NOT NULL,
  event_hash TEXT NOT NULL
);
