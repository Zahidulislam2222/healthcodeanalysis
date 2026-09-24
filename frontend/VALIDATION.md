# Local preview verification — 2026-09-14

This report covers the revised Neural Frontier local frontend. The earlier Evidence Atlas visual direction was rejected. It is not a production-readiness or deployment claim.

## Acceptance criteria

The ten local-preview criteria in `DESIGN.md` were implemented and exercised: publication identity; desktop/mobile artwork and layouts; preserved routes and 404; real search/filtering; local reading list; six working educational/creative tools; navigation/dialog/assets; optional motion; explicit configuration ownership; and reported verification/review.

## Gates

| Gate | Result |
|---|---|
| Legacy offline tests | 293 passed: Phase 1 71, Phase 2–4 46, Phase 6 38, content-swap 126, exporter 11, admin headers 1 |
| Frontend Python regression suite | 7 passed: routes/assets, escaped content, path safety, Unicode, obsolete-output cleanup, and client service boundary |
| JavaScript regression suite | 5 passed: BMI, CKD-EPI 2021 examples, score boundaries, PICO, search |
| Frontend lint/format | Passed for the four new build/server/import/settings modules and Python tests; artwork script also passed lint |
| Types/syntax | Mypy passed for the four new Python modules; browser JavaScript syntax passed Node checking |
| Security | Bandit reported zero findings in the new Python runtime scripts; artwork scan passed. Gitleaks reported zero findings in the tracked/new-source scan and Git history |
| Build | 63 routes and a separate 404 page generated successfully |
| Browser behavior | 13 scenarios passed, including all six tools and a real WebP download |
| Fresh-context review | Three findings corrected and re-reviewed: stale build output, configuration limits, and menu focus. No remaining blocker in those fixes |
| Whole-repository lint | Eight findings remain in four unchanged legacy scripts. This gate is not green |
| Docker-dependent requirements test | Could not connect to the existing local WordPress service. Not a passing integration gate |
| Cloud deployment / live runtime integration | Not performed; the task is local review |

## Real browser flows

Chromium exercised all 63 routes over HTTP, the Unicode route, and an unknown route returning 404. Search returned relevant results and an empty state. Dialog Escape returned focus to its opener. Saving, reloading, removing, and blocked local storage were checked. Archive search and category filtering were checked. All six tool forms produced expected output, including downloading a generated WebP. Mobile menu keyboard focus and reduced motion were checked. No JavaScript errors or external network requests occurred in those exercised flows.

Desktop and mobile screenshots were inspected. The five captured page views had no missing images, JavaScript exceptions, or horizontal overflow. A 320-pixel crawl covered every route; a long URL in one article required wrapping and was corrected.

Screenshots, repeatable manual browser scripts, and detailed gate logs remain in the project's ignored `debug/frontend-tests/` directory. The reviewer's independent test invocation lacked Pillow in its WSL interpreter; the passing test results above were obtained using the installed Windows Python environment.

## Configuration and secret audit

- Real secrets found in scanned source/history: **no**. Private credentials, environment, dossier, and memory files were verified ignored and absent from tracked files/history. An OpenRouter key was added only to ignored private environment/recovery files.
- Changeable frontend values moved to configuration/data: preview host/port and paths, search/storage/image/text limits, related-story count, calculator coefficients and bounds, validation copy, tool guides, navigation, and curation.
- Intentionally retained constants: HTML/SVG syntax, DOM semantics, mathematical operations, and component presentation rules. These are implementation or visual-design definitions rather than deployment/provider settings.
- The offline media runner reads its provider/model/endpoints/prices/timeouts/prompts from `media.config.json` and its key from the configured environment/private file. The shipped browser has no provider credentials or paid API integration. `.env.example` documents the existing automation variable names with safe values; the legacy automation's scattered settings were inventoried, not comprehensively refactored by this frontend task.

## Limits

Imported articles and reviews are demonstration material, not independently fact-checked medical or purchasing advice. Local calculation checks do not constitute clinical validation. Reading lists are browser-local. Search is local collection retrieval, not a remote generative assistant. Physical-device performance and cross-browser certification were not performed. The existing publisher and live site were not changed.

## Neural Frontier revision verification

Revision criteria: **8/8 implemented and exercised** from `artwork/REVISION-BRIEF.md`; this is a local technical verification, not owner aesthetic acceptance.

- Paid image: GPT Image 2.5 Sunburst, $0.033345. Paid video: Seedance 2.5, $1.858590. Total **$1.891935**, one image and one video, no paid retries. Original returned ledger retained privately.
- Opening, close-up, ending and reverse browser frames inspected. Optimized silent H.264 film is approximately 3.6 MB, 1280×720, eight seconds. Mobile does not request it.
- **11 film/accessibility states passed**, including decoded forward/reverse frames, pause/resume, review-card keyboard visibility, live reduced motion, and failed-media fallback.
- **5 real HTTP range checks passed**; six additional independent in-memory cases passed review. The initial local server lacked Range support and prevented seeking; single-byte-range support fixed the real flow. Protocol reference: [MDN HTTP range requests](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Range_requests).
- **13 application scenarios passed** and all **63 routes passed the 320px overflow crawl**. Final five desktop/mobile/content captures returned HTTP 200 with zero broken images, JS errors or horizontal overflow.
- Offline suites rerun: 293 legacy checks and 7 frontend Python tests passed; 5 JavaScript tests passed. Build produced 63 routes plus 404. Scoped lint/format, Bandit and final Mypy across five Python modules passed. Final Gitleaks public-source scan found no leaks.
- Fresh-context review found no blocking defect in the revision. Previously conditional pause/resume and focus checks subsequently passed. A faint midpoint caption during its crossfade remains a visual refinement; owner design acceptance is pending.
- Existing whole-repository lint and unavailable Docker integration exceptions in the gate table remain unresolved. No cloud deployment occurred.

Configuration audit: provider settings and maintained media prompts are centralized; secrets are excluded from public source. Byte-range syntax/status codes and bounded I/O chunk size are fixed HTTP/implementation constants. Existing client configuration regression checks remain passing. Physical-device and non-Chromium checks remain unperformed.

## Hero refinement after owner feedback

The owner likes the brain artwork and accepts the broader direction; the hero required further work. This revision preserves the paid assets and changes only homepage hero composition/copy and caption timing.

Five acceptance criteria in the brief were exercised: 6 viewport checks (320, 390, 768, 900, 1280 and 1440px), headline/action separation, a shorter 175svh sequence, preserved functionality/fallbacks, and local-only scope. The first 320px capture exposed a wrapped secondary action touching the artwork; the corrected final capture separates them. Short laptop screens use a smaller sculpture and separate controls. The caption enters after the close-up.

| Gate | Hero refinement result |
|---|---|
| Tests | 7 frontend Python tests, 13 application scenarios, 11 film/accessibility states, 6 viewport checks passed |
| Build | 63 routes plus 404 generated |
| Syntax/types | Rendered templates and CSS exercised in Chromium; no Python or JavaScript source/type changes |
| Lint | Git whitespace check passed; CSS has no configured dedicated linter; legacy repository exceptions remain |
| Security | Gitleaks frontend scan: zero findings; no executable Python changes requiring a new Bandit scan |
| Scope/configuration | Hero copy in site.json, timing in site.config.json, homepage-only hero.css; no secrets added or paid calls made |
| Browser coverage | Chromium only; physical devices and other engines not verified |

References used for media fitting and fallback behavior: [MDN object-fit](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/object-fit) and [reduced motion](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/@media/prefers-reduced-motion).

Final hero review: **5/5 scoped criteria met** in the exercised local checks. Fresh-context visual review found no outstanding blockers after the 320px action and 900px heading collisions were corrected. Owner aesthetic acceptance remains pending.
