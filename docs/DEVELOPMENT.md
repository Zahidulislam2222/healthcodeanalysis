# Development guide

## Prerequisites

| Tool | Used for |
|---|---|
| Python 3.10+ (CI uses 3.12) | Frontend build, native migration compiler, automation toolkit, tests |
| Node.js (current LTS) | Frontend calculation tests, AskMe Worker |
| Docker with Compose | Local native WordPress stack |
| Git + pre-commit | Hooks: Ruff, JSON/YAML checks, private-key detection |

```bash
git clone https://github.com/Zahidulislam2222/healthcodeanalysis.git
cd healthcodeanalysis
python -m pip install -r requirements-dev.txt   # includes ruff, mypy, bandit, pre-commit
pre-commit install
# Gitleaks is a separate binary: https://github.com/gitleaks/gitleaks
```

## Repository map

| Path | What it is |
|---|---|
| `wordpress-native/` | **Current product.** Native Elementor migration compiler, scoped plugin, gateway templates, policy data, compose file. |
| `frontend/` | Preserved Neural Frontier design source (templates, styles, scripts, data, fonts). |
| `scripts/` | Frontend build/preview, static exporter and the retained automation toolkit ([scripts/README.md](../scripts/README.md)). |
| `workers/askme/` | Retained Cloudflare Worker retrieval chatbot ([README](../workers/askme/README.md)). |
| `deploy/shared-vps/` | Static rollback container definition ([README](../deploy/shared-vps/README.md)). |
| `docker/` | Original local WordPress stack for the automation toolkit ([README](../docker/README.md)). |
| `configs/` | Customer configuration template for the automation toolkit. |
| `tests/` | Committed automated test suites ([tests/README.md](../tests/README.md)). |
| `docs/` | Public documentation ([index](README.md)). |

## Common tasks

### Preview the original design

```bash
python scripts/build_frontend.py
python scripts/preview_frontend.py   # prints the local URL (configured in frontend/site.config.json)
```

### Build and run native WordPress locally

```bash
cp wordpress-native/.env.example wordpress-native/.env   # fill in local-only values
python wordpress-native/scripts/build_native.py
python wordpress-native/scripts/import_local.py \
  --docker docker --environment wordpress-native/.env \
  --compose wordpress-native/compose.yaml --project healthcode-elementor \
  --timeout 240 --replace-native-layouts
```

`--replace-native-layouts` overwrites local Elementor content. Export any editor changes you want to keep first. Details: [wordpress-native/README.md](../wordpress-native/README.md).

### Capacity model (offline arithmetic)

```bash
python wordpress-native/scripts/capacity_model.py wordpress-native/data/capacity-plan.json
```

## Quality gates

Run all of these before opening a pull request. Report any gate you could not run; don't skip it silently.

```bash
# Native contracts and configuration regression checks
python -m unittest discover -s tests -p "test_native_*.py"

# Frontend build tests and calculation tests
python -m unittest discover -s tests -p test_frontend.py
node --test frontend/tests/calculations.test.mjs
node --check frontend/scripts/app.mjs

# Static exporter and admin security header tests
python -m unittest discover -s tests -p test_static_export.py
python -m unittest discover -s tests -p test_admin_security_headers.py

# Retained automation suites (offline)
python tests/test_phase1.py && python tests/test_phase2_4.py && python tests/test_phase6.py && python tests/test_e2e_swap.py

# Lint, types, security
ruff check wordpress-native/scripts tests/test_native_contracts.py tests/test_native_configuration.py
mypy wordpress-native/scripts --ignore-missing-imports
bandit -q -ll -r wordpress-native/scripts
gitleaks protect --staged      # or: gitleaks detect
```

`tests/test_job_requirements.py` and `tests/test_live_integration.py` need a running local WordPress stack and are not part of the offline set. The AskMe Worker test (`npm test` in `workers/askme/`) currently fails under plain Node; see [DEFECT-LOG.md](../DEFECT-LOG.md).

## Configuration rules

- Secrets live only in ignored `.env` files or platform secret stores. `.env.example` files contain names and safe placeholders only.
- Environment-dependent values go through typed loaders (`wordpress-native/scripts/native_settings.py`, `scripts/frontend_settings.py`).
- Product policy and content live in data files (`wordpress-native/data/*.json`, `frontend/data/*.json`), not in control flow.
- Never hardcode model IDs, provider URLs, prices, ports or timeouts in business logic.
- Tests use unmistakably fake values (for example `test-key`, `example.invalid`).

## Branches, commits and pull requests

- Branch from `main`: `feat/…`, `fix/…`, `docs/…`, `chore/…`.
- Use conventional commit prefixes (`feat:`, `fix:`, `docs:`, `chore:`, `refactor:`, `test:`).
- One concern per pull request. Fill in the pull request template: acceptance criteria, gates run, real flow exercised.
- User-visible changes go in [CHANGELOG.md](../CHANGELOG.md).

See [CONTRIBUTING.md](../CONTRIBUTING.md) for the full contribution process.
