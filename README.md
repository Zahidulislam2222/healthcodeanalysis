<h1 align="center">
  HealthCode Analysis<br>
  <sub>WordPress Elementor Automation Engine</sub>
</h1>

<p align="center">
  Clone a WordPress Elementor template site and swap all content — photos, text, SEO metadata, branding — in one command. Includes a dark glassmorphism design system with vanilla JS scroll animations.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/GitHub%20Actions-disabled%20by%20default-lightgrey?style=flat-square" alt="GitHub Actions disabled by default">
  <img src="https://img.shields.io/badge/tests-281%20passing-brightgreen?style=flat-square" alt="Tests">
  <img src="https://img.shields.io/badge/coverage-59%25-yellow?style=flat-square" alt="Coverage">
  <img src="https://img.shields.io/badge/python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/wordpress-REST%20API-21759B?style=flat-square&logo=wordpress&logoColor=white" alt="WordPress">
  <a href="https://docs.astral.sh/ruff/">
    <img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json&style=flat-square" alt="Ruff">
  </a>
  <img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="License">
</p>

---

## Overview

A full-stack WordPress automation platform with three core capabilities:

1. **Content Automation** — Clone an Elementor template site and programmatically replace all content (photos, text, headings, SEO metadata) for multiple customers via a single command.
2. **Dark Glassmorphism Design System** — A plugin-based visual overhaul with vanilla JS scroll animations, sticky header, glassmorphic cards, and responsive dark theme. Zero external dependencies.
3. **AskMe AI Chatbot** — A Cloudflare Worker-powered chatbot that answers visitor questions from a public content index generated during publishing, with Dialogflow ES for greetings/chitchat. It remains available when WordPress is offline.

**Frontend:** [healthcodeanalysis.pages.dev](https://healthcodeanalysis.pages.dev)

**WP Admin Demo:** [local wp-admin](http://127.0.0.1:8889/wp-admin/)

## Domain-Independent Demo Publishing

The durable demo does not depend on `healthcodeanalysis.com` or a running WordPress server:

```text
Local WordPress -> static exporter -> Cloudflare Pages
                         +---------> bundled AskMe content index
```

- Public frontend: `https://healthcodeanalysis.pages.dev`
- Local authoring: `http://127.0.0.1:8889/wp-admin/`
- Chatbot: `https://askme.regenai-workers.workers.dev`

Publish all frontend and chatbot content from PowerShell:

```powershell
.\scripts\publish-static-site.ps1
```

The command exports every published page, post, category archive, referenced WordPress asset, and a public-only content index. It validates AskMe, deploys Pages, and then deploys the Worker with the same index bundled into it. Wrangler OAuth must already be logged in; credentials stay in ignored local files or Cloudflare secrets.

For export-only validation:

```bash
python scripts/export_static_site.py --source http://127.0.0.1:8889 --clean
```

The public site and AskMe continue working when WordPress and Docker are offline. WordPress changes become public only after running the publish command.

The connection is intentionally one-way: WordPress is the authoring source and Pages is a static published snapshot. Editing generated files does not write back to WordPress. WordPress-only MetForm controls are visibly blocked in the static export instead of submitting to dead REST endpoints; use the local WordPress demo when testing those forms.

### Local Demo Tunnel

The public tunnel is optional and must not run unless Cloudflare Access protects WP Admin. Start the normal local stack without a public tunnel:

```bash
cd docker
docker compose up -d
```

Start the tunnel only for a protected client demo:

```bash
docker compose --profile demo-tunnel up -d cloudflared
```

## Architecture

```
healthcodeanalysis/
├── scripts/
│   ├── wp_client.py                    # WordPress REST API client
│   ├── elementor_parser.py             # Elementor JSON tree parser/modifier
│   ├── content_swapper.py              # Image, text, SEO swap orchestrator
│   ├── config_validator.py             # Customer config schema validation
│   ├── deploy_customer.py              # One-command customer deployment
│   ├── clone_site.py                   # cPanel site cloning + migration scripts
│   ├── export_static_site.py            # Deterministic WordPress-to-Pages exporter
│   ├── publish-static-site.ps1          # Validates and publishes Pages + AskMe
│   ├── healthcode-api-bridge.php       # WP plugin: REST API for Elementor data + rate limiting
│   ├── hc-auto-activate.php            # MU-plugin: security headers + auto-loads design system
│   └── healthcode-design-system/       # Dark theme plugin (v3.7.4)
│       ├── healthcode-design-system.php  # Loader: fonts, Rocket Loader bypass
│       ├── css/healthcode-theme.css      # 900+ lines dark glassmorphism CSS
│       └── js/healthcode-animations.js   # Vanilla JS: IntersectionObserver, particles, counters
├── configs/
│   └── customer-template.json          # Config template with real page IDs
├── tests/                              # 281 historical/core checks + exporter tests
├── workers/
│   └── askme/                          # AskMe chatbot Cloudflare Worker
│       ├── wrangler.toml               # Worker config (secrets via wrangler)
│       ├── src/index.js                # Dialogflow + WP REST API search
│       └── package.json                # Dependencies
├── .github/workflows/
│   ├── ci.yml                          # Retained CI/cPanel/Worker pipeline (disabled)
│   ├── deploy.yml                      # Customer deployment pipeline (disabled)
│   └── configure-admin-demo-dns.yml    # Optional demo DNS pipeline (disabled)
├── .env.sample                         # Environment variable template
└── .cpanel.yml                         # cPanel deployment task mapping
```

## Content Automation Engine

### The Problem
A medical WordPress site built with Elementor has 6+ pages, each with photos, text, and SEO metadata. Manually recreating the same site for each new customer is slow, error-prone, and doesn't scale.

### The Solution

```bash
python scripts/deploy_customer.py configs/customer.json --dry-run   # preview changes
python scripts/deploy_customer.py configs/customer.json             # deploy live
```

One command reads a customer config and executes the full pipeline:

| Capability | Details |
|---|---|
| **Image swap** | Upload photos via REST API, replace URLs in Elementor JSON (filename or exact match) |
| **Text swap** | Replace headings and text-editor widgets by index or widget ID |
| **SEO swap** | Update Rank Math title, description, keywords, Open Graph tags per page |
| **Site identity** | Change title, tagline, upload and activate logo + favicon |
| **Site cloning** | cPanel UAPI: create databases, users, generate migration bash scripts |
| **Dry-run** | Preview every change without modifying the live site |
| **Config validation** | Catch errors in customer JSON before deployment |

### Customer Config Format

```json
{
  "customer_name": "MediCare Plus",
  "site_settings": {
    "title": "MediCare Plus",
    "description": "Your trusted health partner",
    "logo_file": "assets/medicare/logo.png"
  },
  "pages": [
    {
      "page_id": 1210,
      "page_name": "About Us",
      "headings": [{"index": 0, "new_text": "About MediCare Plus"}],
      "images": [{"old_url": "About-US.webp", "new_file": "assets/medicare/about.webp", "match_mode": "filename"}],
      "meta": {"rank_math_title": "About Us - MediCare Plus"}
    }
  ]
}
```

Full template: [`configs/customer-template.json`](configs/customer-template.json)

## Dark Glassmorphism Design System

A WordPress plugin that applies a dark medical AI theme on top of any Elementor site. Activates/deactivates per customer clone — no Elementor template editing required.

### Design

- **Colors:** Deep navy base (#0a0e1a), cyan-blue gradient accents, emerald health, purple AI
- **Typography:** Space Grotesk (headings), Inter (body)
- **Effects:** Glassmorphic cards, scroll reveal animations, counter animations, ECG pulse line, floating particles
- **Responsive:** Mobile-first, breakpoints at 1024/768/480px, respects `prefers-reduced-motion`

### Technical Highlights

- **Zero dependencies** — All animations use vanilla IntersectionObserver + CSS transitions. No GSAP, no animation libraries, no license concerns for multi-domain deployment
- **Cloudflare Rocket Loader bypass** — `data-cfasync="false"` via `script_loader_tag` filter keeps animation JS loading normally
- **Elementor container system** — All CSS verified against live DOM. Targets new flexbox containers (`e-con`, `e-parent`, `e-child`), not legacy sections
- **Sticky header** — `position: fixed` on inner container. All animation selectors scoped to `[data-elementor-type="wp-page"]` to prevent animating header/footer templates
- **Popup ownership** — Royal Addons Elementor template 2732 is the active login/register interface; the exporter removes the obsolete competing custom popup when both are rendered
- **Popup background fix** — The design system excludes Royal popup descendants from global background stripping and restores the template shell through a MutationObserver
- **CSS specificity management** — Nuclear dark overrides on Elementor elements with careful exclusions for popups, buttons, and social icons
- **NeuroScan AJAX filter patch** — Code Snippets filter uses `container.next()` which fails due to Elementor container wrapping. Patched with global querySelector + direct AJAX call
- **Smooth scrolling** — `scroll-behavior: smooth` on HTML element
- **Dark theme overrides** — All CSS selectors verified from live DOM via `curl` and browser Console `getComputedStyle()` inspection

### WordPress Plugin Stack

| Plugin | Role |
|---|---|
| Elementor | Page builder (all layouts) |
| Rank Math SEO | SEO metadata, Open Graph |
| Jeg Elementor Kit | Nav menu widget (`jkit_nav_menu`) |
| Royal Elementor Addons | Additional widgets, popup |
| Advanced Custom Fields | Custom data fields |
| MetForm | Contact/login forms |
| Astra | Theme (Header Footer Builder) |

## AskMe AI Chatbot

A serverless chatbot running on Cloudflare Workers (free tier) that gives visitors real answers from site content — not canned responses.

### How It Works

```
User: "What is eGFR calculator?"
    │
    ├── Dialogflow ES → classifies intent (greeting? content question?)
    │
    ├── If greeting/chitchat → Dialogflow responds ("How can I help you?")
    └── If content question → Worker searches the bundled public index
        ├── Scores matching page/post titles and content
        ├── Retries with eligible sub-phrases when needed
        ├── Extracts the relevant indexed content
        └── Returns snippet + link to the article
```

### Capabilities

| Feature | How |
|---|---|
| **Content search** | Searches generated page/post titles and body text without a runtime WordPress dependency |
| **Snippet extraction** | Pulls the most relevant sentence from matched post content |
| **Category browsing** | Lists all categories with post counts, shows posts per category |
| **Latest / Popular** | Returns N latest or featured posts (user specifies count) |
| **Greeting detection** | Catches typos like "hellow" locally, falls back gracefully |
| **Smart retry** | If "blood pressure wearable" finds nothing, retries with "blood pressure" |

### Architecture Decisions

- **Content bundled at publish time** — Pages and AskMe use the same generated public index, so WordPress can remain offline
- **Deterministic fallback search** — Short medical acronyms and remaining eligible terms are handled without a live CMS query
- **Google OAuth token cached** — Avoids re-auth on every request (~300ms saved)
- **Dialogflow only for chitchat** — All content intelligence handled by the Worker
- **Zero cost** — Cloudflare Workers free (100K req/day) + Dialogflow ES free (1K req/day)
- **No hand-maintained chatbot content** — Posts, pages, categories, and links are regenerated from WordPress during publication
- **XSS-safe** — All output sanitized via `escapeHtml()` / `escapeAttr()`
- **Credentials in Cloudflare Secrets** — Google service account key never in source code

### Deploy

```bash
cd workers/askme && npm install
npx wrangler secret put GOOGLE_CLIENT_EMAIL    # service account email
npx wrangler secret put DIALOGFLOW_PROJECT     # Dialogflow project ID
npx wrangler secret put GOOGLE_PRIVATE_KEY     # PEM private key
npx wrangler deploy                            # deploys the configured AskMe Worker
```

The normal publishing path is `scripts/publish-static-site.ps1`, which exports the same content index for Pages and AskMe before deployment.

## CI/CD Pipeline

The repository preserves the original GitHub Actions implementation as client-reviewable proof, but it is intentionally disabled by default. Workflows are manual-only and every job requires the repository variable `HEALTHCODE_ACTIONS_ENABLED=true` before it can execute.

```
Historical / available pipeline
    │
    ├── Lint & Security ────── Ruff linter + Bandit security scan + PHP syntax
    ├── Tests ──────────────── 281 tests across 4 suites
    ├── Coverage ───────────── 59% with threshold enforcement
    ├── Config Validation ──── Customer JSON schema check
    │
    ├── Deploy Plugin ─────── Uploads PHP/CSS/JS to cPanel via File Manager API
    │                          then flushes Elementor cache
    │
    └── Deploy Worker ─────── Deploys AskMe chatbot to Cloudflare Workers
                               then verifies Worker responds to POST
```

The retained workflows are:

- `ci.yml` — lint, tests, coverage, config validation, historical cPanel plugin deploy, and Worker deploy
- `deploy.yml` — parameterized customer dry run or explicit production deployment
- `configure-admin-demo-dns.yml` — optional Cloudflare DNS setup for the local WordPress demo tunnel

The customer workflow prevents a successful dry run from falling through into a production deployment. The cPanel and old-domain steps are historical/inactive and must not be described as currently live.

**Current safety state:** automatic push/PR triggers removed | all jobs guarded by `HEALTHCODE_ACTIONS_ENABLED` | Dependabot version updates paused with `open-pull-requests-limit: 0`

**Quality gates available when re-enabled:** Pre-commit hooks (Ruff lint/format, secret detection) | GitHub Secrets | tests and config validation

## Security Hardening

The platform includes layered security protections:

### HTTP Security Headers

Set at the mu-plugin level (`hc-auto-activate.php`) for earliest execution — fires before LiteSpeed Cache or any other plugin:

| Header | Value | Purpose |
|---|---|---|
| `X-Frame-Options` | `SAMEORIGIN` | Prevents clickjacking |
| `X-Content-Type-Options` | `nosniff` | Prevents MIME-type sniffing |
| `Referrer-Policy` | `strict-origin-when-cross-origin` | Controls referrer leakage |
| `Permissions-Policy` | `camera=(), microphone=(), geolocation=()` | Restricts browser APIs |
| `Content-Security-Policy` | Full allowlist (see below) | Prevents XSS/injection |

> HSTS is intentionally omitted from PHP — Cloudflare handles it. Setting HSTS in PHP on cPanel shared hosting causes redirect loops.

### Content Security Policy (CSP)

Every CSP source verified from browser Console errors:

| Directive | Sources | Why |
|---|---|---|
| `script-src` | `'self' 'unsafe-inline' 'unsafe-eval'` + Cloudflare + Google | MetForm templates, reCAPTCHA v3, Cloudflare Analytics |
| `style-src` | `'self' 'unsafe-inline'` + Google Fonts | Elementor inline styles |
| `font-src` | `'self'` + Google Fonts + `data:` | Plugin base64 inline fonts |
| `img-src` | `'self' data: https:` | External images + SVG data URIs |
| `connect-src` | `'self'` + Google + legacy direct AskMe Worker host | reCAPTCHA + optional WordPress chatbot connection; Pages uses same-origin `/askme-proxy` |
| `worker-src` | `blob:` | WordPress emoji detection worker |
| `frame-src` | `'self'` + Google | WordPress update iframe + reCAPTCHA iframe |
| `frame-ancestors` | `'self'` | Prevents clickjacking |

### REST API Rate Limiting

All `/healthcode/v1/` endpoints are rate-limited using WordPress transients:

- **GET endpoints:** 60 requests/minute per IP
- **POST endpoints:** 20 requests/minute per IP
- Uses `CF-Connecting-IP` header for accurate IP detection behind Cloudflare
- Returns `HTTP 429` with `Retry-After` header when exceeded
- Standard WP REST routes (`/wp/v2/`) are unaffected

### API Security

- **Header-only authentication** — API key accepted only via `X-HC-API-Key` header (query string fallback removed to prevent log exposure)
- **Path traversal protection** — Plugin activation endpoint validates paths with regex whitelist (`folder/file.php` format only)
- **Generic error messages** — Server filesystem paths never exposed in API responses
- **SQL parameterization** — All queries use `$wpdb->prepare()`

### Additional Measures

- All credentials in `.env` (gitignored) and GitHub Secrets — never committed to git
- No hardcoded usernames, server paths, or domains in tracked files
- Pre-commit hook detects private keys before commit
- Ruff security scanner (Bandit rules) is configured in the disabled-by-default CI workflow
- Docker dev environment: pinned image versions, parameterized passwords, resource limits, healthchecks
- All scripts are open-source (MIT) with zero commercial library dependencies

## Quick Start

```bash
git clone https://github.com/Zahidulislam2222/healthcodeanalysis.git
cd healthcodeanalysis
pip install -r requirements.txt
cp .env.sample .env   # Add your credentials
```

```bash
# Deploy content
python scripts/deploy_customer.py configs/customer-template.json --dry-run

# Clone to new domain
python scripts/clone_site.py --source healthcodeanalysis.com --target newcustomer.com --generate-script

# Run tests
python tests/test_phase1.py && python tests/test_phase2_4.py && python tests/test_phase6.py && python tests/test_e2e_swap.py
```

## Environment Variables

```bash
# WordPress (required)
WP_SITE_URL=https://example.com
WP_USERNAME=admin
WP_APP_PASSWORD=xxxx xxxx xxxx xxxx xxxx xxxx
HC_API_KEY=your_healthcode_api_key

# cPanel (historical/optional cloning and deployment path)
CPANEL_URL=https://your-server.com:2083
CPANEL_USERNAME=your_user
CPANEL_API_TOKEN=your_token
```

Local credentials belong in `.env` (gitignored); workflow credentials belong in GitHub Secrets if Actions are deliberately re-enabled. Never hardcode credentials.

## Testing

| Suite | Tests | Covers |
|---|---|---|
| Phase 1 | 71 | Core utilities: API client, Elementor parser, config validator |
| Phase 2-4 | 46 | Image upload/swap, text replacement, SEO meta updates |
| Phase 6 | 38 | cPanel cloning, database creation, migration scripts |
| E2E | 126 | Full content swap verification across all widget types |
| **Historical/core total** | **281** | Customer automation and cPanel implementation |
| Static exporter | 11 | Origin rewriting, generated-index shape, static form guard, bundle validation |

Latest verified local run: **281/281 historical/core checks and 11/11 exporter tests passed**.

## Tech Stack

**Automation:** Python 3.10+ | Requests | WordPress REST API | cPanel UAPI

**Design System:** Vanilla JS (IntersectionObserver + CSS transitions) | CSS Custom Properties | Google Fonts

**WordPress:** Elementor | Rank Math SEO | ACF | Astra | LiteSpeed Cache

**Chatbot:** Cloudflare Workers | Dialogflow ES | Bundled public content-index search

**CI/CD (preserved, disabled by default):** GitHub Actions | cPanel File Manager API | Wrangler (Cloudflare) | Dependabot configuration

**Quality:** Ruff (lint + format + security) | 281 core checks + 11 exporter tests | Pre-commit hooks | Secret detection

## License

[MIT](LICENSE)
