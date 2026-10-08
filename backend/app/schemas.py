from pydantic import BaseModel, Field


class ProjectIn(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    repo_url: str
    criticality: str = "medium"


class ProjectOut(BaseModel):
    project_id: str
    name: str
    owner_id: str
    repo_url: str
    criticality: str

    model_config = {"from_attributes": True}


class ScanIn(BaseModel):
    project_id: str
    ecosystem: str
    manifest: str


class SignIn(BaseModel):
    project_id: str
    build_id: str
    artifact_hash: str
    sbom_ref: str = ""


class VerifyIn(BaseModel):
    artifact_id: str
    signature: str
