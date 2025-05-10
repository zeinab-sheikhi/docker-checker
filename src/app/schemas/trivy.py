from typing import Any

from pydantic import BaseModel


class CVSSModel(BaseModel):
    V2Vector: str | None = None
    V3Vector: str | None = None
    V2Score: float | None = None
    V3Score: float | None = None


class VulnerabilityModel(BaseModel):
    VulnerabilityID: str
    PkgID: str | None
    PkgName: str
    InstalledVersion: str | None
    FixedVersion: str | None
    Status: str | None
    Severity: str
    Title: str | None
    Description: str | None
    PrimaryURL: str | None
    References: list[str] | None
    CweIDs: list[str] | None
    CVSS: dict[str, CVSSModel] | None


class ResultModel(BaseModel):
    Target: str
    Class: str | None
    Type: str | None
    Vulnerabilities: list[VulnerabilityModel] | None = None


class MetadataModel(BaseModel):
    Size: int | None
    OS: dict[str, Any] | None
    ImageID: str | None
    DiffIDs: list[str] | None
    RepoTags: list[str] | None
    ImageConfig: dict[str, Any] | None
    Layers: list[dict[str, Any]] | None


class TrivyReportModel(BaseModel):
    SchemaVersion: int
    CreatedAt: str
    ArtifactName: str
    ArtifactType: str
    Metadata: MetadataModel
    Results: list[ResultModel]


class VulnerabilitySummary(BaseModel):
    package: str
    vulnerability_id: str
    severity: str
    title: str | None
    description: str | None
    fixed_version: str | None


class ScanResult(BaseModel):
    is_safe: bool
    vulnerabilities: list[VulnerabilitySummary]


def format_vulnerabilities(vulnerabilities: list) -> str:
    if not vulnerabilities:
        return "No vulnerabilities found."
    lines = []
    for vuln in vulnerabilities:
        lines.append(
            f"Package: {getattr(vuln, 'package', '')}\n"
            f"Vulnerability: {getattr(vuln, 'vulnerability_id', '')}\n"
            f"Severity: {getattr(vuln, 'severity', '')}\n"
            f"Title: {getattr(vuln, 'title', '')}\n"
            f"Description: {(getattr(vuln, 'description', '') or '')[:100]}...\n"
            f"Fixed Version: {getattr(vuln, 'fixed_version', '')}\n" + "-" * 60
        )
    return "\n".join(lines)
