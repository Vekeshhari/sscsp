import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


def uid():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    username: Mapped[str] = mapped_column(String, unique=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True)
    role: Mapped[str] = mapped_column(String)
    pw_hash: Mapped[str] = mapped_column(String)
    mfa: Mapped[bool] = mapped_column(Boolean, default=False)
    created: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Project(Base):
    __tablename__ = "projects"

    project_id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    name: Mapped[str] = mapped_column(String, unique=True)
    owner_id: Mapped[str] = mapped_column(ForeignKey("users.user_id"))
    repo_url: Mapped[str] = mapped_column(String)
    criticality: Mapped[str] = mapped_column(String, default="medium")
    created: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Dependency(Base):
    __tablename__ = "dependencies"

    dep_id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.project_id"))
    name: Mapped[str] = mapped_column(String)
    version: Mapped[str] = mapped_column(String)
    ecosystem: Mapped[str] = mapped_column(String)
    hash: Mapped[str] = mapped_column(String, nullable=True)
    depth: Mapped[int] = mapped_column(Integer, default=1)


class Vulnerability(Base):
    __tablename__ = "vulnerabilities"

    vuln_id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    cve: Mapped[str] = mapped_column(String, index=True)
    package: Mapped[str] = mapped_column(String)
    version: Mapped[str] = mapped_column(String)
    cvss: Mapped[float] = mapped_column(Float)
    source: Mapped[str] = mapped_column(String, default="OSV")


class Finding(Base):
    __tablename__ = "findings"

    finding_id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.project_id"))
    dep_id: Mapped[str] = mapped_column(ForeignKey("dependencies.dep_id"))
    vuln_id: Mapped[str] = mapped_column(ForeignKey("vulnerabilities.vuln_id"), nullable=True)
    severity: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String, default="OPEN")
    detected: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Artifact(Base):
    __tablename__ = "artifacts"

    artifact_id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.project_id"))
    build_id: Mapped[str] = mapped_column(String)
    hash: Mapped[str] = mapped_column(String)
    signature: Mapped[str] = mapped_column(String)
    sbom_ref: Mapped[str] = mapped_column(String)
    created: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Remediation(Base):
    __tablename__ = "remediations"

    rem_id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    finding_id: Mapped[str] = mapped_column(ForeignKey("findings.finding_id"))
    action: Mapped[str] = mapped_column(String)
    assignee: Mapped[str] = mapped_column(ForeignKey("users.user_id"))
    status: Mapped[str] = mapped_column(String, default="OPEN")
    due: Mapped[datetime] = mapped_column(DateTime, nullable=True)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    log_id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    actor_id: Mapped[str] = mapped_column(String)
    action: Mapped[str] = mapped_column(String)
    target: Mapped[str] = mapped_column(String)
    ts: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    prev_hash: Mapped[str] = mapped_column(String, nullable=True)
    curr_hash: Mapped[str] = mapped_column(String)
