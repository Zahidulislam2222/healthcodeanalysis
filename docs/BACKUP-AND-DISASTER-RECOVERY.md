# Backup and disaster recovery

**Status:** backup and isolated restore are **verified** for the current release. Scheduled automated backups, off-site retention policy enforcement and timed RTO/RPO drills are **planned** (roadmap Phase 1).

## 1. What must be recoverable

| Data | Source of truth | Backup method |
|---|---|---|
| Application code and configuration | Git repository | Git history on GitHub plus local clones. |
| Page content, layouts, users, settings | WordPress database | SQL dump taken with authoring writes stopped. |
| Uploads and media | WordPress content volume | Archive of the content volume. |
| Release artifacts | Versioned release directory | 141-file SHA256 manifest; the prior release is retained on the host. |
| Routing configuration | Project-scoped Caddy site file | Previous version retained; automatic restore on failed activation. |
| Secrets | Private credential store (not Git) | Kept in the private recovery record; rotated after incidents. |

## 2. Evidence to date

- A fresh SQL + content snapshot was restored on a separate isolated server runtime: 68 published pages and 156 valid Elementor layouts; public interactions, film, MFA and the native editor worked on the restored copy.
- The production transition saved a database backup before applying the prepared export.
- Routing rollback to the retained static release is built into activation.
- Database readiness requires an authenticated TCP query, so a temporary initialization server cannot pass as ready.

## 3. Recovery objectives (proposed)

| Scenario | RPO (data loss) | RTO (time to restore) |
|---|---|---|
| Bad deploy / broken layout | 0 (roll back release) | 30 minutes |
| Database corruption | Last backup (target ≤ 24 h) | 4 hours |
| Host loss | Last off-site backup (target ≤ 24 h) | 24 hours on replacement infrastructure |
| CDN/DNS misconfiguration | 0 | 1 hour |

These are proposals. They become commitments only after two consecutive timed drills meet them.

## 4. Backup policy (target state)

- **3-2-1:** three copies, two media types, one off-site and access-separated from the production host.
- **Frequency:** daily database dump; content volume daily or after each publish; before every deploy or plugin update.
- **Retention:** 7 daily, 4 weekly, 3 monthly.
- **Integrity:** checksum every archive; encrypt off-site copies; restrict access to named operators.
- **Privacy:** backups contain administrator account data. Apply the same retention and deletion rules as the live system.

## 5. Restore procedure (summary)

1. Declare the incident and freeze authoring ([INCIDENT-RESPONSE.md](INCIDENT-RESPONSE.md)).
2. Select the newest backup that predates the problem; verify its checksum.
3. Restore into an **isolated** runtime first, never directly over production.
4. Verify: page count, Elementor layout validity, MFA login, editor opens, public browser scenarios, HTTP security checks.
5. Compare editable facts with the last known-good state.
6. Activate routing to the restored runtime; the previous configuration is retained for rollback.
7. Invalidate the gateway cache and regenerate Elementor CSS together.
8. Confirm local/live SHA256 parity; record timings to measure actual RTO/RPO.

## 6. Drill schedule (planned)

Run a quarterly restore drill, and another after any major version upgrade. Each drill records backup age, restore duration, the checks passed and the issues found.
