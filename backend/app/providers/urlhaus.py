import httpx

class URLhausProvider:
    def __init__(self, api_key: str | None, enabled: bool = True):
        self.api_key = api_key
        self.enabled = enabled

    async def check_url(self, url: str) -> tuple[dict, str]:
        if not self.enabled or not self.api_key:
            return {"provider": "urlhaus", "available": False, "reason": "not_configured"}, "not_configured"
        try:
            headers = {"Auth-Key": self.api_key}
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post("https://urlhaus-api.abuse.ch/v1/url/", data={"url": url}, headers=headers)
                response.raise_for_status()
                data = response.json()

            query_status = data.get("query_status", "unknown")
            if query_status == "ok":
                return {
                    "provider": "urlhaus",
                    "is_threat": True,
                    "threat": data.get("threat"),
                    "url_status": data.get("url_status"),
                    "tags": data.get("tags", []),
                    "available": True
                }, "ok"
            elif query_status in ("no_results", "invalid_url"):
                return {
                    "provider": "urlhaus",
                    "is_threat": False,
                    "available": True
                }, "ok"
            else:
                return {
                    "provider": "urlhaus",
                    "available": False,
                    "reason": query_status
                }, "unavailable"
        except Exception as exc:
            return {"provider": "urlhaus", "available": False, "error": type(exc).__name__}, "unavailable"
