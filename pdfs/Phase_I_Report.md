# SentinelGuard: AI-Driven Incident Response Console

**Course:** CCGC 5003 Application Programming  
**Phase:** I – Project Inception  
**Submission Date:** October 27, 2025  

### Group Details
- **Group Name:** CyberSentinel Labs  
- **Group Members:** Gurmatsingh Sour (solo project team)  

---

## 1. Project Overview
SentinelGuard is a Python-based cybersecurity operations console that helps security analysts triage, investigate, and remediate security events. The application couples a traditional incident-response workflow with an embedded AI assistant that classifies alerts, summarizes log evidence, and recommends next actions. A desktop UI (Tkinter) will orchestrate five integrated use cases that read from and write to an SQLite database via SQLAlchemy. A lightweight scikit-learn model (trained on labeled security events) will power the AI risk scoring and recommendation engine. Future phases will extend these foundations into fully functional model, view, and controller layers.

## 2. Core Use Case Scenarios
1. **Log Intake & Asset Linking:** Analysts register new security events by selecting the affected asset, attaching raw log evidence, and tagging the event source. The workflow stores the event and ties it to the appropriate asset and owning analyst.  
2. **AI Risk Assessment:** On demand, the AI module evaluates the ingested event, assigns a severity score, and generates a natural-language summary plus recommended remediation tasks. Assessments are written back to the database with model lineage for audit trail.  
3. **Threat Intelligence Enrichment:** Analysts trigger enrichment to compare the event indicators (IP, hash, domain) with prior incidents and known threat intelligence. The system surfaces correlations, populates related threat records, and suggests playbooks to follow.  
4. **Incident Task Orchestration:** Analysts create and track remediation tasks (containment, eradication, recovery) from the same UI. Tasks can be assigned to team members, prioritized, and monitored until closure.  
5. **Compliance & Reporting:** When incidents close, the system compiles AI summaries, analyst actions, and timelines into a compliance-ready report. Reports can be exported for auditors and mapped to regulatory controls for future reference.  

Each scenario launches from the shared dashboard, and the state captured in one flow (e.g., AI severity score) is consumed by the others (e.g., determining task priority or report sections).

## 3. Database Tables (Model Layer Candidates)
- `analysts` – registered security team members managing incidents and tasks.  
- `assets` – catalog of protected systems and their business owners.  
- `security_events` – normalized representation of incoming alerts/logs.  
- `ai_assessments` – AI-generated severity scores, summaries, and recommended actions for each event.  
- `incident_tasks` – remediation activities tied to specific security events.  
- `threat_intel_matches` – cross-reference table tracking enrichment hits against known campaigns.  
- `compliance_reports` – finalized incident summaries for governance and audit requirements.  

(At least one table supports every scenario above; some scenarios share tables to maintain referential integrity.)

## 4. Key Fields and Data Types
**analysts**  
- `analyst_id` INTEGER PRIMARY KEY  
- `full_name` TEXT NOT NULL  
- `email` TEXT UNIQUE NOT NULL  
- `role` TEXT CHECK(role IN ('Tier 1','Tier 2','Tier 3','Manager'))  
- `on_call` BOOLEAN DEFAULT 0  
- `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP  

**assets**  
- `asset_id` INTEGER PRIMARY KEY  
- `hostname` TEXT NOT NULL  
- `ip_address` TEXT NOT NULL  
- `business_owner` TEXT NOT NULL  
- `criticality` TEXT CHECK(criticality IN ('Low','Moderate','High','Critical'))  
- `last_patch_date` DATE  

**security_events**  
- `event_id` INTEGER PRIMARY KEY  
- `asset_id` INTEGER REFERENCES assets(asset_id)  
- `ingest_time` DATETIME DEFAULT CURRENT_TIMESTAMP  
- `source` TEXT NOT NULL  
- `raw_log` TEXT NOT NULL  
- `status` TEXT CHECK(status IN ('New','Triaged','In Progress','Resolved'))  

**ai_assessments**  
- `assessment_id` INTEGER PRIMARY KEY  
- `event_id` INTEGER REFERENCES security_events(event_id) ON DELETE CASCADE  
- `model_version` TEXT NOT NULL  
- `risk_score` REAL CHECK(risk_score BETWEEN 0 AND 1)  
- `severity_label` TEXT CHECK(severity_label IN ('Low','Medium','High','Critical'))  
- `recommended_action` TEXT  
- `summary` TEXT  

**incident_tasks**  
- `task_id` INTEGER PRIMARY KEY  
- `event_id` INTEGER REFERENCES security_events(event_id) ON DELETE CASCADE  
- `assigned_to` INTEGER REFERENCES analysts(analyst_id)  
- `task_description` TEXT NOT NULL  
- `priority` TEXT CHECK(priority IN ('Low','Medium','High','Urgent'))  
- `due_date` DATE  
- `status` TEXT CHECK(status IN ('Pending','In Progress','Blocked','Complete'))  

**threat_intel_matches**  
- `match_id` INTEGER PRIMARY KEY  
- `event_id` INTEGER REFERENCES security_events(event_id)  
- `indicator_type` TEXT CHECK(indicator_type IN ('IP','Domain','Hash','URL'))  
- `indicator_value` TEXT NOT NULL  
- `threat_actor` TEXT  
- `confidence` REAL CHECK(confidence BETWEEN 0 AND 1)  

**compliance_reports**  
- `report_id` INTEGER PRIMARY KEY  
- `event_id` INTEGER REFERENCES security_events(event_id)  
- `generated_by` INTEGER REFERENCES analysts(analyst_id)  
- `generated_at` DATETIME DEFAULT CURRENT_TIMESTAMP  
- `regulation` TEXT NOT NULL  
- `summary_text` TEXT NOT NULL  
- `export_path` TEXT  

## 5. Team Roles & Responsibilities
- **Gurmatsingh Sour:** Acts as project lead, full-stack developer, and AI engineer. Responsibilities include gathering sample alert data, designing the SQLite schema, building the Tkinter interface, training the scikit-learn risk classifier, integrating all flows via controller logic, and managing testing/documentation for subsequent phases.


