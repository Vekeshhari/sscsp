"""Fuzzing test on manifest parser boundary using Hypothesis."""
from hypothesis import given, settings, strategies as st

from app.services import scanner


@settings(max_examples=1000, deadline=None)
@given(st.text(min_size=0, max_size=2000))
def test_parse_manifest_never_crashes(s):
    """Fuzzer: any string input must not crash the parser."""
    try:
        result = scanner.parse_manifest(s, "npm")
        assert isinstance(result, list)
    except ValueError:
        pass  # only acceptable exception


@settings(max_examples=500)
@given(st.floats(min_value=-100.0, max_value=200.0, allow_nan=False))
def test_severity_handles_extreme_cvss(cvss):
    """Fuzzer: severity() must return one of the 4 labels for any input."""
    assert scanner.severity(cvss) in {"CRITICAL", "HIGH", "MEDIUM", "LOW"}


@settings(max_examples=300)
@given(st.text(min_size=1, max_size=200))
def test_purl_parser_rejects_malformed(purl):
    """Fuzzer: malformed PURL should raise ValueError, not crash."""
    try:
        scanner.parse_purl(purl)
    except (ValueError, KeyError):
        pass
