# HealthCode Analysis: US and EU publication, privacy and security assessment

## Scope and conclusion

This assessment covers a public editorial and technology demonstration: a WordPress site using native Elementor Free layouts, an illustrated medical-technology library, browser-based search, a device-local reading list and educational tools. Advertising, affiliate tracking, analytics, newsletters, public accounts and server-side health-data collection are disabled. Future commercial operation is a separate activation decision. The legal operator, establishment, client contracts and intended medical-device use have not been established.

“Demo” is a description, not a legal exemption. Hosting a public demonstration can still involve personal information in connection metadata and security logs. Likewise, calling a calculator educational does not by itself settle whether its functionality and intended use are regulated. This report distinguishes measures appropriate now from obligations that require a real operator and business model. It is an engineering applicability assessment, not a certification or a substitute for jurisdiction-specific legal advice.

Research was checked on 14 September 2026. Statutes, regulator guidance and technical documentation have different authority. Guidance explains enforcement or interpretation; it does not replace legislation. EU obligations can also depend on Member State implementation. US privacy, breach and accessibility obligations can vary by state and judicial circuit. A future launch requires a fresh jurisdiction review rather than an assertion that one privacy page covers every jurisdiction.

## Current data and content boundaries

| Activity | Intended data flow | Consequence and verification required |
|---|---|---|
| Reading public pages | Browser → hosting/CDN | Connection information may be processed even without analytics. Describe actual providers, log purpose and retention. |
| Library search and Ask the library | Static index downloaded; matching performed in browser | No remote language-model inference. Check network requests while submitting queries. |
| Reading list | Story identifiers in browser storage after saving | Explain persistence and provide removal/clear controls. Avoid collecting a central interest profile. |
| Educational tools | Form values used in browser memory | Do not send values in URLs, telemetry or form submissions; do not retain clinical inputs. |
| Image transformation | Browser reads a selected local image | Never claim anonymisation of medical images. Verify no upload and do not invite patient images. |
| WordPress administration | Authenticated staff → WordPress/database | Authentication cookies, administrator details and backups need protection even with no public accounts. |
| Imported stories | Thirty demonstration articles, not independently verified | Preserve for layout review, label clearly and exclude from indexing until editorial review. |
| Brain illustration | Previously generated image/video served as assets | Disclose synthetic illustration; do not represent it as a patient scan or clinical evidence. |

The distinction between “the operator does not receive calculator inputs” and “the site processes no personal data” is essential. Only the former can be supported by a passing browser-network test. Server/CDN behavior, administrator access and backup storage need separate evidence.

## European Union

### GDPR scope, transparency and data protection

The EDPB explains GDPR territorial scope through establishment and, for relevant non-EU operators, offering goods/services to people in the Union or monitoring their behavior. Mere website availability is not the whole test. A stated plan to target EU users requires assessment before launch; no operator-country exemption should be assumed.[1]

For an applicable operation, identify the controller and a working contact, record purposes and lawful bases, limit collection, explain retention and recipients, and support relevant individual rights. The EDPB small-business guide is a practical starting point. The demo cannot honestly publish a fictitious controller, supervisory authority or data-protection officer. Before collecting public submissions, complete the operator record and adopt an actual request-handling procedure.[2]

Security must address confidentiality, integrity and availability. Access privileges, updates, backups and restoration are operational duties, not badges supplied by a plugin. Evaluate whether planned high-risk processing requires a data-protection impact assessment. Sensitive clinical data and user profiling materially change the assessment.[3]

If a personal-data breach occurs, assess notification obligations promptly. EDPB guidance describes the controller’s 72-hour notification framework and the distinction between regulator notification and communication to affected people; processors must alert controllers without undue delay. Preserve a decision record even when notification is not required. Do not silently substitute the US health-breach deadline.[4]

International transfers require their own analysis. The Commission describes mechanisms including adequacy decisions and contractual safeguards. A server physically located in Europe does not settle transfers involving a CDN, support personnel, email provider or overseas administrative access. A future client must verify processor terms, recipients, relevant transfer mechanisms and any associated assessment.[5]

### Cookies and similar storage

EU guidance distinguishes storage necessary for a service explicitly requested by a person from storage requiring prior consent. Nonessential analytics/advertising must not execute before the applicable consent. Clear information and a genuine choice are required; a cosmetic banner does not make tracking lawful.[6]

For this demo, keep nonessential integrations absent. Treat the explicitly requested local reading list as a documented functional-storage use, while recording that Member State interpretation still matters. Retain clear/individual-remove controls. Do not add a cookie-consent vendor solely for appearance when no consent-requiring feature exists. If tracking is enabled later, test refusal, withdrawal and consent persistence as real behavioral flows. Authentication and security cookies must also be accurately described.

### AI transparency

The Commission’s guidance updated 6 August 2026 states that Article 50 applies from 2 August 2026. It distinguishes provider duties from deployer disclosure duties, including relevant synthetic content and certain public-interest text without human review/editorial control.[7]

The site’s existing Ask the library function retrieves local matches; it is not a deployed generative chatbot. Explain that behavior plainly. The brain asset should be labelled as AI-generated illustration, not diagnostic imagery. Imported articles’ provenance and editorial status must be disclosed without inventing a human reviewer. If a client later connects an AI API, assess the actual provider/deployer roles, transparency, training use, transfers and processing of submitted health information before activation.

### Medical-device software

The Commission’s MDCG software guidance was revised in June 2025. Qualification and classification depend on intended purpose and functionality. Medical terminology, promotional claims and the information produced by software can matter; a footer disclaimer alone cannot establish an exemption.[8]

Keep clinical calculators within an explicitly educational demonstration. Do not advertise diagnostic accuracy, treatment selection, validated clinical use or regulatory clearance. Before offering patient-specific clinical decision support commercially, obtain a documented qualification/classification decision and address the applicable evidence, quality, risk and conformity obligations. Browser-only execution protects data flow but does not itself resolve device regulation.

### Accessibility and commercial activity

The European Accessibility Act covers specified products and services; it is not a universal rule covering every informational blog. E-commerce or other covered services may change applicability, and exemptions require factual assessment. The official EU guidance describes covered services and relevant microenterprise considerations.[9]

Apply accessible navigation, meaningful labels, keyboard use, focus visibility, usable contrast and reduced-motion behavior now. Test the actual rendered Elementor output. Do not publish a blanket WCAG conformance statement based on automated checks alone. If sales are added, separately assess consumer-information, cancellation, pricing, tax and country-specific requirements before checkout exists.

## United States

### HIPAA and consumer health information

HHS states that HIPAA applies to covered entities and business associates. A health-themed publication does not automatically become HIPAA-covered. A future arrangement processing protected health information for a covered client can change the result. Do not advertise “HIPAA compliant” based on TLS, WordPress hardening or a privacy policy.[10]

The FTC Health Breach Notification Rule covers specified non-HIPAA personal-health-record vendors, related entities and service providers. Its 2024 amendments address health apps and connected devices. Coverage and an actionable breach depend on the actual records and relationships; notification can concern unauthorized disclosure, not only hacking. The present local-only tools are not established to be a covered PHR service. Reassess before connecting sources or retaining identifiable health records.[11]

Washington’s My Health My Data framework separately addresses consumer health data and includes enforcement through its Consumer Protection Act. State health-data duties may extend beyond HIPAA and must be reviewed before collecting or inferring health interests. A linked medical topic and an identifiable user can be relevant to risk analysis even without a clinical chart. The source scope is state-specific; it should not be generalized to all US states.[12]

### General privacy and children

California’s CCPA applies to qualifying businesses and provides privacy rights and notice obligations. Applicability depends on facts including business activity, applicable thresholds and data practices; a small demo is not automatically covered or exempt. Before commercial launch, evaluate current thresholds and state laws for the actual operator. Where applicable, implement sale/sharing opt-outs and recognized preference signals as real controls, not decorative links.[13]

COPPA can apply to child-directed services and general-audience services with actual knowledge of collecting personal information from children under 13. The FTC guidance explains that the audience and collection practices matter. Do not add a children’s signup flow, age collection or targeted advertising without reviewing the rules. The demo should not solicit children’s data or create public accounts.[14]

### Editorial truth, affiliate marketing and reviews

FTC endorsement guidance requires material connections to be disclosed clearly and conspicuously in context. A generic footer disclosure is not a replacement for a nearby understandable disclosure when an endorsement or affiliate relationship requires one. Future affiliate links must be recorded in maintained content, visibly disclosed and technically labelled appropriately.[15]

The FTC’s consumer-review rule addresses specified false or deceptive reviews and testimonials. Do not invent product ownership, testing experience, reviewer identities, ratings or customer quotes. The present imported stories are layout demonstrations, not verified test reports. Search markup must not transform their unsupported statements into review ratings or medical authority.[16]

For a real editorial release, maintain claim-level sources, distinguish manufacturer statements from independent evidence, record conflicts, and have qualified review where medical claims justify it. This is a practical publication gate, not a claim that every editorial statement is subject to one identical statutory requirement.

### Accessibility

DOJ guidance addresses accessible websites for state/local governments and businesses open to the public. The legal setting and applicable standards depend on the entity and context. Treat keyboard, screen-reader structure, text alternatives, motion control and clear errors as baseline engineering work. A passing automated audit does not settle all ADA questions or establish full accessibility.[17]

## Search and search-agent discoverability

Google states that its ordinary search foundations remain relevant to AI features and that there is no special required AI markup or file. Technical eligibility does not guarantee indexing or a citation. Focus on crawlable text, useful internal links, consistent canonical URLs, understandable content and accurate structured data.[18]

Article markup should describe real page facts. Do not invent authors, credentials, publication dates, review dates or rating aggregates merely to fill schema properties. Until demonstration articles receive editorial verification, a truthful WebPage representation and noindex are preferable to fabricated authoritative Article metadata.[19]

OpenAI distinguishes OAI-SearchBot discovery from GPTBot training controls. It also explains the relevance of accessible roles and labels to agent interaction. Permit public discovery where appropriate while allowing crawlers to see noindex on excluded material. Robots directives are cooperative instructions, not access controls or proof of a bot’s identity.[20]

Canonical tags, social metadata, eligible-only sitemaps, stable routes and honest descriptions should be verified from HTTP responses. Query variants, private reading lists, administrative surfaces and unverified imported content should not become duplicate public search results. Search Console and equivalent owner-verification services can be connected later with the actual account; no account ownership or indexing success should be claimed without evidence.

## Security model and release obligations

WordPress hardening guidance emphasizes updates, trustworthy packages, least privilege and layered protection. It specifically warns that additional admin protection must preserve required AJAX behavior. Security reduces risk; it does not make a site unhackable.[21]

The planned release controls are: isolated database networking; loopback exposure behind TLS; protected credentials outside the document root; file editing disabled in the dashboard; restricted unused interfaces; upload execution prevention; bounded login requests; compatible browser headers; strong administrative authentication; backed-up persistent state; and tested restore. Controls must be reported as planned, implemented or verified rather than conflated.

NGINX supports request-rate limits and explicit rejection status codes. Apply limits narrowly to login attempts so ordinary page reads, search bots and authenticated editor saves are not treated as attacks. Validate client-IP trust boundaries behind the existing proxy; do not trust arbitrary forwarded headers from the internet.[22]

## Activation gates for a real client

| Proposed feature | Required work before enabling |
|---|---|
| Real publication/indexing | Verify claims, authorship, source rights, dates and conflicts; record editorial approval. |
| Analytics/advertising | Data-flow map; jurisdiction/consent assessment; pre-consent blocking; refusal/withdrawal tests; truthful notices. |
| Affiliate links | Actual commercial relationship and close-by disclosures; link classification; product-claim review. |
| Newsletter | Working operator/contact; consent or other applicable permission basis; unsubscribe; suppression; provider terms and retention. |
| Public accounts | Authorization tests, secure recovery, abuse controls, deletion/export workflow and retention policy. |
| Health information | Regulatory qualification, privacy basis, processor contracts, impact/risk assessment, access controls and breach procedure. |
| Generative AI | Appropriate disclosures, model/provider configuration, no unintended training or health-data transfer, cost authorization. |
| US/EU commercial launch | Identified operator and target jurisdictions, current legal review, accessible service flow and verified public notices. |

The demo can demonstrate these engineering boundaries without pretending the future business decisions have already been made. No paid integration is necessary for the current scope.

## Sources

1. EDPB. [Guidelines 3/2018 on territorial scope](https://www.edpb.europa.eu/documents/guideline/guidelines-32018-on-the-territorial-scope-of-the-gdpr-article-3-version-adopted_en), final version, 12 November 2019.
2. EDPB. [Data protection guide for small business](https://www.edpb.europa.eu/sme_en), current guide accessed 14 September 2026.
3. EDPB. [Secure personal data](https://www.edpb.europa.eu/sme/be-compliant/secure-personal-data_en), accessed 14 September 2026.
4. EDPB. [Data breaches](https://www.edpb.europa.eu/sme/assess-the-risks/data-breaches_en), accessed 14 September 2026.
5. European Commission. [Rules on international data transfers](https://commission.europa.eu/law/law-topic/data-protection/international-dimension-data-protection/rules-international-data-transfers_en), accessed 14 September 2026.
6. Your Europe. [Online privacy: cookies](https://europa.eu/youreurope/business/growing/digitalising/online-privacy/index_en.htm), accessed 14 September 2026.
7. European Commission. [AI transparency guidelines](https://digital-strategy.ec.europa.eu/en/policies/guidelines-ai-transparency-obligations), updated 6 August 2026.
8. European Commission. [MDCG 2019-11 revision 1](https://health.ec.europa.eu/latest-updates/update-mdcg-2019-11-rev1-qualification-and-classification-software-regulation-eu-2017745-and-2025-06-17_en), 17 June 2025.
9. Your Europe. [Accessibility of products and services](https://europa.eu/youreurope/business/selling-in-eu/selling-goods-services/accessibility/index_en.htm), accessed 14 September 2026.
10. HHS. [Covered entities and business associates](https://www.hhs.gov/hipaa/for-professionals/covered-entities/index.html), accessed 14 September 2026.
11. FTC. [Complying with the Health Breach Notification Rule](https://www.ftc.gov/business-guidance/resources/complying-ftcs-health-breach-notification-rule-0), accessed 14 September 2026.
12. Washington Attorney General. [Protecting Washingtonians’ personal health data](https://www.atg.wa.gov/protecting-washingtonians-personal-health-data-and-privacy), indexed official guidance accessed 14 September 2026; direct retrieval returned 403.
13. California Attorney General. [CCPA](https://oag.ca.gov/privacy/ccpa), updated 28 August 2026. Confirm current statutory/regulatory thresholds rather than treating the FAQ as an individualized opinion.
14. FTC. [COPPA frequently asked questions](https://www.ftc.gov/business-guidance/resources/complying-coppa-frequently-asked-questions), accessed 14 September 2026.
15. FTC. [Endorsement Guides: what people are asking](https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking), accessed 14 September 2026.
16. FTC. [Consumer Reviews and Testimonials Rule Q&A](https://www.ftc.gov/business-guidance/resources/consumer-reviews-testimonials-rule-questions-answers), accessed 14 September 2026.
17. US DOJ. [Web accessibility and the ADA](https://www.ada.gov/resources/web-guidance/), accessed 14 September 2026.
18. Google Search Central. [AI features and your website](https://developers.google.com/search/docs/appearance/ai-features), accessed 14 September 2026.
19. Google Search Central. [Article structured data](https://developers.google.com/search/docs/appearance/structured-data/article), accessed 14 September 2026.
20. OpenAI. [Publishers and Developers FAQ](https://help.openai.com/en/articles/12627856), accessed 14 September 2026.
21. WordPress. [Hardening WordPress](https://developer.wordpress.org/advanced-administration/security/hardening/), accessed 14 September 2026.
22. NGINX. [Request limiting module](https://nginx.org/en/docs/http/ngx_http_limit_req_module.html), accessed 14 September 2026.
23. FDA. [Clinical Decision Support Software](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/clinical-decision-support-software), January 2026 final guidance. This provides the US counterpart to the medical-software activation review; no exemption determination has been made for these tools.

The EUR-Lex GDPR text could not be retrieved because of its browser-verification gate. This assessment therefore relies on the cited regulator guidance for the GDPR discussion and does not represent that a complete statutory text review succeeded.
