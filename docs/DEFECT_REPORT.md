# Defect Report — SSCSP Sprint 2

| Field | Value |
|---|---|
| Defect ID | **D-101** |
| Title | SQL Injection in login endpoint |
| Reporter | Dev A |
| Date Reported | 2026-01-08 |
| Sprint | Sprint 1 |
| Severity | **Critical** (CVSS 9.1) |
| Priority | P0 |
| Component | `backend/app/auth_v1_vulnerable.py` |
| Steps to Reproduce | 1. POST `/api/v1/auth/login` with `username="' OR '1'='1", password="x"`. 2. Observe 200 OK with user data. |
| Expected | 401 Unauthorized |
| Actual | 200 OK — login bypass |
| Root Cause | f-string used to build SQL query (W1 in Phase 12) |
| Fix | Replace with SQLAlchemy `select(User).where(User.username == username)` |
| Fix Commit | `fix(US-12): refactor auth module` |
| Retest | `test_sql_injection_payload_does_not_bypass` → **PASS** |
| Status | **Closed** |
