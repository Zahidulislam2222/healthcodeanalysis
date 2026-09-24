# Contributing

Thank you for your interest in HealthCode Analysis. This is a maintained portfolio and client-demonstration project. Issues and focused pull requests are welcome.

## Before you start

- **Security issues:** do not open an issue. Follow [SECURITY.md](SECURITY.md).
- **Larger changes:** open an issue first to agree on the approach.
- Read the [Code of Conduct](CODE_OF_CONDUCT.md).

## Setup

See [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) for prerequisites, local setup and the full list of quality gates.

## Pull request checklist

1. **Spec first.** State the acceptance criteria in the pull request (or add a failing test that reproduces the bug).
2. **Keep the scope small.** One feature or fix per pull request.
3. **No secrets, no hardcoded configuration.** Credentials go in ignored `.env` files; URLs, model IDs, limits and policy go in configuration or data files. Use obviously fake values in tests.
4. **Run the gates** listed in [DEVELOPMENT.md](docs/DEVELOPMENT.md#quality-gates) and paste the results into the pull request. Say explicitly if a gate could not run.
5. **Exercise the real flow.** Browser, HTTP or CLI, not just unit tests, for behavior changes.
6. **Keep the docs truthful.** If behavior, data flows or capacity claims change, update the relevant docs in the same pull request. Never move a **Planned** item to **Verified** without evidence.
7. **Update [CHANGELOG.md](CHANGELOG.md)** under *Unreleased* for user-visible changes.

## Content and medical-safety rules

- Do not add medical claims, reviewer credentials, ratings or testimonials that are not real and verifiable.
- New data collection (analytics, forms, accounts, uploads, AI calls) needs the legal gate in [docs/legal/COMPLIANCE-REGISTER.md](docs/legal/COMPLIANCE-REGISTER.md) and a threat-model update before merge.
- Educational tools must stay clearly labelled as non-clinical.

## Commit style

Use conventional commits: `feat:`, `fix:`, `docs:`, `chore:`, `refactor:`, `test:`, `ci:`.

## Licence

By contributing, you agree that your contributions are licensed under the [MIT License](LICENSE).
