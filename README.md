<h1 align="center">
  HealthCode Analysis<br>
  <sub>WordPress Elementor Automation Engine</sub>
</h1>

<p align="center">
  Clone a WordPress template site and swap all content — photos, text, SEO metas — in one command.
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

<br>

## The Problem

A medical WordPress site built with Elementor has 6 pages, each with photos, text, and SEO metadata. Creating the same site for a new customer means manually editing every page — slow, error-prone, and doesn't scale.

## The Solution

```
python scripts/deploy_customer.py configs/customer.json --dry-run   # preview
python scripts/deploy_customer.py configs/customer.json             # deploy
```

One command reads a customer config, connects to WordPress via REST API, and swaps everything:

```
Customer JSON ──> deploy_customer.py ──> WordPress REST API
                        |
         ┌──────────────┼──────────────┐
         |              |              |
    Upload new     Replace text    Update Rank Math
    photos &       & headings in   SEO title, desc,
    swap URLs in   Elementor       keywords & OG
    Elementor JSON widgets         tags
         |              |              |
         └──────────────┼──────────────┘
                        |
                  Flush cache
                  (Elementor + LiteSpeed)
```

## What It Does

| Capability | Details |
|---|---|
| **Swap photos** | Upload images via REST API, replace URLs in Elementor JSON (filename or exact match) |
| **Swap text** | Replace headings and text-editor widgets by index or Elementor widget ID |
| **Swap SEO metas** | Update Rank Math title, description, keywords, Open Graph tags per page |
| **Update site identity** | Change site title, tagline, upload and activate logo + favicon |
| **Clone sites** | Create cPanel databases, generate full migration bash scripts |
| **Dry-run mode** | Preview every change without modifying the live site |
| **Validate configs** | Catch errors in customer JSON before deployment |

## Quick Start

```bash
git clone https://github.com/Zahidulislam2222/healthcodeanalysis.git
cd healthcodeanalysis
pip install -r requirements.txt
cp .env.sample .env   # Add your WordPress credentials
```

```bash
# Deploy content for a customer
python scripts/deploy_customer.py configs/customer-template.json --dry-run

# Clone template to a new domain
python scripts/clone_site.py --source healthcodeanalysis.com --target newcustomer.com --generate-script

# Validate a config
python scripts/config_validator.py configs/customer-template.json
```

## Scripts

| Script | What It Does |
|---|---|
| `deploy_customer.py` | Master orchestrator — one command runs all swaps for a customer |
| `content_swapper.py` | Handles image upload/replace, text swap, SEO meta update |
| `elementor_parser.py` | Parses and modifies Elementor JSON data (nested widget tree) |
| `wp_client.py` | WordPress REST API client with auth, media upload, cache flush |
| `config_validator.py` | Validates customer config JSON before deployment |
| `clone_site.py` | cPanel UAPI — creates databases, users, generates migration scripts |
| `healthcode-api-bridge.php` | WordPress plugin — exposes Elementor data and Rank Math via REST |

## CI/CD Pipeline

Every push triggers **4 parallel CI jobs** and an automatic plugin deployment:

```
git push to main
    │
    ├── CI (automatic, ~30s)
    │   ├── Lint & Security ──── Ruff + Bandit + PHP syntax
    │   ├── Tests ───────────── 281 tests across 4 suites
    │   ├── Coverage ────────── 59% with enforcement
    │   └── Validate ────────── Customer config schema check
    │
    ├── CD: Plugin Deploy (automatic)
    │   └── .cpanel.yml ──────── Copies PHP plugin to live site via SSH deploy key
    │
    └── CD: Customer Deploy (manual trigger with approval gate)
        ├── Validate config
        ├── Dry-run preview
        ├── Manual approval
        └── Live deploy + verification
```

**Quality gates:** Pre-commit hooks (Ruff, secret detection) | Dependabot (weekly) | Branch protection

## Testing

```bash
python tests/test_phase1.py        # 71 unit tests
python tests/test_phase2_4.py      # 46 content swap tests
python tests/test_phase6.py        # 38 site cloning tests
python tests/test_e2e_swap.py      # 126 end-to-end tests
```

Tests verify: image swapping (4 photos, filename match), heading/text replacement, SEO meta updates, bulk domain replace, nested Elementor widgets, repeater fields, config validation, dry-run mode, and clone script generation.

## Customer Config

```json
{
  "customer_name": "MediCare Plus",
  "domain": "medicareplus.com",
  "site_settings": {
    "title": "MediCare Plus",
    "description": "Your trusted health partner",
    "logo_file": "assets/medicare/logo.png",
    "favicon_file": "assets/medicare/favicon.png"
  },
  "pages": [
    {
      "page_id": 1210,
      "page_name": "About Us",
      "headings": [{"index": 0, "new_text": "About MediCare Plus"}],
      "texts": [{"index": 0, "new_html": "<p>Leading healthcare provider.</p>"}],
      "images": [{"old_url": "About-US.webp", "new_file": "assets/medicare/about-bg.webp", "match_mode": "filename"}],
      "meta": {"rank_math_title": "About Us - MediCare Plus", "rank_math_description": "Learn about our team."}
    }
  ]
}
```

Full template with all 6 pages: [`configs/customer-template.json`](configs/customer-template.json)

## Project Structure

```
healthcodeanalysis/
├── .github/workflows/
│   ├── ci.yml                 # 4 parallel CI jobs
│   └── deploy.yml             # Manual customer deployment
├── .cpanel.yml                # Auto-deploy PHP plugin on push
├── scripts/                   # 6 Python scripts + 1 PHP plugin
├── tests/                     # 281 tests (unit + e2e)
├── configs/                   # Customer config templates
├── docker/                    # Local dev environment
├── .pre-commit-config.yaml    # Ruff, JSON/YAML check, secret detection
├── pyproject.toml             # Ruff + coverage config
└── requirements.txt           # Dependencies
```

## Tech Stack

**Automation:** Python 3.10+ | Requests | WordPress REST API | cPanel UAPI

**WordPress:** Elementor | Rank Math SEO | ACF | Astra | LiteSpeed Cache

**CI/CD:** GitHub Actions | cPanel Git Deploy (SSH) | Dependabot

**Quality:** Ruff (lint + format + security) | 281 tests | 59% coverage | Pre-commit hooks

## License

[MIT](LICENSE)
