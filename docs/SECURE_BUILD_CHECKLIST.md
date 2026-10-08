# SSCSP Secure Build Checklist

| # | Control | Status | Evidence |
|---|---------|--------|----------|
| 1 | Least privilege (GitHub teams + scoped tokens) | ✅ | Team permissions screenshot |
| 2 | Secret management (Vault / GitHub Secrets, no hard-coded) | ✅ | `.env.example`, Gitleaks pass |
| 3 | Dependency control (Dependabot + `pip-audit` in CI) | ✅ | CI logs |
| 4 | Code review (2 reviewers, CODEOWNERS) | ✅ | PR screenshot |
| 5 | Protected branches (`main`, `develop`) | ✅ | Branch protection screenshot |
| 6 | Reproducible builds (locked requirements, pinned Docker digest) | ✅ | `requirements.txt` + Dockerfile |
| 7 | Artifact integrity (cosign signature) | ✅ | `cosign verify` output |
| 8 | Pre-commit hooks (Gitleaks, Bandit) | ✅ | `.pre-commit-config.yaml` |
| 9 | SAST in CI (Bandit + Semgrep) | ✅ | CI artifacts |
| 10 | SBOM generated per build | ✅ | CycloneDX file |
