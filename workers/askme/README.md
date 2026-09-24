# AskMe Worker (retained)

**Status: Retained, still publicly reachable.** The native site uses browser-side library search and never calls this Worker. The deployed Worker still answers through the legacy `healthcodeanalysis.pages.dev` snapshot (`/askme-proxy`). Either decommission it with that snapshot or fix the issues below.

A Cloudflare Worker that answers visitor questions from a **bundled public content index**, with Dialogflow ES used only for greetings and chit-chat. It keeps working when WordPress is offline, because content is bundled at publish time.

## How it works

```
POST { "query": "...", "sessionId": "..." }
   │
   ├─ Dialogflow ES (greeting / small talk?) ── yes ─► short reply
   │        (if unavailable, falls back to local small-talk detection)
   │
   └─ content question ─► score titles/body in content-index.json
                          ├─ retry with shorter eligible sub-phrases
                          └─ reply with a snippet + link to the article
```

- `POST` and `OPTIONS` only; other methods return `405`.
- Query and session ID lengths are capped; the session ID is restricted to `[A-Za-z0-9_-]`.
- All output is HTML-escaped.
- The Google OAuth access token is cached between requests.
- Answers are retrieval over published content. **It does not generate medical advice.**

## Files

| File | Purpose |
|---|---|
| `src/index.js` | Worker implementation |
| `wrangler.toml` | Worker name, compatibility date, observability. No secrets |
| `test/content-search.test.mjs` | Search behavior test |
| `content-index.json` | **Generated** by `scripts/export_static_site.py`; not committed |

## Secrets

Set with Wrangler; never commit them:

```bash
npx wrangler secret put GOOGLE_CLIENT_EMAIL   # service-account email
npx wrangler secret put GOOGLE_PRIVATE_KEY    # service-account PEM key
npx wrangler secret put DIALOGFLOW_PROJECT    # Dialogflow project ID
```

## Develop and deploy

```bash
cd workers/askme
npm ci
npx wrangler dev        # local
npx wrangler deploy     # requires Wrangler login to the intended account
```

The normal path was `scripts/publish-static-site.ps1`, which regenerates the content index for Pages and the Worker together.

## Known issues (fix, or decommission the public deployment)

1. **Test harness:** `npm test` fails under plain Node because `src/index.js` imports JSON without `with { type: "json" }`, and the generated index is not committed. Wrangler's bundler accepts the import; Node does not.
2. **CORS is `*` and there is no rate limiting.** Restrict `Access-Control-Allow-Origin` to the publication origin and add a rate limit. Both gaps are currently exposed through the legacy snapshot.
3. Re-enabling a chatbot requires an EU AI Act transparency review; see [AI transparency](../../docs/legal/AI-TRANSPARENCY.md).

## Cost

Built for the Cloudflare Workers free tier and the Dialogflow ES free quota. Check the providers' current limits before any traffic increase; exceeding free quotas can incur charges.
