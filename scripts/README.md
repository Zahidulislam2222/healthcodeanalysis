# Scripts

This folder mixes **current** build tooling for the design source with the **retained** WordPress automation toolkit from the project's first phase.

## Current tooling

| Script | Purpose |
|---|---|
| `build_frontend.py` | Builds the Neural Frontier design source (63 routes + a real 404) into the ignored `frontend-preview/` |
| `preview_frontend.py` | Serves the preview locally (host/port from `frontend/site.config.json`) |
| `frontend_settings.py` | Typed configuration loader for the frontend build |
| `import_frontend_content.py` | Refreshes `frontend/data/library.json` from a WordPress export |
| `generate_frontend_media.py` | Offline, one-time media generation (needs a private API key in `.env`; **paid**) |
| `export_static_site.py` | Deterministic WordPress → static export plus a public content index |
| `extract_wpress_assets.py`, `restore_wpress_wp_content.py`, `repair_pages_export.py` | Import and repair helpers for the original `.wpress` archive |

The native WordPress build lives in [`../wordpress-native/scripts/`](../wordpress-native/).

## Retained automation toolkit

**Status: Retained.** It was built for the original client brief: clone an Elementor template site per customer on cPanel, and swap photos, text and SEO metadata with one command. It is **not** part of the current public runtime. It needs WordPress application passwords, which the native runtime deliberately disables, so reusing it is a separate activation with its own review.

```bash
python scripts/deploy_customer.py configs/customer-template.json --dry-run   # preview every change
python scripts/deploy_customer.py configs/customer-abc.json                  # apply
python scripts/clone_site.py --source <template-domain> --target <new-domain> --generate-script
```

| Module | Responsibility |
|---|---|
| `config_validator.py` | Validates the customer JSON before any mutation |
| `wp_client.py` | Central WordPress REST client (auth, retries, dry-run) |
| `elementor_parser.py` | Parses and modifies the Elementor JSON tree; fails on ambiguous matches |
| `content_swapper.py` | Orchestrates image upload/swap, heading/text replacement and Rank Math SEO fields |
| `deploy_customer.py` | One-command pipeline: validate → plan → mutate → read back |
| `clone_site.py` | cPanel UAPI: databases, users and migration scripts |
| `healthcode-api-bridge.php` | WordPress plugin exposing Elementor data over REST: header-only API key, per-IP rate limits (60 GET / 20 POST per minute), path whitelist, prepared SQL |
| `hc-auto-activate.php` | mu-plugin: security headers and design-system loader |
| `healthcode-design-system/` | Dark glassmorphism theme plugin with vanilla JS animations |
| `deploy.sh`, `publish-static-site.ps1`, `export-healthcode-pages.ps1` | Historical deployment/publish wrappers |

Customer config format: [`configs/customer-template.json`](../configs/customer-template.json). Tests: 281 offline checks in [`tests/`](../tests/README.md).

## Known issues

- `publish-static-site.ps1` and `export-healthcode-pages.ps1` contain machine-specific absolute paths. They should read these from configuration before anyone else uses them (tracked in the [roadmap](../docs/ROADMAP.md)).
- Whole-repository Ruff reports eight findings in files unchanged by the native release (three of them in `export_static_site.py`).
