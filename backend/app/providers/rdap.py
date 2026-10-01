import httpx

async def lookup_domain(domain: str) -> tuple[dict, str]:
    try:
        async with httpx.AsyncClient(timeout=4.0, follow_redirects=False) as client:
            response = await client.get(f"https://rdap.org/domain/{domain}")
            response.raise_for_status()
            payload = response.json()
        events = {event.get("eventAction"): event.get("eventDate") for event in payload.get("events", [])}
        return {"domain": domain, "creation_date": events.get("registration"), "expiration_date": events.get("expiration"), "registrar": payload.get("entities", [{}])[0].get("handle"), "status": payload.get("status", []), "available": True}, "ok"
    except Exception as exc:
        return {"domain": domain, "available": False, "error": type(exc).__name__}, "unavailable"
