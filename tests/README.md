# Tests

Committed automated suites. All suites except the two marked below run offline.

| File | Covers | How to run | Latest local result (24 Sep 2026) |
|---|---|---|---|
| `test_native_contracts.py`, `test_native_configuration.py` | Native build contracts, remote-Docker rejection, config ownership, secret/provider regression checks | `python -m unittest discover -s tests -p "test_native_*.py"` | 11/11 pass |
| `test_frontend.py` | Design-source build: routes, escaping, rebuild manifest | `python -m unittest discover -s tests -p test_frontend.py` | 7/7 pass |
| `../frontend/tests/calculations.test.mjs` | Educational tool calculations and search ranking | `node --test frontend/tests/calculations.test.mjs` | 5/5 pass |
| `test_static_export.py` | Static exporter: origin rewriting, index shape, form guard | `python -m unittest discover -s tests -p test_static_export.py` | 11/11 pass |
| `test_admin_security_headers.py` | Admin security headers | `python -m unittest discover -s tests -p test_admin_security_headers.py` | 1/1 pass |
| `test_phase1.py` | API client, Elementor parser, config validator | `python tests/test_phase1.py` | 71/71 pass |
| `test_phase2_4.py` | Image/text/SEO swap | `python tests/test_phase2_4.py` | 46/46 pass |
| `test_phase6.py` | cPanel cloning and migration scripts | `python tests/test_phase6.py` | 38/38 pass |
| `test_e2e_swap.py` | End-to-end swap across widget types | `python tests/test_e2e_swap.py` | 126/126 pass |
| `test_job_requirements.py` | Original client requirements against a live local stack | Needs the `docker/` stack running | Not run (requires a live stack) |
| `test_live_integration.py` | Integration against its original Docker runtime | Needs the original runtime | Not run (requires a live stack) |
| `../workers/askme/test/content-search.test.mjs` | AskMe search | `npm test` in `workers/askme` | **Fails:** JSON import attribute / generated index missing (see `DEFECT-LOG.md`) |

**Offline total:** 316 checks passing. These tests prove code behavior in the stated scope. They are not load tests and not evidence of production capacity or uptime.
