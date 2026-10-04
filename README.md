# NovaWebhookRelay

Self-hosted signed webhook inbox. `POST /webhook` accepts raw JSON only when `X-Nova-Signature` is a valid HMAC-SHA256 using `NOVAWEBHOOK_SECRET`; accepted payloads are stored in SQLite. This release receives and stores events; forwarding/retry delivery is a later milestone.
