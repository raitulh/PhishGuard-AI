import pytest
from app.engines.brand_engine import analyze_brand
from app.engines.url_engine import analyze_url, extract_urls, host_is_public
from app.engines.social_engine import analyze_social
from app.engines.risk_engine import fuse_evidence
from app.schemas.analysis import Evidence


def test_extract_and_normalize_url():
    assert extract_urls("Visit www.Example.com/login#fragment") == ["https://www.example.com/login"]
    result = analyze_url("https://xn--paypa1-9za.example/login?verify=1")
    assert result["has_punycode"] is True
    assert "verify" in result["suspicious_parameters"]

@pytest.mark.parametrize("host", ["localhost", "127.0.0.1", "10.0.0.5", "169.254.169.254"])
def test_ssrf_hosts_are_not_public(host):
    assert host_is_public(host) is False

def test_brand_mismatch_is_signal():
    result = analyze_brand("paypal-login.example", "PayPal account verification")
    assert result["impersonation"] is True

def test_social_fallback_and_deduplicated_risk():
    social = analyze_social("Urgent: your account is suspended. Verify your password now.")
    assert social["urgency"] > 0
    score, level, confidence = fuse_evidence([Evidence(source="url", signal="punycode", severity="high", weight=15, evidence="x"), Evidence(source="url", signal="punycode", severity="high", weight=15, evidence="x")], {"ollama": "unavailable", "virustotal": "not_configured", "rdap": "ok", "redirect": "not_run"})
    assert score == 15
    assert level.value == "LOW_OBSERVED_RISK"
