# PhishGuard

**Don't just detect the link. Understand the trap.**

PhishGuard is an explainable phishing and social-engineering intelligence MVP. It combines deterministic URL signals, brand mismatch detection, rule-based semantic analysis, optional Ollama/Qwen analysis, RDAP domain intelligence, and optional VirusTotal reputation into a structured risk report.

## Repository

- `backend/`: FastAPI analysis API, SQLite persistence, engines, providers, and tests.
- `web/`: Next.js App Router product UI.
- `extension/`: Manifest V3 browser companion.
- `docs/`: architecture, security, and API notes.

## Run locally

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Open `http://localhost:8000/docs` and try `POST /api/v1/analyze` with:

```json
{"text":"Your bank account is suspended. Verify your password now at https://paypal-login.example/verify"}
```

External providers are optional. Without credentials or Ollama, the API uses clearly labeled rule-based analysis and unavailable provider statuses. Never treat a low observed risk result as a guarantee of safety.

## Web app

```powershell
cd web
npm install
npm run dev
```

Set `NEXT_PUBLIC_API_URL=http://localhost:8000` when needed. The browser extension calls the configured backend only; it contains no provider secrets.

## Security notes

The URL engine rejects localhost and private IP destinations before any provider request. Submitted text is treated as untrusted data for Ollama prompts. Raw message content is not persisted; scans store a SHA-256 input hash plus structured evidence. Production deployment still requires HTTPS, secure auth cookies/tokens, rate limiting at the edge, secret management, and a private Ollama network.

## Roadmap

Authentication, history retrieval, redirect inspection, API keys, Telegram, and team workflows are structured as follow-up modules. MCP integration is a roadmap item, not an implemented claim.
