# AI transparency statement

## Where AI is used

| Item | Use of AI | Disclosure |
|---|---|---|
| Hero brain illustration and 8-second motion sequence | Generated with an AI image/video model during design (offline, one-time) | Labelled on the site as AI-generated illustrative artwork, not a medical scan |
| Development assistance | AI coding assistants were used during development; changes pass the same review, tests and security scans as human-written code | This statement |

## Where AI is **not** used

- **No generative AI runs when readers use the site.** There are no per-visitor model calls.
- **"Ask the library" is retrieval, not generation.** It matches your query against a public index in your browser and links to existing pages. It does not write medical answers.
- **The medical prompt studio** builds a prompt text locally. It does not send it to any model.
- **No reader data is used to train models.** The site's `robots.txt` disallows the GPTBot training crawler while keeping ordinary search discovery.

## Retained AskMe chatbot

The repository contains a retained Cloudflare Worker chatbot. It answers from a bundled public content index and uses Dialogflow ES only for greetings. It is **not** called by the native site, but it remains publicly reachable through the legacy `healthcodeanalysis.pages.dev` snapshot (`/askme-proxy`), where visitor messages are processed by the Worker and greetings by Google Dialogflow. Keeping that snapshot online, re-enabling the chatbot elsewhere, or adding any generative model requires a new assessment of transparency (EU AI Act Art. 50), data transfers and medical-safety boundaries ([COMPLIANCE-REGISTER.md](COMPLIANCE-REGISTER.md)).

## Imported content

Imported demonstration articles may not have complete provenance, and parts may have been machine-assisted. They are unverified, excluded from indexing, and must be reviewed before real publication ([EDITORIAL-AND-COPYRIGHT-POLICY.md](EDITORIAL-AND-COPYRIGHT-POLICY.md)).
