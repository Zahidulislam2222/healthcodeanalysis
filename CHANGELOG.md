# Changelog

All notable changes to this project are documented here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Dates are ISO 8601. Git tags have not been used before; releases are identified by date.

## [Unreleased]

### Added
- Public documentation set: architecture, roadmap (10k → 1M readers, 99% SLO), threat model, incident response, backup and disaster recovery, operations runbook, development guide and a documentation index (`docs/`).
- Legal and compliance pack (`docs/legal/`): compliance register (EU, UK, US, Bangladesh), medical disclaimer, cookie and storage inventory, service-provider list, AI transparency, accessibility statement, editorial and copyright policy, and privacy/terms launch templates.
- Community files: `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SUPPORT.md`, `THIRD-PARTY-NOTICES.md`, issue and pull request templates, `CODEOWNERS`.
- READMEs for `workers/askme`, `scripts`, `tests`, `docker` and `deploy/shared-vps`.

### Changed
- README rewritten around the current native Elementor release; historical automation details moved to `scripts/README.md`.
- `SECURITY.md` scope updated to the native runtime, with a safe-harbor statement.
- Scalability document extended with a 1M-reader reference architecture and an error-budget policy.
- GitHub Actions: `actions/checkout` v6 → v7 and `actions/setup-node` v4 → v6 across all workflows (reviewed release notes; workflows remain manual and guarded). Supersedes Dependabot pull requests #3 and #4. setup-node v7 exists; v6 was kept to match the reviewed Dependabot change, and v7 is left for a separate update once CI is active.
- Fixed missing-space typos in the native README, verification, acceptance and scalability documents.
- `requirements-dev.txt` now includes mypy and bandit so the documented gates run from a clean install.

### Security
- `out.txt` (local scratch output) is now git-ignored to prevent committing private correspondence.

## 2026-09-14: Native Elementor release

### Added
- Native WordPress + Elementor Free implementation of the Neural Frontier design: 66 layouts, zero HTML widgets, editable header and footer.
- Scoped plugin: library filters, six educational-tool shortcodes, publication metadata, security headers with a hash-based CSP.
- NGINX gateway with an anonymous HTML cache, private bypass and a login rate limit.
- Capacity model, local smoke tool, US/EU research, verification record and public technical overview.
- Manual, guarded native security workflow.

### Security
- MFA (TOTP) for administrators; XML-RPC, application passwords, author enumeration and file editing disabled.

## 2026-07-12: Domain decommission

### Changed
- Retired the expiring custom domain and the cPanel hosting path; disabled automation that depended on dead infrastructure.
- Static Cloudflare Pages publication and the AskMe Worker with a bundled content index, independent of WordPress uptime.

## 2026-07-10: Admin demo DNS
### Added
- Optional workflow for demo tunnel DNS (now manual and disabled).

## 2026-05-09
### Security
- `.gitignore` hardened for credential files and CSV exports.

## 2026-04-10: Design system, security hardening, AskMe
### Added
- Dark glassmorphism design-system plugin (vanilla JS animations; GSAP removed).
- Security hardening: headers in an mu-plugin, REST rate limiting, path whitelist, header-only API key.
- AskMe Cloudflare Worker chatbot with Dialogflow ES for greetings.

## 2026-04-09: Initial release
### Added
- WordPress Elementor automation toolkit: customer config validation, Elementor parser, content/image/SEO swap, cPanel cloning, dry-run mode, and 281 offline checks.
