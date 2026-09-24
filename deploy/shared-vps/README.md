# Static rollback container

**Status: Retained as the rollback target.** It served the static Neural Frontier release before the native WordPress cutover. It is kept so routing can fall back to a known-good static site.

| File | Purpose |
|---|---|
| `compose.yaml` | One NGINX container: digest-pinned image, non-root, read-only filesystem, all capabilities dropped, `no-new-privileges`, loopback-only port, 128 MiB / 0.5 CPU / 100 PID limits, health check |
| `nginx.conf` | Static serving with temp paths in tmpfs and `server_tokens off` |
| `site.caddy` | Host TLS router entry for the project hostname only |
| `.env.example` | Image digest and reserved loopback port (no secrets) |

The site content (`./site`) is a built release copied at deploy time and is not committed. Deployment and rollback steps are in [docs/OPERATIONS-RUNBOOK.md](../../docs/OPERATIONS-RUNBOOK.md).
