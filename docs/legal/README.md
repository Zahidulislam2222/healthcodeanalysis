# Legal and compliance documentation

> **Not legal advice.** These documents were prepared by the engineering maintainer from primary regulator guidance and the system's actual, verified data flows. Before any commercial launch, operator change or new data-collection feature, a qualified lawyer in the relevant jurisdictions must review them.

## Two kinds of document

| Kind | Where | Status |
|---|---|---|
| **Published demonstration notices.** These are what visitors see today at `/privacy-policy/`, `/terms-of-use/`, `/accessibility/`, `/affiliate-disclosure/` and the editorial policy page. | Source of truth: [`wordpress-native/data/public-notices.json`](../../wordpress-native/data/public-notices.json) | **Live.** They describe the demonstration accurately. Edit that data file, not a copy. |
| **Launch templates and registers.** These are for an operator taking the project into real publication. | This folder | **Templates.** `[BRACKETED]` fields must be completed and reviewed. |

## Contents

| Document | Purpose | Usable as-is? |
|---|---|---|
| [COMPLIANCE-REGISTER.md](COMPLIANCE-REGISTER.md) | Law-by-law applicability, current status and activation gates (EU, UK, US, Bangladesh) | Yes, as an engineering register |
| [MEDICAL-DISCLAIMER.md](MEDICAL-DISCLAIMER.md) | Not-medical-advice and educational-tool boundaries | Yes (extends the live terms) |
| [COOKIES-AND-STORAGE.md](COOKIES-AND-STORAGE.md) | Verified inventory of cookies and browser storage | Yes (inventory as of the review date) |
| [SUBPROCESSORS.md](SUBPROCESSORS.md) | Service providers that can process data | Needs the hosting provider named |
| [AI-TRANSPARENCY.md](AI-TRANSPARENCY.md) | Where AI is and is not used | Yes |
| [ACCESSIBILITY.md](ACCESSIBILITY.md) | Accessibility statement, target and known limits | Needs an operator feedback contact |
| [EDITORIAL-AND-COPYRIGHT-POLICY.md](EDITORIAL-AND-COPYRIGHT-POLICY.md) | Editorial verification, corrections, image rights, takedown | Needs operator contacts |
| [PRIVACY-POLICY-TEMPLATE.md](PRIVACY-POLICY-TEMPLATE.md) | Full privacy policy for a real operator | Template |
| [TERMS-OF-USE-TEMPLATE.md](TERMS-OF-USE-TEMPLATE.md) | Full terms of use for a real operator | Template |

The detailed US/EU research with citations is in [`wordpress-native/docs/US-EU-RESEARCH.md`](../../wordpress-native/docs/US-EU-RESEARCH.md). The long-form narrative is in [PUBLIC-TECHNICAL-OVERVIEW.md](../PUBLIC-TECHNICAL-OVERVIEW.md) sections 15–18.

## Ground rules

1. A policy must describe what the system **actually does**. When code changes a data flow, the policy changes in the same pull request.
2. Collection features (`analytics`, `advertising`, `affiliates`, `newsletter`, `public_accounts`, `health_data_collection` in [`publishing-policy.json`](../../wordpress-native/data/publishing-policy.json)) stay `false` until the matching gate in the compliance register is met.
3. No invented operator identity, credentials, reviewers, ratings or compliance certifications.
