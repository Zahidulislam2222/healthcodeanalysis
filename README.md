<p align="center">
  <h1 align="center">HealthCode Analysis</h1>
  <p align="center">
    Automate WordPress Elementor site cloning and content replacement via REST API.
    <br />
    One command per customer. Clone, swap photos, text, and SEO metas — done.
  </p>
</p>

<p align="center">
  <a href="https://github.com/Zahidulislam2222/healthcodeanalysis/actions/workflows/ci.yml">
    <img src="https://img.shields.io/github/actions/workflow/status/Zahidulislam2222/healthcodeanalysis/ci.yml?branch=main&label=CI&style=flat-square" alt="CI">
  </a>
  <img src="https://img.shields.io/badge/coverage-59%25-yellow?style=flat-square" alt="Coverage">
  <img src="https://img.shields.io/badge/tests-285%20passing-brightgreen?style=flat-square" alt="Tests">
  <img src="https://img.shields.io/badge/python-3.10+-blue?style=flat-square" alt="Python">
  <a href="https://docs.astral.sh/ruff/">
    <img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json&style=flat-square" alt="Ruff">
  </a>
  <img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="License">
</p>

---

<details>
<summary><strong>Table of Contents</strong></summary>

- [About](#about)
- [Features](#features)
- [How It Works](#how-it-works)
- [Quick Start](#quick-start)
- [Usage](#usage)
- [Architecture](#architecture)
- [Testing](#testing)
- [CI/CD Pipeline](#cicd-pipeline)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [License](#license)

</details>

---

## About

A freelance client needs to create websites for multiple customers using a single WordPress Elementor template. Each customer gets their own domain on cPanel with unique photos, text, and SEO metadata.

**The problem:** Manually cloning a WordPress site and editing 6 pages x 4 photos + text + metas per customer is slow, error-prone, and doesn't scale.

**The solution:** This tool automates the entire pipeline — clone the template site via cPanel API, then swap all content programmatically through the WordPress REST API. What took hours now takes one command.

## Features

- **One command deployment** — `python deploy_customer.py config.json` handles everything
- **Elementor JSON manipulation** — Parse, modify, and save Elementor page builder data via REST API
- **Image swap** — Upload new photos and replace URLs in Elementor JSON (exact or filename matching)
- **Text swap** — Replace headings and text-editor widgets by index or widget ID
- **SEO meta swap** — Update Rank Math title, description, keywords, and Open Graph tags
- **Site identity** — Update site title, tagline, logo, and favicon
- **cPanel site cloning** — Create databases, users, and generate full migration scripts
- **Dry-run mode** — Preview all changes without touching the live site
- **Idempotent** — Safe to re-run; same input always produces the same result
- **285 tests** — Unit tests, integration tests, and end-to-end swap verification

## How It Works

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Customer JSON   │────>│  deploy_customer  │────>│  WordPress Site  │
│  (config file)   │     │    .py            │     │  (REST API)      │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                              │
                    ┌─────────┼─────────┐
                    │         │         │
               ┌────▼───┐ ┌──▼───┐ ┌───▼────┐
               │ Images  │ │ Text │ │  SEO   │
               │ Swap    │ │ Swap │ │  Meta  │
               └────┬───┘ └──┬───┘ └───┬────┘
                    │         │         │
               ┌────▼─────────▼─────────▼────┐
               │   Elementor JSON Parser      │
               │   (read → modify → save)     │
               └─────────────────────────────┘
```

**Flow:**
1. Read customer config JSON (pages, photos, text, metas)
2. For each page: fetch Elementor data → swap images → swap headings → swap text → update SEO
3. Save modified Elementor data back via REST API
4. Update site identity (title, tagline, logo, favicon)
5. Flush Elementor + LiteSpeed cache

## Quick Start

### Prerequisites

- Python 3.10+
- WordPress site with [Application Passwords](https://developer.wordpress.org/rest-api/using-the-rest-api/authentication/) enabled
- The `healthcode-api-bridge.php` plugin installed on the target site

### Installation

```bash
git clone https://github.com/Zahidulislam2222/healthcodeanalysis.git
cd healthcodeanalysis
pip install -r requirements.txt
```

### Setup

```bash
cp .env.sample .env
# Edit .env with your WordPress credentials:
#   WP_SITE_URL=https://your-site.com
#   WP_USERNAME=admin
#   WP_APP_PASSWORD=xxxx xxxx xxxx xxxx xxxx xxxx
#   HC_API_KEY=your-api-key
```

## Usage

### Deploy content to a customer site

```bash
# Preview changes (no modifications made)
python scripts/deploy_customer.py configs/customer-template.json --dry-run

# Deploy for real
python scripts/deploy_customer.py configs/customer-template.json

# Deploy a single page only
python scripts/deploy_customer.py configs/customer-template.json --page-id 1210

# Skip images or SEO
python scripts/deploy_customer.py configs/customer-template.json --skip-images --skip-seo
```

### Clone site to a new domain

```bash
# Generate a bash script for server-side cloning
python scripts/clone_site.py \
  --source healthcodeanalysis.com \
  --target newcustomer.com \
  --generate-script --output clone.sh

# Preview cPanel operations
python scripts/clone_site.py \
  --source healthcodeanalysis.com \
  --target newcustomer.com \
  --dry-run
```

### Validate a customer config

```bash
python scripts/config_validator.py configs/customer-template.json
```

## Architecture

| Script | Purpose | Key Operations |
|--------|---------|----------------|
| `deploy_customer.py` | Master orchestrator | Reads config, connects to WP, runs all swaps |
| `content_swapper.py` | Content swap engine | Image upload/replace, heading/text swap, SEO meta update |
| `elementor_parser.py` | Elementor JSON parser | Find widgets, replace images/text, bulk domain replace |
| `wp_client.py` | WordPress REST API client | Auth, CRUD pages, upload media, read/write Elementor data |
| `config_validator.py` | Config validation | Validates customer JSON against required schema |
| `clone_site.py` | cPanel site cloner | Create DB, generate migration scripts |
| `healthcode-api-bridge.php` | WordPress plugin | Exposes Elementor data, Rank Math metas, cache flush via REST |

### Site Map

| Page | ID | Images | Key Content |
|------|----|--------|-------------|
| Home | 2471 | 0 (CSS) | Hero, counters, section links |
| About Us | 1210 | 6 | Doctor photo, testimonials, form |
| Contact | 1212 | 1 | Map, form, social icons |
| Repository | 1233 | 11 | Blog grid, promo box |
| Affiliate Disclosure | 3017 | 1 | Legal page |
| Privacy Policy | 3 | 0 | Legal page |

## Testing

```bash
# Run all 285 tests
python tests/test_phase1.py        # 75 unit tests
python tests/test_phase2_4.py      # 46 content swap tests
python tests/test_phase6.py        # 38 site cloning tests
python tests/test_e2e_swap.py      # 126 end-to-end swap tests

# Run with coverage
pip install coverage
coverage run tests/test_phase1.py
coverage run -a tests/test_phase2_4.py
coverage run -a tests/test_phase6.py
coverage run -a tests/test_e2e_swap.py
coverage report

# Lint
pip install ruff
ruff check scripts/ tests/
ruff format --check scripts/ tests/
```

## CI/CD Pipeline

### CI — Continuous Integration (automatic on every push)

Every push and pull request triggers **4 parallel CI jobs** on GitHub Actions:

| Job | What It Does | Time |
|-----|-------------|------|
| **Lint & Security** | Ruff lint + format check + Bandit security scan + PHP syntax | ~15s |
| **Tests** | Runs all 285 tests across 4 test suites | ~30s |
| **Coverage** | Measures code coverage, enforces minimum threshold | ~30s |
| **Validate** | Validates customer config JSON schema and syntax | ~10s |

### CD — Continuous Deployment

**Plugin auto-deploy:** On every push to `main`, the PHP API bridge plugin is automatically deployed to the live cPanel server via `.cpanel.yml`.

**Customer content deploy:** Triggered manually from GitHub Actions with a dry-run + approval gate:

```
GitHub → Actions → "Deploy Customer" → Run workflow
  │
  ├── Step 1: Validate config schema
  ├── Step 2: Dry-run (preview changes, no modifications)
  ├── Step 3: Manual approval (you review the dry-run output)
  └── Step 4: Live deployment + site verification
```

Required GitHub Secrets: `WP_USERNAME`, `WP_APP_PASSWORD`, `HC_API_KEY`

### Additional Quality Gates

- **Pre-commit hooks** — Ruff lint/format, JSON/YAML validation, secret detection
- **Dependabot** — Automated dependency updates (weekly)
- **cPanel Git deploy** — PHP plugin auto-deploys on push to main

## Project Structure

```
healthcodeanalysis/
├── .github/
│   ├── workflows/
│   │   ├── ci.yml                # CI: lint, test, coverage, validate (4 parallel jobs)
│   │   └── deploy.yml            # CD: manual-trigger customer deployment
│   └── dependabot.yml            # Automated dependency updates
├── .cpanel.yml                   # Auto-deploy PHP plugin to cPanel on push
├── scripts/
│   ├── wp_client.py              # WordPress REST API client
│   ├── elementor_parser.py       # Elementor JSON parser/modifier
│   ├── config_validator.py       # Customer config validation
│   ├── content_swapper.py        # Content swap orchestrator
│   ├── deploy_customer.py        # Master deploy script
│   ├── clone_site.py             # cPanel site cloning
│   └── healthcode-api-bridge.php # WordPress API bridge plugin
├── configs/
│   └── customer-template.json    # Customer config template
├── tests/
│   ├── test_phase1.py            # 75 unit tests
│   ├── test_phase2_4.py          # 46 content swap tests
│   ├── test_phase6.py            # 38 site cloning tests
│   └── test_e2e_swap.py          # 126 end-to-end tests
├── docker/
│   ├── docker-compose.yml        # Local dev environment
│   └── setup.sh                  # WordPress auto-setup
├── .pre-commit-config.yaml       # Pre-commit hooks
├── pyproject.toml                # Ruff config, project metadata
├── requirements.txt              # Production dependencies
├── requirements-dev.txt          # Development dependencies
└── .env.sample                   # Environment template
```

## Configuration

Customer configs are JSON files that define what to swap per page:

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
      "headings": [
        {"index": 0, "new_text": "About MediCare Plus"}
      ],
      "texts": [
        {"index": 0, "new_html": "<p>Leading healthcare provider.</p>"}
      ],
      "images": [
        {
          "old_url": "About-US.webp",
          "new_file": "assets/medicare/about-bg.webp",
          "match_mode": "filename"
        }
      ],
      "meta": {
        "rank_math_title": "About Us - MediCare Plus",
        "rank_math_description": "Learn about our team."
      }
    }
  ]
}
```

See `configs/customer-template.json` for the full template with all 6 pages.

## License

MIT License. See [LICENSE](LICENSE) for details.
