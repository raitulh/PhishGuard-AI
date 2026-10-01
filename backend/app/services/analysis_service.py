import asyncio
import hashlib
import os
import sqlite3
from datetime import datetime, timezone
from uuid import uuid4
from app.engines.brand_engine import analyze_brand
from app.engines.risk_engine import fuse_evidence
from app.engines.social_engine import analyze_social
from app.engines.url_engine import analyze_url, extract_urls
from app.providers.ollama import OllamaProvider
from app.providers.rdap import lookup_domain
from app.providers.virustotal import VirusTotalProvider
from app.providers.safebrowsing import SafeBrowsingProvider
from app.providers.urlhaus import URLhausProvider
from app.schemas.analysis import AnalyzeRequest, AnalyzeResponse, Evidence, ProviderStatus, RedFlag

class AnalysisService:
    def __init__(self, db_path: str = "phishguard.db", ollama: OllamaProvider | None = None, vt: VirusTotalProvider | None = None, sb: SafeBrowsingProvider | None = None, urlhaus: URLhausProvider | None = None):
        self.db_path = db_path
        self.ollama = ollama or OllamaProvider(os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"), os.getenv("OLLAMA_MODEL", "qwen3:1.7b"))
        self.vt = vt or VirusTotalProvider(os.getenv("VIRUSTOTAL_API_KEY"))
        self.sb = sb or SafeBrowsingProvider(os.getenv("GOOGLE_SAFE_BROWSING_API_KEY"))
        self.urlhaus = urlhaus or URLhausProvider(os.getenv("URLHAUS_API_KEY"), os.getenv("ENABLE_URLHAUS", "false").lower() == "true")
        self._initialize_db()

    def _initialize_db(self):
        with sqlite3.connect(self.db_path) as db:
            db.execute("CREATE TABLE IF NOT EXISTS scans (id TEXT PRIMARY KEY, input_hash TEXT NOT NULL, risk_score INTEGER NOT NULL, risk_level TEXT NOT NULL, confidence TEXT NOT NULL, created_at TEXT NOT NULL)")
            db.execute("CREATE TABLE IF NOT EXISTS evidence (id INTEGER PRIMARY KEY AUTOINCREMENT, scan_id TEXT NOT NULL, source TEXT NOT NULL, signal TEXT NOT NULL, severity TEXT NOT NULL, weight INTEGER NOT NULL, evidence TEXT NOT NULL, metadata_json TEXT NOT NULL)")
            try:
                db.execute("ALTER TABLE scans ADD COLUMN target TEXT DEFAULT ''")
            except sqlite3.OperationalError:
                pass

    def get_scans(self, limit: int = 50) -> list[dict]:
        with sqlite3.connect(self.db_path) as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cols = [col[1] for col in cursor.execute("PRAGMA table_info(scans)").fetchall()]
            has_target = "target" in cols
            query = f"SELECT id, input_hash, {'target, ' if has_target else ''}risk_score, risk_level, confidence, created_at FROM scans ORDER BY created_at DESC LIMIT ?"
            cursor.execute(query, (limit,))
            return [dict(row) for row in cursor.fetchall()]

    def get_scan(self, scan_id: str) -> dict | None:
        with sqlite3.connect(self.db_path) as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute("SELECT * FROM scans WHERE id = ?", (scan_id,))
            scan = cursor.fetchone()
            if not scan:
                return None
            cursor.execute("SELECT source, signal, severity, weight, evidence FROM evidence WHERE scan_id = ?", (scan_id,))
            scan_dict = dict(scan)
            scan_dict["evidence"] = [dict(r) for r in cursor.fetchall()]
            return scan_dict

    async def analyze(self, request: AnalyzeRequest) -> AnalyzeResponse:
        text = (request.text or "").strip()
        urls = extract_urls(text)
        if request.url:
            urls.append(request.url.strip())
        normalized_urls = []
        for candidate in dict.fromkeys(urls):
            try:
                normalized_urls.append(analyze_url(candidate))
            except ValueError:
                continue
        primary_url = normalized_urls[0] if normalized_urls else {}
        domain = primary_url.get("hostname", "")
        social_task = self.ollama.analyze(text) if text else asyncio.sleep(0, result=(None, "not_requested"))
        if domain:
            rdap_task = lookup_domain(domain)
            vt_task = self.vt.get_url_report(primary_url["normalized_url"])
            sb_task = self.sb.check_url(primary_url["normalized_url"])
            urlhaus_task = self.urlhaus.check_url(primary_url["normalized_url"])
            social_result, rdap_result, vt_result, sb_result, urlhaus_result = await asyncio.gather(social_task, rdap_task, vt_task, sb_task, urlhaus_task)
        else:
            social_result = await social_task
            rdap_result = ({"available": False, "reason": "no_domain"}, "not_requested")
            vt_result = ({"available": False, "reason": "no_url"}, "not_requested")
            sb_result = ({"available": False, "reason": "no_url"}, "not_requested")
            urlhaus_result = ({"available": False, "reason": "no_url"}, "not_requested")
        social = social_result[0] if social_result[0] else analyze_social(text)
        social_status = social_result[1]
        rdap, rdap_status = rdap_result
        reputation, vt_status = vt_result
        safebrowsing, sb_status = sb_result
        urlhaus, urlhaus_status = urlhaus_result
        brand = analyze_brand(domain, text) if domain else {"matches": [], "impersonation": False}
        evidence: list[Evidence] = []
        if primary_url:
            if primary_url.get("is_ip_host"):
                evidence.append(Evidence(source="url_engine", signal="ip_hostname", severity="high", weight=18, evidence="The URL uses a numeric IP address instead of a domain name."))
            if primary_url.get("has_punycode"):
                evidence.append(Evidence(source="url_engine", signal="punycode", severity="high", weight=15, evidence="The hostname contains punycode, which can obscure lookalike characters."))
            if primary_url.get("has_at_symbol"):
                evidence.append(Evidence(source="url_engine", signal="at_symbol", severity="high", weight=18, evidence="The URL contains an @ symbol that can disguise the actual destination."))
            if primary_url.get("keyword_hits"):
                evidence.append(Evidence(source="url_engine", signal="suspicious_path_keywords", severity="medium", weight=10, evidence="The URL includes account or credential workflow keywords."))
            if primary_url.get("suspicious_parameters"):
                evidence.append(Evidence(source="url_engine", signal="suspicious_parameters", severity="medium", weight=8, evidence="The URL contains redirect or session-like parameters."))
        if brand.get("impersonation"):
            evidence.append(Evidence(source="brand_engine", signal="brand_domain_mismatch", severity="high", weight=20, evidence="The message references a recognizable brand while the registered domain does not match its official domains."))
        for signal, title, weight in [("urgency", "urgency_pressure", 12), ("credential_request", "credential_request", 20), ("authority_impersonation", "authority_impersonation", 10), ("fear", "fear_language", 8), ("payment_request", "payment_request", 12)]:
            if social.get(signal, 0) >= 0.5:
                evidence.append(Evidence(source=f"{social.get('provider', 'rules')}_analysis", signal=title, severity="high" if weight >= 18 else "medium", weight=weight, evidence=f"Language patterns indicate {title.replace('_', ' ')}."))
        if reputation.get("malicious", 0) or reputation.get("suspicious", 0):
            evidence.append(Evidence(source="virustotal", signal="provider_detections", severity="high", weight=30, evidence="A configured reputation provider reported malicious or suspicious detections."))
        if safebrowsing.get("is_threat"):
            threat_labels = ", ".join(safebrowsing.get("threat_types", ["Phishing/Malware"]))
            evidence.append(Evidence(source="google_safebrowsing", signal="safebrowsing_threat", severity="high", weight=35, evidence=f"Google Safe Browsing flagged this destination as {threat_labels}."))
        if urlhaus.get("is_threat"):
            threat_name = urlhaus.get("threat") or "malware_distribution"
            evidence.append(Evidence(source="urlhaus", signal="urlhaus_threat", severity="high", weight=35, evidence=f"URLhaus (abuse.ch) flagged this destination as an active threat ({threat_name})."))
        provider_status = {"ollama": social_status if social_status != "not_requested" else "not_requested", "virustotal": vt_status, "safebrowsing": sb_status, "urlhaus": urlhaus_status, "rdap": rdap_status, "redirect": "not_run"}
        score, level, confidence = fuse_evidence(evidence, provider_status)
        flags = [RedFlag(title=item.signal.replace("_", " ").title(), severity=item.severity, evidence=item.evidence) for item in sorted(evidence, key=lambda item: item.weight, reverse=True)[:3]]
        recommendation = ["Do not click the link.", "Do not enter passwords, OTPs, or payment information.", "Verify through the organization's official website."] if score >= 50 else ["Review the sender and destination carefully.", "Verify unexpected requests through a trusted channel."]
        scan_id = f"scan_{uuid4().hex[:12]}"
        target_preview = primary_url.get("normalized_url") or (text[:80] + "..." if len(text) > 80 else text) or "N/A"
        with sqlite3.connect(self.db_path) as db:
            cols = [col[1] for col in db.execute("PRAGMA table_info(scans)").fetchall()]
            if "target" in cols:
                db.execute("INSERT INTO scans (id, input_hash, target, risk_score, risk_level, confidence, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)", (scan_id, hashlib.sha256((text + str(urls)).encode()).hexdigest(), target_preview, score, level.value, confidence.value, datetime.now(timezone.utc).isoformat()))
            else:
                db.execute("INSERT INTO scans (id, input_hash, risk_score, risk_level, confidence, created_at) VALUES (?, ?, ?, ?, ?, ?)", (scan_id, hashlib.sha256((text + str(urls)).encode()).hexdigest(), score, level.value, confidence.value, datetime.now(timezone.utc).isoformat()))
            db.executemany("INSERT INTO evidence (scan_id, source, signal, severity, weight, evidence, metadata_json) VALUES (?, ?, ?, ?, ?, ?, ?)", [(scan_id, item.source, item.signal, item.severity, item.weight, item.evidence, "{}") for item in evidence])
        return AnalyzeResponse(scan_id=scan_id, risk_score=score, risk_level=level, confidence=confidence, summary="Multiple suspicious signals were identified." if score >= 50 else "No strong phishing pattern was observed, but absence of detection does not prove safety.", red_flags=flags, url_analysis=primary_url, domain_analysis={"domain": domain, "brand": brand, **rdap}, reputation=reputation, safebrowsing=safebrowsing, urlhaus=urlhaus, social_engineering=social, redirect_analysis={"redirect_count": 0, "chain": [], "final_url": primary_url.get("normalized_url")}, evidence=evidence, recommendation=recommendation, provider_status=ProviderStatus(**provider_status))
