"""
SentinelGuard Phase II demonstration script.
Initialises the SQLite schema, populates sample data for five scenarios,
and runs validation queries. Use printed outputs as evidence for Phase II testing.
"""
from pathlib import Path
import sqlite3
from textwrap import dedent

DB_PATH = Path("sentinelguard_phase2.db")
SCHEMA = Path("db/schema.sql").read_text()


def reset_database(conn: sqlite3.Connection) -> None:
    conn.executescript("DROP TABLE IF EXISTS compliance_reports;")
    conn.executescript("DROP TABLE IF EXISTS threat_intel_matches;")
    conn.executescript("DROP TABLE IF EXISTS incident_tasks;")
    conn.executescript("DROP TABLE IF EXISTS ai_assessments;")
    conn.executescript("DROP TABLE IF EXISTS security_events;")
    conn.executescript("DROP TABLE IF EXISTS assets;")
    conn.executescript("DROP TABLE IF EXISTS analysts;")
    conn.executescript(SCHEMA)


def seed_static_data(conn: sqlite3.Connection) -> None:
    conn.executemany(
        """
        INSERT INTO analysts(full_name, email, role, on_call)
        VALUES (?, ?, ?, ?)
        """,
        [
            ("Riya Patel", "riya.patel@sentinelguard.io", "Tier 2", 1),
            ("Marcus Lee", "marcus.lee@sentinelguard.io", "Tier 1", 0),
            ("Leila Ahmed", "leila.ahmed@sentinelguard.io", "Manager", 0),
        ],
    )
    conn.executemany(
        """
        INSERT INTO assets(hostname, ip_address, business_owner, criticality, last_patch_date)
        VALUES (?, ?, ?, ?, ?)
        """,
        [
            ("auth-gateway-01", "10.20.5.14", "FinOps", "Critical", "2025-10-01"),
            ("vpn-edge-02", "172.16.9.200", "Infrastructure", "High", "2025-09-20"),
            ("dev-build-agent", "192.168.88.12", "Engineering", "Moderate", "2025-09-27"),
        ],
    )


def scenario_log_intake(conn: sqlite3.Connection) -> int:
    event_cursor = conn.execute(
        """
        INSERT INTO security_events(asset_id, source, raw_log, status)
        VALUES (?, ?, ?, ?)
        """,
        (
            1,
            "CrowdStrike Falcon",
            dedent(
                """\
                {"timestamp":"2025-10-26T14:35:22Z","event":"process_spawn","user":"svc-finance",
                 "parent_process":"powershell.exe","child_process":"rundll32.exe","command_line":"rundll32.exe C:\\Temp\\stage.dll"}"""
            ),
            "New",
        ),
    )
    event_id = event_cursor.lastrowid
    conn.commit()
    return event_id


def scenario_ai_assessment(conn: sqlite3.Connection, event_id: int) -> None:
    conn.execute(
        """
        INSERT INTO ai_assessments(event_id, model_version, risk_score, severity_label, recommended_action, summary)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            event_id,
            "risk-clf-v1.0",
            0.87,
            "High",
            "Isolate auth-gateway-01 and reset svc-finance credentials.",
            "AI flagged living-off-the-land execution pattern indicative of credential theft.",
        ),
    )
    conn.commit()


def scenario_threat_intel(conn: sqlite3.Connection, event_id: int) -> None:
    conn.executemany(
        """
        INSERT INTO threat_intel_matches(event_id, indicator_type, indicator_value, threat_actor, confidence)
        VALUES (?, ?, ?, ?, ?)
        """,
        [
            (event_id, "IP", "185.199.110.153", "APT-PhantomFox", 0.92),
            (event_id, "Hash", "f2c7d9a8e4bd88f3f89d7b5b1c4fbd67", "APT-PhantomFox", 0.84),
        ],
    )
    conn.commit()


def scenario_task_orchestration(conn: sqlite3.Connection, event_id: int) -> None:
    conn.executemany(
        """
        INSERT INTO incident_tasks(event_id, assigned_to, task_description, priority, due_date, status)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        [
            (event_id, 1, "Disable svc-finance account", "Urgent", "2025-10-27", "In Progress"),
            (event_id, 2, "Collect volatile memory from auth-gateway-01", "High", "2025-10-28", "Pending"),
            (event_id, 1, "Update incident ticket with AI summary", "Medium", "2025-10-27", "Complete"),
        ],
    )
    conn.commit()


def scenario_compliance_report(conn: sqlite3.Connection, event_id: int) -> None:
    conn.execute(
        """
        INSERT INTO compliance_reports(event_id, generated_by, regulation, summary_text, export_path)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            event_id,
            3,
            "SOC2-CC8",
            "Incident contained within SLA. AI-guided triage accelerated remediation by 30%.",
            "reports/INC-2025-10-26.pdf",
        ),
    )
    conn.execute(
        "UPDATE security_events SET status = 'Resolved' WHERE event_id = ?",
        (event_id,),
    )
    conn.commit()


def run_validation_queries(conn: sqlite3.Connection) -> None:
    print("\n=== Scenario Validation Outputs ===")
    print("\n[1] Newly ingested security event:")
    for row in conn.execute(
        """
        SELECT e.event_id, a.hostname, e.source, e.status, e.ingest_time
        FROM security_events e
        JOIN assets a ON e.asset_id = a.asset_id
        """
    ):
        print(dict(row))

    print("\n[2] Latest AI assessment for event:")
    for row in conn.execute(
        """
        SELECT event_id, model_version, severity_label, risk_score, recommended_action
        FROM ai_assessments
        ORDER BY created_at DESC LIMIT 1
        """
    ):
        print(dict(row))

    print("\n[3] Threat intelligence matches:")
    for row in conn.execute(
        """
        SELECT indicator_type, indicator_value, threat_actor, confidence
        FROM threat_intel_matches
        """
    ):
        print(dict(row))

    print("\n[4] Outstanding incident tasks:")
    for row in conn.execute(
        """
        SELECT t.task_description, t.priority, t.status, an.full_name
        FROM incident_tasks t
        LEFT JOIN analysts an ON t.assigned_to = an.analyst_id
        """
    ):
        print(dict(row))

    print("\n[5] Compliance report snapshot:")
    for row in conn.execute(
        """
        SELECT event_id, regulation, summary_text, export_path
        FROM compliance_reports
        """
    ):
        print(dict(row))


def main() -> None:
    if DB_PATH.exists():
        DB_PATH.unlink()
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        reset_database(conn)
        seed_static_data(conn)
        event_id = scenario_log_intake(conn)
        scenario_ai_assessment(conn, event_id)
        scenario_threat_intel(conn, event_id)
        scenario_task_orchestration(conn, event_id)
        scenario_compliance_report(conn, event_id)
        run_validation_queries(conn)

    print(f"\nSQLite database initialised at: {DB_PATH.resolve()}")


if __name__ == "__main__":
    main()
