# Native Elementor implementation

This is the deployed, editable WordPress implementation of the preserved Neural Frontier design. The previous static release is retained as a visual reference and rollback option. Recorded public behavior, security, editor and deployment-parity checks passed; owner visual acceptance and sustained capacity/uptime measurements remain outstanding. See [acceptance criteria](ACCEPTANCE.md), [US/EU research](docs/US-EU-RESEARCH.md) and the [capacity register](../docs/SCALABILITY-AND-RELIABILITY.md). The current evidence and remaining gates are in the [verification record](docs/VERIFICATION.md).

## Editing and preservation

Layouts use Elementor Free containers, headings, text, images, buttons and video. The free Ultimate Addons header/footer builder owns the header and footer templates. Twenty-eight native library-filter widgets provide search/category controls; six shortcodes provide the browser-only educational tools. No HTML widgets are used. Original frontend source remains under `frontend/`; the private recovery snapshot retains the approved source and rendered design.

Representative heading and button edits through visible Elementor controls, and an image edit through Elementor's native settings command, have been saved, checked over public HTTP, and restored. The custom behavior attributes survived editor reload. Typography, visual matching and actual interaction checks are separate gates.

`build_native.py` is an initial migration compiler. Re-importing replaces local Elementor content. Once an editor changes a page, preserve/export those changes before any import. A source rebuild must never silently overwrite editorial work. Local database/content snapshots and a drift check precede deployment.

## Local configuration and import

Use `.env.example` as the environment contract and keep actual credentials in ignored `.env` and the root recovery file. The typed loader is `scripts/native_settings.py`. Pin the resolved container image digests for a release; examples are not verification of a later image.

After an approved build, use the cache-safe local importer rather than calling the PHP import directly:

```bash
python wordpress-native/scripts/build_native.py
python wordpress-native/scripts/import_local.py \
  --docker docker \
  --environment wordpress-native/.env \
  --compose wordpress-native/compose.yaml \
  --project healthcode-elementor \
  --timeout 240 \
  --replace-native-layouts
```

Pass the installed Docker executable path when it is not on PATH. This command rejects nonlocal site URLs and remote Docker contexts/environment overrides, pins the verified local socket, imports the approved native layout, then restarts the local gateway to invalidate HTML cached against old Elementor CSS. If either step fails, it reports failure. Do not publish while markup and generated CSS belong to different imports.

## Configuration ownership

- Environment and private access: typed native environment and `.env.example`.
- Public notices, feature flags, editorial eligibility and response policy: `data/public-notices.json` and `data/publishing-policy.json`.
- Gateway limits, timeouts and trusted proxy networks: `data/delivery.json`.
- Native SVG contextual colors: `data/icon-palette.json`, reflecting the approved frontend color system. Preserve rule order: outlined buttons precede filled buttons.
- Capacity assumptions: `data/capacity-plan.json`; its generated output is arithmetic, never a benchmark.
- Source content and design: the existing `frontend/` data, templates, styles and assets.

The publisher excludes unverified demonstration articles from indexing, emits truthful WebSite/WebPage metadata, and does not fabricate author credentials or review ratings. Future analytics, advertising, affiliates, newsletters, public accounts and health-data collection remain disabled. Operator-specific legal and privacy information must be completed for a real client.

## Evidence and limitations

Local and public evidence includes the representative editor round trip, 13 interaction scenarios, 11 motion/accessibility states, 21 HTTP security checks and 11 native/configuration regression tests. Full separate-host SQL/content restoration passed before native production activation. Final 141-file and project-Caddy SHA256 parity passed. A 28-request public proxy test verified real-client rate limiting despite forged application headers. See docs/VERIFICATION.md for scope and exceptions.

Two Factor 0.16.0 is installed locally and on the verified public release. Password-only access is withheld; invalid TOTP is rejected; valid TOTP opens the dashboard and Elementor. Recovery values are private. Do not disable MFA for convenience when updating browser tests.

The implementation includes an anonymous NGINX HTML cache, bounded cache storage, cache locking, private-request bypass and hash-based CSP. It has not demonstrated 10k–1M concurrent users or a 99% observation window. Follow the capability register and qualification gates before making those claims.

## Security pipeline activation

The repository contains a separate native security workflow covering the native build, configuration/behavior contracts, lint, types, Bandit, Semgrep, PHP syntax and Gitleaks. It is manual and guarded by `HEALTHCODE_ACTIONS_ENABLED`; it has not been activated or billed by this work. Review runner availability, action licensing and account billing before enabling it. There is no paid AI-review job. Local results and the machine's mandatory edit scan remain separate evidence; a workflow definition is not a successful CI run.

## Related documentation

- [Architecture](../docs/ARCHITECTURE.md) · [Threat model](../docs/THREAT-MODEL.md) · [Roadmap](../docs/ROADMAP.md)
- [Operations runbook](../docs/OPERATIONS-RUNBOOK.md) · [Backup and disaster recovery](../docs/BACKUP-AND-DISASTER-RECOVERY.md)
- [Legal and compliance pack](../docs/legal/README.md): the published notices are owned by `data/public-notices.json`
