from difflib import SequenceMatcher

BRAND_REGISTRY = {
    "paypal": ["paypal.com"],
    "microsoft": ["microsoft.com", "live.com"],
    "google": ["google.com"],
    "amazon": ["amazon.com"],
    "apple": ["apple.com"],
    "facebook": ["facebook.com"],
    "instagram": ["instagram.com"],
    "linkedin": ["linkedin.com"],
}


def _registered_domain(hostname: str) -> str:
    labels = hostname.lower().strip(".").split(".")
    return ".".join(labels[-2:]) if len(labels) >= 2 else hostname.lower()


def analyze_brand(hostname: str, text: str = "") -> dict:
    registered = _registered_domain(hostname)
    haystack = f"{hostname} {text}".lower()
    matches = []
    for brand, official_domains in BRAND_REGISTRY.items():
        if brand in haystack:
            official = registered in official_domains
            similarity = max(SequenceMatcher(None, registered.split(".")[0], domain.split(".")[0]).ratio() for domain in official_domains)
            matches.append({"brand": brand, "official_domain": official, "similarity": round(similarity, 3)})
    return {"registered_domain": registered, "matches": matches, "impersonation": any(not item["official_domain"] for item in matches)}
