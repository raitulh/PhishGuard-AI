import re

GROUPS = {
    "urgency": ["urgent", "immediately", "now", "within minutes", "expires", "act today"],
    "credential_request": ["password", "otp", "pin", "verification", "login", "code", "credentials"],
    "payment_request": ["pay", "transfer", "gift card", "crypto", "wire", "payment"],
    "fear": ["suspended", "blocked", "locked", "compromised", "legal action", "fraud"],
    "authority_impersonation": ["bank", "security team", "support", "admin", "government", "irs"],
    "secrecy_pressure": ["don't tell", "do not share", "secret", "confidential"],
}


def analyze_social(text: str) -> dict:
    lowered = (text or "").lower()
    scores = {name: round(min(1.0, sum(lowered.count(term) for term in terms) / 2), 2) for name, terms in GROUPS.items()}
    scores["overall_social_engineering"] = round(min(1.0, sum(scores.values()) / (len(scores) * 0.72)), 2)
    labels = {
        "urgency": "Urgency pressure",
        "credential_request": "Credential request",
        "payment_request": "Payment request",
        "fear": "Fear or threat language",
        "authority_impersonation": "Authority impersonation",
        "secrecy_pressure": "Secrecy pressure",
    }
    scores["red_flags"] = [labels[name] for name, score in scores.items() if name in labels and score >= 0.5][:5]
    scores["explanation"] = "Rule-based semantic analysis; local Ollama can provide richer context when configured."
    scores["provider"] = "rules"
    return scores
