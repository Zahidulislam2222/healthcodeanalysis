<h1 align="center">
  HealthCode Analysis<br>
  <sub>WordPress Elementor Automation Engine</sub>
</h1>

<p align="center">
  Clone a WordPress Elementor template site and swap all content — photos, text, SEO metadata, branding — in one command. Includes a dark glassmorphism design system with GSAP animations.
</p>

<p align="center">
  <a href="https://github.com/Zahidulislam2222/healthcodeanalysis/actions/workflows/ci.yml">
    <img src="https://img.shields.io/github/actions/workflow/status/Zahidulislam2222/healthcodeanalysis/ci.yml?branch=main&label=CI&style=flat-square" alt="CI">
  </a>
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

A full-stack WordPress automation platform with two core capabilities:

1. **Content Automation** — Clone an Elementor template site and programmatically replace all content (photos, text, headings, SEO metadata) for multiple customers via a single command.
2. **Dark Glassmorphism Design System** — A plugin-based visual overhaul with GSAP scroll animations, sticky header, glassmorphic cards, and responsive dark theme.

**Live Site:** [healthcodeanalysis.com](https://healthcodeanalysis.com)

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
│   ├── healthcode-api-bridge.php       # WP plugin: REST API for Elementor data + rate limiting
│   ├── hc-auto-activate.php            # MU-plugin: security headers + auto-loads design system
│   └── healthcode-design-system/       # Dark theme plugin (v3.4.0)
│       ├── healthcode-design-system.php  # Loader: GSAP, fonts, Rocket Loader bypass
│       ├── css/healthcode-theme.css      # 900+ lines dark glassmorphism CSS
│       └── js/healthcode-animations.js   # GSAP scroll reveals, particles, counters
├── configs/
│   └── customer-template.json          # Config template with real page IDs
├── tests/                              # 281 tests (4 suites)
├── .github/workflows/
│   ├── ci.yml                          # CI + auto-deploy to cPanel on push
│   └── deploy.yml                      # Manual customer deployment with approval
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

- **Cloudflare Rocket Loader bypass** — `data-cfasync="false"` via `script_loader_tag` filter keeps GSAP loading normally while Rocket Loader optimizes everything else
- **Elementor container system** — All CSS verified against live DOM. Targets new flexbox containers (`e-con`, `e-parent`, `e-child`), not legacy sections
- **Sticky header** — `position: fixed` on inner container. All GSAP selectors scoped to `[data-elementor-type="wp-page"]` to prevent animating header/footer templates
- **Popup fix** — Custom popup (`#hca-custom-popup`) has inline `!important` transparent background set by JS. Overridden via MutationObserver
- **CSS specificity management** — Nuclear dark overrides on Elementor elements with careful exclusions for popups, buttons, and social icons

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

## CI/CD Pipeline

Every push to `main` triggers CI and automatic deployment:

```
git push to main
    │
    ├── Lint & Security ────── Ruff linter + Bandit security scan + PHP syntax
    ├── Tests ──────────────── 281 tests across 4 suites
    ├── Coverage ───────────── 59% with threshold enforcement
    ├── Config Validation ──── Customer JSON schema check
    │
    └── Deploy Plugin ─────── Uploads PHP/CSS/JS to cPanel via File Manager API
                               then flushes Elementor cache
```

**Customer deployments** are triggered manually via `workflow_dispatch` with dry-run preview and approval gate.

**Quality gates:** Pre-commit hooks (Ruff lint/format, secret detection) | Dependabot (weekly) | GitHub Secrets for all credentials

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
| `Content-Security-Policy` | Allowlist for self, Elementor inline, GSAP CDN, Google Fonts | Prevents XSS/injection |

> HSTS is intentionally omitted from PHP — Cloudflare handles it. Setting HSTS in PHP on cPanel shared hosting causes redirect loops.

### REST API Rate Limiting

All `/healthcode/v1/` endpoints are rate-limited using WordPress transients:

- **GET endpoints:** 60 requests/minute per IP
- **POST endpoints:** 20 requests/minute per IP
- Returns `HTTP 429` with `Retry-After` header when exceeded
- Standard WP REST routes (`/wp/v2/`) are unaffected

### Subresource Integrity (SRI)

External CDN scripts (GSAP core + ScrollTrigger) include `integrity` and `crossorigin` attributes to prevent CDN tampering.

### Additional Measures

- All credentials in `.env` (gitignored) and GitHub Secrets — never committed to git
- Pre-commit hook detects private keys before commit
- Ruff security scanner (Bandit rules) runs in CI
- Docker dev environment: pinned image versions, parameterized passwords, resource limits, healthchecks

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

# cPanel (for cloning + CI/CD deploy)
CPANEL_URL=https://your-server.com:2083
CPANEL_USERNAME=your_user
CPANEL_API_TOKEN=your_token
```

All credentials stored in `.env` (gitignored) and GitHub Secrets for CI/CD. Never hardcoded.

## Testing

| Suite | Tests | Covers |
|---|---|---|
| Phase 1 | 71 | Core utilities: API client, Elementor parser, config validator |
| Phase 2-4 | 46 | Image upload/swap, text replacement, SEO meta updates |
| Phase 6 | 38 | cPanel cloning, database creation, migration scripts |
| E2E | 126 | Full content swap verification across all widget types |
| **Total** | **281** | All operations idempotent and safe to re-run |

## Tech Stack

**Automation:** Python 3.10+ | Requests | WordPress REST API | cPanel UAPI

**Design System:** GSAP 3.12 + ScrollTrigger | CSS Custom Properties | Google Fonts

**WordPress:** Elementor | Rank Math SEO | ACF | Astra | LiteSpeed Cache

**CI/CD:** GitHub Actions | cPanel File Manager API | Dependabot

**Quality:** Ruff (lint + format + security) | 281 tests | Pre-commit hooks | Secret detection

## License

[MIT](LICENSE)
