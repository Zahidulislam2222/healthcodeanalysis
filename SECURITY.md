# Security Policy

## Supported versions

| Version | Supported |
|---|---|
| `main` branch and the currently deployed native release | Yes |
| Older commits, retained legacy tooling in its original deployment context | No. Report anyway if it affects `main` |

## Reporting a vulnerability

**Please do not open a public issue for security problems.**

Report privately by either:

- **GitHub private vulnerability reporting:** the "Report a vulnerability" button on the repository's **Security** tab, or
- **Email:** muhammadzahidulislam2222@gmail.com with the subject line `SECURITY: HealthCode Analysis`.

Please include:

- A description of the issue and its impact.
- Steps to reproduce or a proof of concept (minimal and non-destructive).
- Affected URL, file or component.
- Any suggested fix.

## Response targets

| Stage | Target |
|---|---|
| Acknowledgment | Within 48 hours |
| Initial assessment | Within 5 business days |
| Fix for critical issues | Within 7 days of confirmation |
| Fix for other issues | Within 30 days of confirmation |

These are good-faith targets for a single-maintainer project, not a contractual SLA. You will be kept informed of progress.

## Scope

**In scope:**

- `wordpress-native/`: scoped plugin, gateway templates, build/import scripts and policy data.
- `frontend/`: design source scripts and templates.
- `workers/askme/`: retained Cloudflare Worker.
- `scripts/`: automation toolkit and PHP plugins (`healthcode-api-bridge.php`, `hc-auto-activate.php`, the design system).
- `deploy/`, `docker/` and `.github/workflows/`.
- The live demonstration site, **within the safe-harbor rules below**.

**Out of scope:**

- Vulnerabilities in WordPress core, Elementor or other third-party plugins. Report those upstream (for example through the WordPress or plugin vendor's security programme), unless our configuration makes them exploitable.
- Denial-of-service or load testing, spam, social engineering, and physical attacks.
- Missing security headers without a demonstrated impact, and self-XSS.
- Findings from automated scanners without a working proof.

## Safe harbor

We will not pursue legal action against good-faith research that:

- Avoids privacy violations, data destruction and service degradation.
- Does not access, modify or keep data beyond what is needed to demonstrate the issue.
- Does not brute-force logins or run high-volume automated scanning against the live site.
- Gives us reasonable time to fix the issue before public disclosure.

## Disclosure

We follow coordinated disclosure. After a fix is released, we will credit you in the release notes or fix commit if you wish.

## Security documentation

- [Threat model](docs/THREAT-MODEL.md): controls and residual risks.
- [Incident response](docs/INCIDENT-RESPONSE.md): how incidents and breaches are handled.
- [Architecture](docs/ARCHITECTURE.md): trust boundaries.
