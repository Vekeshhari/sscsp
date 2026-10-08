"""
Phase 9 & 10 — Automated Jira Scrum project setup for SSCSP.

Before running:
  1. Create a Jira Cloud project with key 'SSCSP' (Scrum template).
  2. Create an API token at https://id.atlassian.com/manage-profile/security/api-tokens
  3. Set the environment variables below (or edit the CONFIG block).
  4. Find your board ID and sprint field ID by running the discovery helper at bottom.

Run:
  python jira_setup_sscsp.py
"""

import os
import base64
import requests
import json
import sys
import time

# ─────────────────────────────────────────────────────────────
# CONFIG — edit these
# ─────────────────────────────────────────────────────────────
JIRA_BASE   = os.getenv("JIRA_BASE",   "https://vekeshhari.atlassian.net")
JIRA_EMAIL  = os.getenv("JIRA_EMAIL",  "rajasekarsenthilkumari@gmail.com")
JIRA_TOKEN  = os.getenv("JIRA_TOKEN",  "ATATT3xFfGF0qTeHJGItzx0V6Wker-CTIKV_IhPJMIAj5mOV4HuHWM4wurTv3rNwLoGHie7sT1Xsp6yZLbl-bG04kArsIAxSOMRI6GC6Z-N69kcIAXAYPUd5x1lfmpjkifz9fX_YrwlAr66PeY0uAZV5XHqg3-42F34WUbm1OthDcA9O1Edo9dU=181AA617")
PROJECT_KEY = os.getenv("JIRA_PROJECT", "SSCSP")
BOARD_ID    = int(os.getenv("JIRA_BOARD_ID", "101"))       # find via discovery helper
SPRINT_FIELD = os.getenv("JIRA_SPRINT_FIELD", "customfield_10020")  # find via discovery helper

# ─────────────────────────────────────────────────────────────
# HTTP helper
# ─────────────────────────────────────────────────────────────
AUTH = base64.b64encode(f"{JIRA_EMAIL}:{JIRA_TOKEN}".encode()).decode()
HEADERS = {
    "Authorization": f"Basic {AUTH}",
    "Content-Type": "application/json",
    "Accept": "application/json",
}

def api(method, path, **kwargs):
    url = f"{JIRA_BASE}/rest/api/3{path}"
    r = requests.request(method, url, headers=HEADERS, **kwargs)
    if r.status_code >= 400:
        print(f"[ERROR {r.status_code}] {method} {path}")
        print(r.text[:500])
        return None
    if r.text:
        try:
            return r.json()
        except Exception:
            return r.text
    return {}

# ─────────────────────────────────────────────────────────────
# EPICS (from Phase 2 / Phase 9)
# ─────────────────────────────────────────────────────────────
EPICS = [
    ("E1", "Project Management",   "Register and manage software projects"),
    ("E2", "Dependency Tracking",  "Record direct and transitive dependencies"),
    ("E3", "Scanning & Detection", "Detect CVEs, malicious packages, secrets"),
    ("E4", "Reporting & SBOM",     "Generate risk reports and SBOM exports"),
    ("E5", "Remediation",          "Track and verify vulnerability fixes"),
    ("E6", "Artifact Security",    "Sign, store and verify build artifacts"),
    ("E7", "Admin & Access",       "Manage users, roles, policies, audit"),
]

# ─────────────────────────────────────────────────────────────
# USER STORIES (Phase 9 requirement: ≥10)
# ─────────────────────────────────────────────────────────────
STORIES = [
    # (story_id, epic_key, priority, summary, description, acceptance, sprint)
    ("US-01", "E1", "High",
     "Register a new project",
     "As a Developer, I want to register a project so that I can track its dependencies.",
     "Project created with ID; owner set; audited; visible only to owner.",
     1),
    ("US-02", "E1", "Medium",
     "Edit project metadata",
     "As a Developer, I want to edit project metadata so that records stay accurate.",
     "Update persists; change is audit-logged; RBAC enforced.",
     1),
    ("US-03", "E2", "High",
     "Upload and parse manifest",
     "As a Developer, I want to upload a manifest so that dependencies are recorded.",
     "Supported formats: npm, PyPI, Maven, Go, Cargo. Graph stored.",
     1),
    ("US-04", "E2", "High",
     "Resolve transitive dependencies",
     "As a Developer, I want transitive dependencies resolved so that hidden risks surface.",
     "Depth ≥2 recorded; parent-child links stored.",
     1),
    ("US-05", "E3", "Critical",
     "Match dependency versions against CVEs",
     "As a Security Analyst, I want CVE matching so that I know which dependencies are vulnerable.",
     "OSV/NVD query returns matches in <30s for 1000 deps.",
     1),
    ("US-06", "E3", "Critical",
     "Detect malicious packages",
     "As a Security Analyst, I want malicious-package detection so that backdoors are caught.",
     "Typosquat + dependency-confusion detected; flagged in findings.",
     1),
    ("US-07", "E4", "High",
     "Export SBOM",
     "As an Auditor, I want SBOM export so that I can verify composition.",
     "CycloneDX and SPDX formats; signed; downloadable.",
     2),
    ("US-08", "E4", "High",
     "Compute risk score per project",
     "As a Security Analyst, I want risk scores so that I can prioritize.",
     "Score 0–100; CVSS + EPSS weighted; updates after each scan.",
     2),
    ("US-09", "E5", "High",
     "Suggest fix for a finding",
     "As a Developer, I want fix suggestions so that I can patch fast.",
     "Upgrade path or removal suggested per finding.",
     2),
    ("US-10", "E5", "High",
     "Track remediation ticket lifecycle",
     "As a Security Analyst, I want ticket tracking so that fixes are verified.",
     "Lifecycle: OPEN → IN PROGRESS → FIXED → VERIFIED → CLOSED.",
     2),
    ("US-11", "E6", "Critical",
     "Sign build artifacts",
     "As a CI/CD System, I want artifact signing so that tampering is detected.",
     "Signature produced via HSM/KMS; stored with artifact; verifiable.",
     2),
    ("US-12", "E7", "Critical",
     "Enforce RBAC on all endpoints",
     "As an Admin, I want RBAC so that least privilege applies.",
     "Role matrix enforced; negative tests pass; audit every authZ failure.",
     2),
    ("US-13", "E7", "High",
     "View immutable audit log",
     "As an Auditor, I want to view the audit log so that I can verify history.",
     "Hash chain visible; read-only for auditor role.",
     2),
    ("US-14", "E6", "Critical",
     "Verify artifact signature before deploy",
     "As a CI/CD System, I want signature verification so that only trusted artifacts deploy.",
     "Deploy blocked if signature invalid or missing.",
     2),
]

# ─────────────────────────────────────────────────────────────
# SPRINTS (Phase 9 requirement: two sprints)
# ─────────────────────────────────────────────────────────────
SPRINTS = [
    {
        "name": "SSCSP Sprint 1",
        "goal": "Enable project registration, dependency recording, and CVE scanning.",
        "start": "2026-01-06T09:00:00.000+05:30",
        "end":   "2026-01-17T17:00:00.000+05:30",
    },
    {
        "name": "SSCSP Sprint 2",
        "goal": "Deliver reporting, remediation, artifact signing and RBAC.",
        "start": "2026-01-20T09:00:00.000+05:30",
        "end":   "2026-01-31T17:00:00.000+05:30",
    },
]

# ─────────────────────────────────────────────────────────────
# STEP 1 — Create Epics
# ─────────────────────────────────────────────────────────────
def create_epics():
    print("\n[1/4] Creating Epics...")
    epic_keys = {}
    for local_id, name, desc in EPICS:
        payload = {
            "fields": {
                "project":     {"key": PROJECT_KEY},
                "summary":     f"[{local_id}] {name}",
                "description": {
                    "type": "doc", "version": 1,
                    "content": [{"type": "paragraph",
                                 "content": [{"type": "text", "text": desc}]}]
                },
                "issuetype":   {"name": "Epic"},
            }
        }
        resp = api("POST", "/issue", data=json.dumps(payload))
        if resp:
            key = resp.get("key")
            epic_keys[local_id] = key
            print(f"   ✔ {local_id} → {key}  {name}")
        else:
            print(f"   ✘ Failed to create epic {local_id}")
    return epic_keys

# ─────────────────────────────────────────────────────────────
# STEP 2 — Create User Stories + Subtasks
# ─────────────────────────────────────────────────────────────
def create_stories(epic_keys):
    print("\n[2/4] Creating User Stories and Subtasks...")
    story_keys = {}
    for sid, epic_local, prio, summary, desc, accept, sprint_no in STORIES:
        payload = {
            "fields": {
                "project":   {"key": PROJECT_KEY},
                "summary":   f"[{sid}] {summary}",
                "description": {
                    "type": "doc", "version": 1,
                    "content": [
                        {"type": "paragraph",
                         "content": [{"type": "text", "text": desc}]},
                        {"type": "paragraph",
                         "content": [{"type": "text", "text": "Acceptance Criteria: " + accept,
                                      "marks": [{"type": "strong"}]}]},
                    ]
                },
                "issuetype": {"name": "Story"},
                "priority":  {"name": prio},
                "parent":    {"key": epic_keys.get(epic_local)},
            }
        }
        resp = api("POST", "/issue", data=json.dumps(payload))
        if resp:
            key = resp.get("key")
            story_keys[sid] = key
            print(f"   ✔ {sid} → {key}  {summary}")
        else:
            print(f"   ✘ Failed: {sid}")

        # add 3 subtasks per story (dev / test / docs)
        if resp:
            for suffix, task_desc in [
                ("dev",   "Implement functionality"),
                ("test",  "Write unit + integration tests"),
                ("docs",  "Update documentation & SBOM notes"),
            ]:
                st_payload = {
                    "fields": {
                        "project":   {"key": PROJECT_KEY},
                        "parent":    {"key": key},
                        "summary":   f"{sid} {suffix}: {task_desc}",
                        "issuetype": {"name": "Subtask"},
                    }
                }
                api("POST", "/issue", data=json.dumps(st_payload))
    return story_keys

# ─────────────────────────────────────────────────────────────
# STEP 3 — Create Sprints + attach stories
# ─────────────────────────────────────────────────────────────
def create_sprints():
    print("\n[3/4] Creating Sprints...")
    url = f"{JIRA_BASE}/rest/agile/1.0/sprint"
    sprint_ids = []
    for s in SPRINTS:
        payload = {
            "name":          s["name"],
            "goal":          s["goal"],
            "startDate":     s["start"],
            "endDate":       s["end"],
            "originBoardId": BOARD_ID,
        }
        r = requests.post(url, headers=HEADERS, data=json.dumps(payload))
        if r.status_code < 400:
            sid = r.json()["id"]
            sprint_ids.append(sid)
            print(f"   ✔ {s['name']}  (id={sid})  goal: {s['goal']}")
        else:
            print(f"   ✘ Failed: {s['name']} — {r.text[:200]}")
    return sprint_ids

def attach_stories_to_sprints(story_keys, sprint_ids):
    print("\n   Attaching stories to sprints...")
    url = f"{JIRA_BASE}/rest/agile/1.0/sprint/{{sid}}/issue"
    for sid, epic_local, prio, summary, desc, accept, sprint_no in STORIES:
        key = story_keys.get(sid)
        if not key:
            continue
        sprint_id = sprint_ids[sprint_no - 1]
        r = requests.post(
            url.format(sid=sprint_id),
            headers=HEADERS,
            data=json.dumps({"issues": [key]}),
        )
        if r.status_code < 400:
            print(f"   ✔ {sid} → Sprint {sprint_no}")
        else:
            print(f"   ✘ {sid}: {r.text[:200]}")

# ─────────────────────────────────────────────────────────────
# STEP 4 — Move some tasks through the workflow (Phase 10 evidence)
# ─────────────────────────────────────────────────────────────
def transition_issue(issue_key, target_status):
    """Move an issue to a target status via the transitions API."""
    url = f"{JIRA_BASE}/rest/api/3/issue/{issue_key}/transitions"
    r = requests.get(url, headers=HEADERS)
    if r.status_code >= 400:
        return False
    for t in r.json().get("transitions", []):
        if t["to"]["name"].lower() == target_status.lower():
            requests.post(url, headers=HEADERS,
                          data=json.dumps({"transition": {"id": t["id"]}}))
            return True
    return False

def simulate_sprint_progress(story_keys):
    print("\n[4/4] Simulating Sprint 1 progress (for Phase 10 evidence)...")
    moves = [
        ("US-01", "In Progress"),
        ("US-01", "Done"),
        ("US-03", "In Progress"),
        ("US-03", "Done"),
        ("US-04", "In Progress"),
        ("US-05", "In Progress"),
        ("US-05", "Done"),
        ("US-06", "In Progress"),
    ]
    for sid, status in moves:
        key = story_keys.get(sid)
        if key and transition_issue(key, status):
            print(f"   ✔ {sid} → {status}")

# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────
def main():
    if "your-domain" in JIRA_BASE or JIRA_TOKEN == "your_api_token_here":
        print("❌  Edit the CONFIG block first (JIRA_BASE, JIRA_EMAIL, JIRA_TOKEN).")
        sys.exit(1)

    if BOARD_ID == 0:
        print("❌  Set BOARD_ID (run discovery helper below).")
        sys.exit(1)

    print(f"Connecting to {JIRA_BASE} as {JIRA_EMAIL}...")
    me = api("GET", "/myself")
    if not me:
        sys.exit(1)
    print(f"   ✔ Authenticated as {me.get('displayName')}")

    epic_keys   = create_epics()
    story_keys  = create_stories(epic_keys)
    sprint_ids  = create_sprints()
    attach_stories_to_sprints(story_keys, sprint_ids)
    simulate_sprint_progress(story_keys)

    print("\n✅ Setup complete. Open Jira → Project SSCSP → Board / Backlog.")


# ─────────────────────────────────────────────────────────────
# Discovery helpers (run these first to fill BOARD_ID and SPRINT_FIELD)
# ─────────────────────────────────────────────────────────────
def discover_board_id():
    """Run once: python -c 'from jira_setup_sscsp import discover_board_id; discover_board_id()'"""
    r = requests.get(f"{JIRA_BASE}/rest/agile/1.0/board",
                     headers=HEADERS, params={"projectKeyOrId": PROJECT_KEY})
    print(json.dumps(r.json(), indent=2))

def discover_sprint_field():
    r = requests.get(f"{JIRA_BASE}/rest/api/3/field", headers=HEADERS)
    for f in r.json():
        if "sprint" in f["name"].lower():
            print(f["id"], "→", f["name"])


if __name__ == "__main__":
    main()