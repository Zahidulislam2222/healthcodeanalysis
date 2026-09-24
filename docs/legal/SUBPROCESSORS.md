# Service providers (sub-processors)

Providers that can process personal data (mainly connection metadata) when the live site is used. **Last reviewed:** 24 September 2026.

| Provider | Service | Data involved | Used by the live reader path? |
|---|---|---|---|
| Cloudflare, Inc. | CDN, TLS termination, DDoS protection, DNS | IP address, request headers, URLs, security signals | **Yes** |
| `[HOSTING PROVIDER — operator to name]` | Virtual server hosting the origin, database and backups | Server logs (IP address, requests), editor account data, content | **Yes** |
| GitHub, Inc. | Source-code hosting | Contributor data only; no reader data | No |
| Cloudflare Workers | Runtime for the retained AskMe chatbot | Chat text submitted to the Worker | Not by the native site; **yes** for visitors of the legacy pages.dev snapshot |
| Google (Dialogflow ES) | Greeting/chit-chat intent detection for the retained AskMe chatbot | Chat text classified as greetings/chit-chat | Not by the native site; **yes** for visitors of the legacy pages.dev snapshot |

## Notes for the operator

- A real privacy policy must **name** the hosting provider and state where data is processed. International transfers need a documented mechanism where GDPR or UK GDPR applies.
- Enter a data processing agreement with each provider that processes personal data on your behalf (GDPR Art. 28).
- Adding any provider (analytics, email, payments, AI models) requires updating this list, the privacy policy and [COOKIES-AND-STORAGE.md](COOKIES-AND-STORAGE.md) **before** the feature goes live.
