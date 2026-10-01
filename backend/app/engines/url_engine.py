import ipaddress
import re
from urllib.parse import urlsplit, urlunsplit

URL_PATTERN = re.compile(r"(?i)(?:https?://|www\.)[^\s<>\"']+")
SUSPICIOUS_PARAMS = {"redirect", "return", "next", "continue", "url", "token", "session", "verify"}
KEYWORDS = {"login", "verify", "account", "secure", "password", "update", "confirm", "billing"}


def extract_urls(text: str) -> list[str]:
    return [normalize_url(match.rstrip(".,);]")) for match in URL_PATTERN.findall(text or "")]


def normalize_url(value: str) -> str:
    raw = value.strip()
    if raw.lower().startswith("www."):
        raw = "https://" + raw
    parts = urlsplit(raw)
    if parts.scheme.lower() not in {"http", "https"} or not parts.hostname:
        raise ValueError("Only valid HTTP(S) URLs are supported")
    hostname = parts.hostname.lower().rstrip(".")
    port = parts.port
    netloc = hostname
    if port and not ((parts.scheme.lower() == "http" and port == 80) or (parts.scheme.lower() == "https" and port == 443)):
        netloc = f"{hostname}:{port}"
    path = parts.path or "/"
    return urlunsplit((parts.scheme.lower(), netloc, path, parts.query, ""))


def host_is_public(hostname: str) -> bool:
    if hostname.lower() in {"localhost", "ip6-localhost"} or ".local" in hostname.lower():
        return False
    try:
        address = ipaddress.ip_address(hostname)
        return not (address.is_private or address.is_loopback or address.is_link_local or address.is_reserved or address.is_unspecified)
    except ValueError:
        return True


def analyze_url(url: str) -> dict:
    normalized = normalize_url(url)
    parts = urlsplit(normalized)
    hostname = parts.hostname or ""
    labels = hostname.split(".") if hostname else []
    query_keys = [item.split("=", 1)[0].lower() for item in parts.query.split("&") if item]
    lowered = normalized.lower()
    return {
        "normalized_url": normalized,
        "hostname": hostname,
        "url_length": len(normalized),
        "hostname_length": len(hostname),
        "path_length": len(parts.path),
        "query_length": len(parts.query),
        "subdomain_count": max(0, len(labels) - 2),
        "digit_count": sum(char.isdigit() for char in hostname),
        "hyphen_count": hostname.count("-"),
        "special_character_count": sum(char in "@%_" for char in normalized),
        "has_at_symbol": "@" in parts.netloc,
        "is_ip_host": not any(char.isalpha() for char in hostname),
        "has_punycode": any(label.startswith("xn--") for label in labels),
        "has_encoded_characters": "%" in normalized,
        "query_parameter_count": len(query_keys),
        "suspicious_parameters": sorted(set(query_keys) & SUSPICIOUS_PARAMS),
        "keyword_hits": sorted(keyword for keyword in KEYWORDS if keyword in lowered),
        "is_public_host": host_is_public(hostname),
    }
