"""Unit tests for the scanner service (Phase 14 deliverable)."""
import pytest

from app.services import scanner


# ─── Unit test 1: severity() classification ─────────────────
@pytest.mark.parametrize(
    "cvss,expected",
    [
        (9.8, "CRITICAL"),
        (10.0, "CRITICAL"),
        (7.5, "HIGH"),
        (7.0, "HIGH"),
        (5.5, "MEDIUM"),
        (3.9, "LOW"),
        (0.0, "LOW"),
    ],
)
def test_severity_classification(cvss, expected):
    assert scanner.severity(cvss) == expected


# ─── Unit test 2: parse_manifest() ──────────────────────────
def test_parse_manifest_typical():
    manifest = """
    # comment line
    log4j-core==2.14.1
    lodash==4.17.20
    """
    deps = scanner.parse_manifest(manifest, "npm")
    assert len(deps) == 2
    assert deps[0]["name"] == "log4j-core"
    assert deps[0]["version"] == "2.14.1"


def test_parse_manifest_empty():
    assert scanner.parse_manifest("", "npm") == []


def test_parse_manifest_ignores_comments():
    deps = scanner.parse_manifest("# just a comment\n", "npm")
    assert deps == []


# ─── Unit test 3: CVE matching logic ────────────────────────
def test_known_cve_match():
    adv = [a for a in scanner.SAMPLE_ADVISORIES if a["package"] == "log4j-core" and a["version"] == "2.14.1"]
    assert len(adv) == 1
    assert adv[0]["cvss"] == 10.0
    assert adv[0]["cve"] == "CVE-2021-44228"


def test_no_match_for_safe_version():
    adv = [a for a in scanner.SAMPLE_ADVISORIES if a["package"] == "lodash" and a["version"] == "4.17.21"]
    assert adv == []
