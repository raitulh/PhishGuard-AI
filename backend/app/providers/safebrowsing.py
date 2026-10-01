import httpx

class SafeBrowsingProvider:
    def __init__(self, api_key: str | None):
        self.api_key = api_key

    async def check_url(self, url: str) -> tuple[dict, str]:
        if not self.api_key:
            return {"provider": "safebrowsing", "available": False, "reason": "not_configured"}, "not_configured"
        try:
            endpoint = f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={self.api_key}"
            payload = {
                "client": {"clientId": "phishguard", "clientVersion": "1.0.0"},
                "threatInfo": {
                    "threatTypes": [
                        "MALWARE",
                        "SOCIAL_ENGINEERING",
                        "UNWANTED_SOFTWARE",
                        "POTENTIALLY_HARMFUL_APPLICATION"
                    ],
                    "platformTypes": ["ANY_PLATFORM"],
                    "threatEntryTypes": ["URL"],
                    "threatEntries": [{"url": url}]
                }
            }
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(endpoint, json=payload)
                response.raise_for_status()
                data = response.json()

            matches = data.get("matches", [])
            threat_types = list(dict.fromkeys([m.get("threatType") for m in matches if m.get("threatType")]))
            is_threat = len(matches) > 0

            return {
                "provider": "safebrowsing",
                "is_threat": is_threat,
                "matches": matches,
                "threat_types": threat_types,
                "available": True
            }, "ok"
        except Exception as exc:
            return {"provider": "safebrowsing", "available": False, "error": type(exc).__name__}, "unavailable"
