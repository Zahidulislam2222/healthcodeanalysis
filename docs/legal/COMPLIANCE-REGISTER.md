# Compliance register

**Last reviewed:** 24 September 2026. **Not legal advice.** Applicability depends on the operator's establishment, audience, revenue and actual processing. Laws change, so re-verify every row before launch.

**Status key:** **N/A (demo)** = not triggered by current features · **Addressed** = engineering controls in place for the current scope · **Gate** = must be satisfied before the named feature is enabled · **Operator** = requires the legal operator's facts or decision.

## 1. Current data inventory (what triggers most of these laws)

| Data | Collected? | Where |
|---|---|---|
| IP address, request metadata | Yes, by infrastructure | Cloudflare and the hosting server (security, delivery, logs) |
| Administrator account data | Yes, editors only | WordPress database and backups |
| Reader health inputs (calculators, worksheets, images) | **No.** Processed in the browser only | Reader's device |
| Search queries | **No.** Matched in the browser | Reader's device |
| Reading list | **No.** Stored in the reader's browser only | `localStorage` |
| Analytics, advertising IDs, newsletter emails, public accounts | **No.** Features disabled | — |
| Chat messages (legacy snapshot only) | Yes, for visitors of the legacy `healthcodeanalysis.pages.dev` snapshot (`/askme-proxy`) | Cloudflare Worker; greetings forwarded to Google Dialogflow. Not part of the native site; decommission or document in a privacy notice |

## 2. European Union

| Law / instrument | Trigger | Current status | Gate before activation |
|---|---|---|---|
| **GDPR** (Reg. 2016/679), Art. 3 territorial scope | EU establishment, or offering to / monitoring people in the EU | **Operator.** Minimal processing today (connection metadata, editor accounts) | Identify the controller and contact; record purposes and lawful bases; transparent notice; rights handling; processor contracts (Art. 28). |
| GDPR Art. 9, special-category (health) data | Collecting or inferring health data | **N/A (demo).** Health inputs never leave the browser | Explicit legal basis, DPIA (Art. 35), strict access controls, contracts. |
| GDPR Art. 33/34, breach notification | Personal-data breach | **Addressed:** process in [INCIDENT-RESPONSE.md](../INCIDENT-RESPONSE.md) | Supervisory-authority notification within 72 hours where required. |
| GDPR Chapter V, international transfers | Transfers outside the EEA (CDN, host) | **Operator** | Transfer mechanism assessed per provider. |
| **ePrivacy Directive** Art. 5(3), cookies and storage | Storing or reading information on a device | **Addressed:** only strictly necessary or user-requested storage ([COOKIES-AND-STORAGE.md](COOKIES-AND-STORAGE.md)) | Prior consent with real pre-consent blocking, equal refusal and withdrawal before any analytics or ads. |
| **EU AI Act** (Reg. 2024/1689) Art. 50 transparency | AI systems interacting with people or generating synthetic content | **Addressed:** artwork disclosed as AI-generated; search is retrieval, not generative ([AI-TRANSPARENCY.md](AI-TRANSPARENCY.md)) | Role and transparency assessment before any chatbot or model integration. Commission guidance states Art. 50 applies from 2 August 2026. |
| **Medical Device Regulation** (Reg. 2017/745), MDCG 2019-11 | Software intended for diagnosis/treatment of individuals | **Addressed:** tools are educational and bounded ([MEDICAL-DISCLAIMER.md](MEDICAL-DISCLAIMER.md)) | Qualification and classification decision before any patient-specific clinical use. |
| **European Accessibility Act** (Dir. 2019/882) | Covered products/services such as e-commerce | **N/A (demo):** no covered service | Reassess if checkout or other covered services are added. |
| **Digital Services Act** | Hosting third-party content | **N/A (demo):** no user-generated content | Notice-and-action, terms and transparency duties if comments or uploads are added. |

## 3. United Kingdom

| Law | Trigger | Current status | Gate |
|---|---|---|---|
| **UK GDPR** and Data Protection Act 2018 | UK establishment or targeting UK people | **Operator** | Same duties as GDPR; ICO fee/registration assessment; UK transfer mechanisms. |
| **PECR** (as amended) | Cookies and electronic marketing | **Addressed** for current storage | Consent for non-exempt cookies; marketing consent for a newsletter. |

## 4. United States

| Law / rule | Trigger | Current status | Gate |
|---|---|---|---|
| **HIPAA** | Covered entities and business associates handling PHI | **N/A (demo):** not a covered entity; no PHI | Reassess for any provider/health-plan client or PHI workflow; a BAA is required with vendors. |
| **FTC Health Breach Notification Rule** (16 CFR 318) | Vendors of personal health records not covered by HIPAA | **N/A (demo):** no identifiable health records stored | Assess before storing or syncing health data. |
| **FTC Act §5** (unfair/deceptive practices) | Any public claims | **Addressed:** no invented credentials, ratings or compliance claims | Keep privacy statements accurate as features change. |
| **Washington My Health My Data Act**; Nevada SB 370; Connecticut consumer-health-data provisions | Collecting consumer health data (no revenue threshold in Washington) | **N/A (demo):** none collected server-side | Consumer health data privacy policy, consent, and no geofencing around health facilities. |
| **CCPA/CPRA** (California) and other state comprehensive privacy laws | Statutory thresholds (revenue, consumer volume, or revenue share from selling/sharing data) | **Operator** | Notices, rights requests, opt-out of sale/sharing, honoring Global Privacy Control where required. |
| **COPPA** | Child-directed service, or actual knowledge of users under 13 | **N/A (demo):** general audience; no accounts | Assess before accounts or age-specific content. |
| **FTC Endorsement Guides** (16 CFR 255) and **Consumer Reviews and Testimonials Rule** (16 CFR 465) | Affiliate links, sponsored content, reviews | **Addressed:** no affiliates; demonstration reviews labelled unverified | Clear nearby disclosure; no fake or unverifiable reviews. |
| **FDA clinical decision support** guidance | Software supporting patient-specific clinical decisions | **Addressed:** educational only | Regulatory assessment before clinical use. |
| **ADA** (Title III, per DOJ web guidance) | Public accommodations online | **Operator** | WCAG 2.2 AA audit ([ACCESSIBILITY.md](ACCESSIBILITY.md)). |
| **CAN-SPAM** | Commercial email | **N/A (demo):** no newsletter | Identification, physical address, working unsubscribe honored within 10 business days. |
| **DMCA §512** safe harbor | Hosting user-uploaded content | **N/A (demo)** | Register a designated agent with the US Copyright Office; takedown process ([EDITORIAL-AND-COPYRIGHT-POLICY.md](EDITORIAL-AND-COPYRIGHT-POLICY.md)). |
| State breach-notification laws | Breach of residents' personal information | **Addressed:** process defined | Per-state assessment during an incident. |

## 5. Bangladesh

| Law | Trigger | Current status | Gate |
|---|---|---|---|
| **Personal Data Protection Act 2026** (replacing the 2025 Ordinance) | Processing personal data by entities subject to Bangladeshi law | **Operator.** Secondary sources report phased implementation through 2027. **Not verified against the official gazette text.** | Obtain local counsel review of the current text if the operator is established in Bangladesh. |

## 6. Cross-cutting engineering controls already in place

- Data minimization by design: browser-only tools and search, and no analytics.
- Security of processing: MFA, a hardened attack surface, CSP, rate limiting, internal-only database ([THREAT-MODEL.md](../THREAT-MODEL.md)).
- Tested backup and restore ([BACKUP-AND-DISASTER-RECOVERY.md](../BACKUP-AND-DISASTER-RECOVERY.md)).
- Indexing restricted to editorially eligible content; no fabricated structured data.
- Feature flags that keep collection off: [`publishing-policy.json`](../../wordpress-native/data/publishing-policy.json).

## 7. Primary sources

- GDPR: <https://eur-lex.europa.eu/eli/reg/2016/679/oj> · EDPB territorial scope: <https://www.edpb.europa.eu/documents/guideline/guidelines-32018-on-the-territorial-scope-of-the-gdpr-article-3-version-adopted_en>
- EDPB breach guidance: <https://www.edpb.europa.eu/sme/assess-the-risks/data-breaches_en>
- EU online privacy / cookies: <https://europa.eu/youreurope/business/growing/digitalising/online-privacy/index_en.htm>
- EU AI transparency: <https://digital-strategy.ec.europa.eu/en/policies/guidelines-ai-transparency-obligations>
- MDCG 2019-11: <https://health.ec.europa.eu/latest-updates/update-mdcg-2019-11-rev1-qualification-and-classification-software-regulation-eu-2017745-and-2025-06-17_en>
- EU accessibility: <https://europa.eu/youreurope/business/selling-in-eu/selling-goods-services/accessibility/index_en.htm>
- UK ICO: <https://ico.org.uk/for-organisations/>
- HHS HIPAA covered entities: <https://www.hhs.gov/hipaa/for-professionals/covered-entities/index.html>
- FTC Health Breach Notification Rule: <https://www.ftc.gov/business-guidance/resources/complying-ftcs-health-breach-notification-rule-0>
- Washington My Health My Data: <https://www.atg.wa.gov/protecting-washingtonians-personal-health-data-and-privacy>
- California CCPA: <https://oag.ca.gov/privacy/ccpa>
- COPPA FAQ: <https://www.ftc.gov/business-guidance/resources/complying-coppa-frequently-asked-questions>
- FTC endorsements: <https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking> · Reviews rule: <https://www.ftc.gov/business-guidance/resources/consumer-reviews-testimonials-rule-questions-answers>
- FDA clinical decision support: <https://www.fda.gov/regulatory-information/search-fda-guidance-documents/clinical-decision-support-software>
- DOJ web accessibility: <https://www.ada.gov/resources/web-guidance/> · WCAG 2.2: <https://www.w3.org/TR/WCAG22/>
- FTC CAN-SPAM guide: <https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business>
- US Copyright Office DMCA agent directory: <https://www.copyright.gov/dmca-directory/>
- Bangladesh PDPA (secondary summaries): <https://securiti.ai/bangladesh-personal-data-protection-act-overview/> · <https://www.thedailystar.net/tech-startup/news/bangladeshs-personal-data-protection-ordinance-2025-key-takeaways-4015401>
