# Incident response plan

**Applies to:** the live publication, its hosting, CDN, DNS, repository and credentials.
**Status:** defined process. On-call rotation and automated paging are **planned** (roadmap Phase 1); today the maintainer responds manually.

## 1. Severity levels

| Level | Definition | Examples | Target response |
|---|---|---|---|
| **SEV-1** | Site down, content tampered, or suspected personal-data breach | Origin unreachable; defacement; leaked admin credential | Acknowledge within 1 hour; continuous work until mitigated |
| **SEV-2** | Major degradation or security weakness being exploited | Error rate > 5%; login flood bypassing limits | Acknowledge within 4 hours |
| **SEV-3** | Minor degradation, no data risk | One page broken; slow cold cache | Next business day |
| **SEV-4** | Cosmetic issues or hardening findings | Duplicate header; typo | Scheduled normally |

The response targets above are goals, not a contractual SLA.

## 2. Roles

For a single-maintainer project, one person may hold all of these roles. List them anyway so they can be handed over.

- **Incident lead:** owns decisions and the timeline.
- **Operator:** executes the runbook steps.
- **Communications:** updates the status page and notifies affected parties.
- **Scribe:** keeps the timestamped log used in the review.

## 3. Response flow

1. **Detect:** probe alert, error report, security report (see [SECURITY.md](../SECURITY.md)) or anomaly.
2. **Triage:** assign severity; open a private incident record with a timestamped log.
3. **Contain:**
   - Tampering or compromise: put the site in maintenance or roll back routing to the retained static release; rotate the affected credentials; revoke sessions.
   - Outage: follow the [OPERATIONS-RUNBOOK.md](OPERATIONS-RUNBOOK.md) recovery steps.
   - Preserve evidence (logs, database snapshot) **before** destructive cleanup.
4. **Eradicate:** remove the root cause (patch the plugin, close the path, fix the configuration).
5. **Recover:** restore from a known-good backup if integrity is in doubt ([BACKUP-AND-DISASTER-RECOVERY.md](BACKUP-AND-DISASTER-RECOVERY.md)); verify with the public checks; confirm local/live parity.
6. **Notify:** apply the legal decision tree in section 4.
7. **Review:** blameless post-incident review within 5 business days (template in section 5). Add a row to [DEFECT-LOG.md](../DEFECT-LOG.md) if a quality gate should have caught the problem.

## 4. Personal-data breach decision tree

The demonstration intentionally collects almost no personal data (see [legal/COOKIES-AND-STORAGE.md](legal/COOKIES-AND-STORAGE.md)). Administrator accounts, server logs and CDN metadata still exist, so this process applies.

| Question | If yes |
|---|---|
| Were personal data accessed, disclosed, altered, lost or made unavailable without authorization? | Treat it as a potential personal-data breach; record the facts and the decision either way. |
| Is the operator subject to the GDPR or UK GDPR for the affected data? | Assess whether the breach is likely to result in a risk to individuals. If so, notify the competent supervisory authority **without undue delay and, where feasible, within 72 hours** of becoming aware. If the risk is high, also inform the affected individuals. |
| Are US residents' data affected? | Assess state breach-notification laws for the affected residents' states (timelines and thresholds vary). |
| Are identifiable health records involved (only possible if a future feature collects them)? | Assess the HIPAA Breach Notification Rule (covered entities/business associates) or the FTC Health Breach Notification Rule (non-HIPAA personal health records). |
| Is the operator established in Bangladesh or otherwise subject to its personal data protection law (the 2025 Ordinance, reported to be replaced by a 2026 Act; not verified against the official gazette)? | Assess its notification duties with local counsel; the regime is phasing in. |
| Is a processor (host, CDN) the source? | Obtain their incident report under the contract terms. |

This table routes decisions; it is not legal advice. Obtain qualified counsel for any real breach.

## 5. Post-incident review template

```
### Incident: <title>  (SEV-n)
- Timeline (UTC): detected / acknowledged / mitigated / resolved
- Impact: users/pages affected, duration, error-budget minutes consumed
- Root cause:
- What went well / what went poorly:
- Corrective actions (owner, due date):
- Gate that should have caught it; gate added?:
- Notifications made (authority / individuals / none, with reasoning):
```

## 6. Contacts

- Security reports: see [SECURITY.md](../SECURITY.md).
- Provider escalation paths (CDN, host, registrar) are kept in the private operations record, not in this public repository.
