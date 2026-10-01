# API

## `GET /health`
Returns configured provider visibility without exposing credentials.

## `POST /api/v1/analyze`

```json
{"text":"Your account is suspended. Verify now at https://example.example/login"}
```

The response includes `risk_score`, `risk_level`, `confidence`, `red_flags`, normalized URL features, domain/provider payloads, structured evidence, recommendations, and provider status. `text` and `url` are both optional individually but one is required. Text is limited to 10,000 characters and URLs to 4,096 characters.
