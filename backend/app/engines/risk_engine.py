from collections.abc import Iterable
from app.schemas.analysis import Confidence, Evidence, RiskLevel


def risk_level(score: int) -> RiskLevel:
    if score >= 75:
        return RiskLevel.HIGH_RISK
    if score >= 50:
        return RiskLevel.SUSPICIOUS
    if score >= 25:
        return RiskLevel.CAUTION
    return RiskLevel.LOW_OBSERVED_RISK


def confidence_for(provider_status: dict[str, str], evidence: Iterable[Evidence]) -> Confidence:
    available = sum(status == "ok" for status in provider_status.values())
    strength = sum(item.weight for item in evidence)
    if available >= 3 and strength >= 45:
        return Confidence.HIGH
    if available >= 2 or strength >= 25:
        return Confidence.MEDIUM
    return Confidence.LOW


def fuse_evidence(evidence: list[Evidence], provider_status: dict[str, str]) -> tuple[int, RiskLevel, Confidence]:
    strongest_by_signal: dict[str, Evidence] = {}
    for item in evidence:
        if item.signal not in strongest_by_signal or item.weight > strongest_by_signal[item.signal].weight:
            strongest_by_signal[item.signal] = item
    score = min(100, sum(item.weight for item in strongest_by_signal.values()))
    return score, risk_level(score), confidence_for(provider_status, strongest_by_signal.values())
