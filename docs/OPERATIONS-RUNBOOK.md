# Operations runbook

Routine procedures for the live native publication. Host names, credentials, key paths and provider account details are **deliberately excluded** from this public file; operators keep them in the private recovery record.

## 1. Golden rules

1. **Local first.** Every change is made and verified locally, then deployed. Never hand-edit production.
2. **Detect drift before editing.** Hash the live versions of files you will touch. If live is ahead of local, pull it and reconcile first.
3. **Prove parity after deploying.** Re-hash every deployed file and confirm local equals live.
4. **Never re-import generated layouts over newer editor work.** Export and reconcile first.
5. **Backups before mutation:** before deploys, plugin updates and imports.

## 2. Standard deployment

| Step | Action | Evidence to keep |
|---|---|---|
| 1 | Write acceptance criteria for the change. | Pull request description. |
| 2 | Drift check: compare the live files and editable content with local. | Hash list / diff. |
| 3 | Build locally: `python wordpress-native/scripts/build_native.py`. | Build output (page count, zero HTML widgets). |
| 4 | Run the gates (see [DEVELOPMENT.md](DEVELOPMENT.md#quality-gates)). | Test/lint/type/security output. |
| 5 | Import into the **local** stack with `wordpress-native/scripts/import_local.py` (refuses remote Docker endpoints). | Import log. |
| 6 | Browser and HTTP checks locally. | Scenario results. |
| 7 | Back up the production database and content. | Backup checksum. |
| 8 | Restore into an isolated runtime on the server and verify it. | Restored checks. |
| 9 | Activate project-scoped routing; activation auto-restores the previous config on failure. | Activation log. |
| 10 | Invalidate the gateway cache **together with** Elementor CSS regeneration. | Cache HIT after warmup. |
| 11 | Public checks: browser scenarios, 21 HTTP/security checks, MFA login, editor opens. | Results. |
| 12 | SHA256 parity of all release files and the routing file. | Parity report. |

## 3. Rollback

| Situation | Action |
|---|---|
| Routing activation fails | Automatic: the previous project routing file is restored. |
| New release misbehaves after activation | Re-activate the previous release's routing; the retained static release is the last-resort visual fallback. |
| Content damaged | Restore the pre-deploy database backup into isolation, verify it, then switch ([BACKUP-AND-DISASTER-RECOVERY.md](BACKUP-AND-DISASTER-RECOVERY.md)). |

Rolling back routing and recovering WordPress content are **separate** operations. Decide which one you need.

## 4. Cache operations

- Public cache lifetime: 30 s plus 30 s stale-while-revalidate (`wordpress-native/data/publishing-policy.json`).
- Gateway cache settings: `wordpress-native/data/delivery.json`.
- **Deployment parameter:** the committed `trusted_proxy_cidrs` is empty, which suits local builds. Production must supply the trusted host-gateway network at render time, or the login limiter keys on the proxy's address instead of the real client. That value is kept in the private deployment record; moving it into the typed environment and `.env.example` is tracked in the roadmap.
- After any layout import or CSS-affecting change: regenerate Elementor CSS and restart/invalidate the gateway cache in the same maintenance window. Mismatched markup and CSS show up as a broken layout.
- Verify with response headers: an anonymous second request should be a HIT; cookie, query-string or authorization requests should be BYPASS.

## 5. WordPress maintenance

| Task | Frequency | Notes |
|---|---|---|
| Minor core updates | Automatic | Verify the site afterwards. |
| Major core / plugin / theme updates | Monthly or on security advisories | Back up; update locally; run the editor round trip, browser scenarios and MFA login; then deploy. Use official packages only. |
| PHP / database image updates | Quarterly | Pin image digests; re-run the full checks. |
| Review administrator accounts | Quarterly | Remove unused accounts; confirm MFA on all privileged users. |
| Core checksum verification | Monthly | `wp core verify-checksums` through the tools-profile CLI container. |

## 6. Secret rotation

| Trigger | Action |
|---|---|
| Suspected exposure | Rotate immediately; revoke sessions; review logs (SEV-1). |
| Staff/contractor offboarding | Rotate all credentials that person could access. |
| Routine | Annually for passwords, API tokens and database users. |

After rotation, update the environment/secret store, redeploy, verify, and record the rotation date (not the value) in the private record.

## 7. Monitoring (target state, roadmap Phase 1)

| Signal | Alert condition |
|---|---|
| External probe success | 3 consecutive failures from 2+ locations → page |
| Error-budget burn | > 10% of the monthly budget in 24 h → ticket |
| TLS certificate expiry | < 14 days → ticket |
| Origin CPU / memory | > 85% for 10 min → ticket |
| Login 429 rate | Spike above baseline → review |
| Disk usage | > 80% → ticket |

## 8. Retained components

- **AskMe Worker:** not used by the native site, but still publicly reachable through the legacy `healthcodeanalysis.pages.dev` snapshot (`/askme-proxy`). Decide whether to decommission it (and the snapshot) or harden it. Before keeping it: restrict CORS, add rate limiting, fix the test harness, regenerate the content index. Secrets are set with `npx wrangler secret put`.
- **Automation toolkit / legacy REST bridge:** requires application passwords, which the native runtime deliberately disables. Treat any reuse as a new activation with its own review.
- **GitHub Actions:** manual and guarded by the `HEALTHCODE_ACTIONS_ENABLED` repository variable. Review billing before enabling.
