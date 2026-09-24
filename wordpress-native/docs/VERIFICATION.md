# Native release verification record

Status: native WordPress is deployed on the configured public HTTPS origin. Local, restored-server and public browser checks passed. Owner visual acceptance and sustained capacity/uptime measurements remain outstanding.

| Gate | Latest evidence | Scope and limit |
|---|---|---|
| Preserved approved design | 205/205 snapshot hashes match | Original source/rendered reference retained. |
| Editable native layouts | 66 pages; zero HTML widgets | Core Elementor Free widgets, free header/footer builder, ACF fields and scoped behavior plugin. |
| Real editor round trip | Heading, button and image edits saved and restored | Local representative controls; metadata survived editor reload. |
| Application behavior | 13 browser scenarios pass | Includes preserved routes, search, reading list and six tools. |
| Motion and accessibility behavior | 11 states pass | Includes reduced motion, failed media and keyboard behavior; not a blanket WCAG certification. |
| Mobile visual correction | 20px header gutter and contained disclosure pass | Real browser geometry and screenshot; owner visual acceptance remains. |
| HTTP security/cache behavior | 21 checks pass locally and publicly | Warm cache, private bypass, protected routes and headers; 28-request production proxy test also passed: 17 rate-limit rejections; real client identity preserved despite forged headers. |
| MFA | Invalid code rejected; valid TOTP and Elementor access pass locally and on the public release | Recovery values retained privately; authenticated native editor opens. |
| Native behavior/configuration contracts | 11 tests pass | Remote Docker rejection, pinned local transport, config ownership and obvious secret/provider regression checks. |
| Python lint/types | Ruff pass; Mypy six source files pass | Native tooling scope; historical legacy exceptions remain separately recorded. |
| Blocking Python scan | Bandit medium/high gate passes | Lower-severity subprocess advisories reviewed; no suppressions used. |
| Secret scan | 177 candidate files, about 6.30 MB, no leaks | Redacted Gitleaks source report; earlier 43-commit history scan also clean. |
| Community security scans | General pack: 22 applicable rules/9 files; PHP pack: 23 rules/4 files; no findings | Static analysis does not prove absence of vulnerabilities. |
| Local cache smoke | 40/40 responses and cache hits at four workers | Loopback-only; not a 10k–1M concurrency benchmark. |
| Backups | Full separate-host SQL/content restore passed | 68 published pages and 156 valid Elementor layouts; restored runtime and MFA verified. |
| Deployment parity | 141/141 release files and project Caddy SHA256 match local | Original static release retained for rollback and legacy asset URLs. |
| Fresh-context source review | No outstanding material blocker | Final public checks subsequently passed; owner visual judgment remains separate. |
| CI | Manual guarded workflow prepared | Not activated or executed; no CI success badge or paid job claimed. |
| Legal/publication | Cited US/EU assessment and demo feature boundaries | Operator identity and future commercial activation remain explicit gates. |
| Uptime/capacity | Architecture and evidence register published | 99% and 10k–1M remain targets, not measured results. |

A blind legacy unittest discovery run failed because an old integration script assumes its original Docker runtime and executes at import time. The file was preserved. Its failure is not represented as a passing native integration test. The existing offline phase scripts passed 71, 46 and 38 checks; the original frontend suite passed 7 checks.

The project recovery checkpoint records private release identifiers, deployment progress, rollback and artifact locations. Credentials remain in the ignored recovery file and environment files. Public documentation never contains their values.

## Local commit closeout — 2026-09-14

The final local rerun passed 315 offline checks: 11 native contracts, 7 frontend Python tests, 5 JavaScript tests, 281 retained automation checks and 11 static-export tests. The frontend build generated 63 routes plus a real 404; the native build generated 66 pages with zero HTML widgets. Scoped native/frontend Ruff, Mypy, the medium/high Bandit gate and syntax checks on all four native PHP plugin files passed.

Whole-repository Ruff still reports eight findings in unchanged legacy scripts. The old runtime-dependent integration exception remains; CI was not activated. This documentation closeout does not constitute a new production deployment or a new capacity measurement. Prior public behavior, editor and parity evidence remains scoped to the recorded release.

Closeout Gitleaks scans found no leaks in the staged diff, the full 179-file index snapshot (about 6.34 MB), or the 43-commit history. Private recovery/document paths were absent from staging and the checked history. The installed edit scanner passed for the documentation corrections. The four added Python dependencies were verified on PyPI at their installed versions. Native configuration regression checks passed; provider URLs/model IDs remain in media configuration, and the schema.org/SVG identifiers are fixed protocol vocabulary. Unchanged legacy configuration exceptions remain outside this scoped release refactor.
