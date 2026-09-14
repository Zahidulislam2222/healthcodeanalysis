# Native Elementor migration acceptance

The owner requires the approved design, including the neural brain and slower balanced hero, reproduced almost exactly in Elementor Free. These criteria were established before migration. The native release is now deployed; the preserved static release remains the visual reference and rollback option. Recorded verification and remaining owner acceptance are listed in `docs/VERIFICATION.md`.

1. All63 routes preserved in WordPress; layouts stored as real Elementor containers and free heading/text/image/button/video widgets. No whole-page HTML or iframe workaround.
2. Header/footer are editable Elementor templates managed by the current free Ultimate Addons header/footer builder; no Elementor Pro dependency.
3. Desktop1903×905/1440×1000, laptop1280×720 and mobile390/320 side-by-side screenshot comparisons; fix visual differences in hierarchy, spacing, media, cards, controls and footer.
4. Real Elementor editor opens and saves representative heading, button and image edits; revert the test edits and verify frontend output. Inventory widget types and explicitly account for every shortcode/HTML exception.
5. Search, saved list, six tools, video seeking/pause, responsive navigation, keyboard use, failed media and reduced motion work in WordPress. Custom behavior belongs in a small plugin; layout remains native widgets.
6. Latest stable PHP/core/plugins verified from official sources; no prerelease or nulled paid packages. ACF only where content editing benefits.
7. Isolated local build first. Snapshot/database/uploads recovery, persistent-volume recreation and tested off-server restore before replacing the public static reference. Loopback server binding and TLS/DNS remain scoped.
8. Update checkpoint/dossier/credentials and shared registry as state changes; report tests/types/lint/security/build/native validators, real flows, review, and local/live parity. Visual acceptance is the owner's decision; do not invent a100% match.

## Search, security and legal extension

9. Research US/EU applicability from primary sources, inventory actual data flows, record conditional obligations and missing operator details in a cited report. Public notices must match verified behavior; no invented compliance guarantees.
10. Unique metadata/canonical/social tags, truthful JSON-LD, sitemap/robots and redirects; production indexing restricted to eligible verified content. No fabricated reviews, authors, credentials, dates or AI-ranking guarantees.
11. Harden login/admin, disable unused attack surfaces, protect secrets/uploads, apply compatible response headers and bounded resource limits; verify editor, tools and crawler access still work. Verify upgrades against official inventories.
12. Exercise privacy/storage, keyboard access, form boundaries, security denials, crawl routes, backup/restore and local/live parity; fresh-context review before completion. Keep original visual reference intact.

## Capacity and availability extension

13. Publish a client/developer-facing capability register distinguishing IMPLEMENTED, VERIFIED, PLANNED and NOT MEASURED. 10k–1M concurrent users and 99% availability are targets, not current capacity or achieved uptime.
14. Provide a configurable capacity model, staged architecture, measurable SLI/SLO definitions, safe local-only smoke tooling, and evidence required before making scale claims. Account separately for cached readers, origin requests, media bandwidth, authenticated writes and failure scenarios.
15. No paid resources, traffic-generating cloud test services or large live load tests are provisioned or executed. Any future capacity claim requires representative sustained load, recovery/failover evidence and provider quota/cost review.

## Review corrections

16. The local importer rejects remote Docker endpoints from environment variables or the active context before any Compose mutation, and pins a verified local socket for all subsequent commands.
17. Social metadata preserves valid same-origin absolute ACF image URLs and imported relative image paths; invalid or external URLs use the configured fallback. Verify saved metadata over HTTP and restore test edits.
18. Database readiness must require an authenticated TCP query against the configured database; the image's temporary socket-only initialization server must never satisfy readiness. Verify normal health and rejection of invalid credentials before resuming restore.
19. Transformed WordPress SQL exports must restore fully into an isolated schema using connection-scoped compatibility settings, preserve valid Elementor JSON, and leave global SQL modes unchanged.

20. Public cutover preserves original /assets/* media, validates only the project Caddy replacement, proves production canonical URL and native content, and restores the prior project configuration automatically if activation fails.
