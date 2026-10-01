from enum import Enum
from typing import Any
from pydantic import BaseModel, Field, model_validator

class RiskLevel(str, Enum):
    LOW_OBSERVED_RISK = "LOW_OBSERVED_RISK"
    CAUTION = "CAUTION"
    SUSPICIOUS = "SUSPICIOUS"
    HIGH_RISK = "HIGH_RISK"

class Confidence(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class AnalyzeRequest(BaseModel):
    text: str | None = Field(default=None, max_length=10000)
    url: str | None = Field(default=None, max_length=4096)

    @model_validator(mode="after")
    def requires_input(self):
        if not (self.text and self.text.strip()) and not (self.url and self.url.strip()):
            raise ValueError("text or url is required")
        return self

class Evidence(BaseModel):
    source: str
    signal: str
    severity: str
    weight: int = Field(ge=0, le=100)
    evidence: str
    metadata: dict[str, Any] = Field(default_factory=dict)

class RedFlag(BaseModel):
    title: str
    severity: str
    evidence: str

class ProviderStatus(BaseModel):
    ollama: str
    virustotal: str
    safebrowsing: str = "not_run"
    urlhaus: str = "not_run"
    rdap: str
    redirect: str

class AnalyzeResponse(BaseModel):
    scan_id: str
    risk_score: int = Field(ge=0, le=100)
    risk_level: RiskLevel
    confidence: Confidence
    summary: str
    red_flags: list[RedFlag]
    url_analysis: dict[str, Any]
    domain_analysis: dict[str, Any]
    reputation: dict[str, Any]
    safebrowsing: dict[str, Any] = Field(default_factory=dict)
    urlhaus: dict[str, Any] = Field(default_factory=dict)
    social_engineering: dict[str, Any]
    redirect_analysis: dict[str, Any]
    evidence: list[Evidence]
    recommendation: list[str]
    provider_status: ProviderStatus
