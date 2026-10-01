import base64
import httpx

class VirusTotalProvider:
    def __init__(self, api_key: str | None):
        self.api_key = api_key

    async def get_url_report(self, url: str) -> tuple[dict, str]:
        if not self.api_key:
            return {"provider": "virustotal", "available": False, "reason": "not_configured"}, "not_configured"
        try:
            identifier = base64.urlsafe_b64encode(url.encode()).decode().strip("=")
            headers = {"x-apikey": self.api_key}
            async with httpx.AsyncClient(timeout=6.0) as client:
                response = await client.get(f"https://www.virustotal.com/api/v3/urls/{identifier}", headers=headers)
                if response.status_code == 404:
                    return {"provider": "virustotal", "available": True, "malicious": 0, "suspicious": 0, "undetected": 0, "harmless": 0, "timeout": 0, "not_found": True}, "ok"
                response.raise_for_status()
                stats = response.json().get("data", {}).get("attributes", {}).get("last_analysis_stats", {})
            return {"provider": "virustotal", **stats, "available": True}, "ok"
        except Exception as exc:
            return {"provider": "virustotal", "available": False, "error": type(exc).__name__}, "unavailable"

