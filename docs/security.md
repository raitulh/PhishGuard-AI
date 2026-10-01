# Security Notes

- User text is untrusted data in the Ollama prompt and is never treated as instructions.
- Localhost, loopback, link-local, reserved, unspecified, and private IP destinations are rejected by the URL safety helper.
- Provider API keys belong only in the backend environment.
- Raw submitted message content is not stored by the analysis service.
- CORS uses the configured frontend origin.
- Production deployment still needs HTTPS, secure auth cookies, edge rate limiting, secret rotation, and private model networking.
