# Documentation

Every document here separates what is **Live/Verified** from what is **Planned** or a **Target**. No document claims measured capacity, guaranteed uptime or legal compliance that has not been established.

## Start here

| If you are… | Read |
|---|---|
| A client or reviewer | [Main README](../README.md) → [Architecture](ARCHITECTURE.md) → [Roadmap](ROADMAP.md) → [Public technical overview](PUBLIC-TECHNICAL-OVERVIEW.md) |
| A developer | [Development guide](DEVELOPMENT.md) → [Architecture](ARCHITECTURE.md) → [`wordpress-native/README.md`](../wordpress-native/README.md) |
| An operator | [Operations runbook](OPERATIONS-RUNBOOK.md) → [Backup and DR](BACKUP-AND-DISASTER-RECOVERY.md) → [Incident response](INCIDENT-RESPONSE.md) |
| A security researcher | [SECURITY.md](../SECURITY.md) → [Threat model](THREAT-MODEL.md) |
| Legal / compliance | [Legal pack](legal/README.md) → [Compliance register](legal/COMPLIANCE-REGISTER.md) |

## Engineering

| Document | Contents |
|---|---|
| [ARCHITECTURE.md](ARCHITECTURE.md) | Components (frontend and backend), state ownership, request lifecycle, design decisions |
| [SCALABILITY-AND-RELIABILITY.md](SCALABILITY-AND-RELIABILITY.md) | Capability register, capacity model, 1M-reader reference architecture, 99% SLO and error budget |
| [ROADMAP.md](ROADMAP.md) | Phases 0–4 (foundation → 1M-reader qualification), legal and quality tracks, exit criteria |
| [THREAT-MODEL.md](THREAT-MODEL.md) | STRIDE analysis, controls and residual risks |
| [DEVELOPMENT.md](DEVELOPMENT.md) | Setup, repository map, quality gates, configuration rules |
| [PUBLIC-TECHNICAL-OVERVIEW.md](PUBLIC-TECHNICAL-OVERVIEW.md) | Long-form release narrative and evidence (release edition of 14 September 2026; documentation update of 24 September 2026) |

## Operations

| Document | Contents |
|---|---|
| [OPERATIONS-RUNBOOK.md](OPERATIONS-RUNBOOK.md) | Deploy, rollback, cache, maintenance, secret rotation, monitoring |
| [BACKUP-AND-DISASTER-RECOVERY.md](BACKUP-AND-DISASTER-RECOVERY.md) | What is backed up, restore evidence, RPO/RTO, drills |
| [INCIDENT-RESPONSE.md](INCIDENT-RESPONSE.md) | Severity levels, response flow, breach-notification decision tree, post-incident review |

## Legal and compliance

| Document | Contents |
|---|---|
| [legal/COMPLIANCE-REGISTER.md](legal/COMPLIANCE-REGISTER.md) | GDPR, UK GDPR, ePrivacy, EU AI Act, MDR, EAA, HIPAA, FTC, state health-data laws, CCPA, COPPA, ADA, CAN-SPAM, DMCA, Bangladesh PDPA |
| [legal/MEDICAL-DISCLAIMER.md](legal/MEDICAL-DISCLAIMER.md) | Not-medical-advice statement |
| [legal/COOKIES-AND-STORAGE.md](legal/COOKIES-AND-STORAGE.md) | Verified cookie/storage inventory |
| [legal/SUBPROCESSORS.md](legal/SUBPROCESSORS.md) | Service providers |
| [legal/AI-TRANSPARENCY.md](legal/AI-TRANSPARENCY.md) | Where AI is and is not used |
| [legal/ACCESSIBILITY.md](legal/ACCESSIBILITY.md) | Accessibility statement and roadmap |
| [legal/EDITORIAL-AND-COPYRIGHT-POLICY.md](legal/EDITORIAL-AND-COPYRIGHT-POLICY.md) | Editorial verification, corrections, takedown |
| [legal/PRIVACY-POLICY-TEMPLATE.md](legal/PRIVACY-POLICY-TEMPLATE.md), [legal/TERMS-OF-USE-TEMPLATE.md](legal/TERMS-OF-USE-TEMPLATE.md) | Launch templates for a real operator |

## Component documentation

- [`wordpress-native/`](../wordpress-native/README.md): native implementation, with its [acceptance criteria](../wordpress-native/ACCEPTANCE.md), [verification record](../wordpress-native/docs/VERIFICATION.md) and [US/EU research](../wordpress-native/docs/US-EU-RESEARCH.md)
- [`frontend/`](../frontend/README.md): design source, with [design notes](../frontend/DESIGN.md) and [validation](../frontend/VALIDATION.md)
- [`workers/askme/`](../workers/askme/README.md) · [`scripts/`](../scripts/README.md) · [`tests/`](../tests/README.md) · [`docker/`](../docker/README.md) · [`deploy/shared-vps/`](../deploy/shared-vps/README.md)

## Project records

[CHANGELOG.md](../CHANGELOG.md) · [DEFECT-LOG.md](../DEFECT-LOG.md) · [THIRD-PARTY-NOTICES.md](../THIRD-PARTY-NOTICES.md) · [CONTRIBUTING.md](../CONTRIBUTING.md) · [CODE_OF_CONDUCT.md](../CODE_OF_CONDUCT.md) · [SUPPORT.md](../SUPPORT.md)
