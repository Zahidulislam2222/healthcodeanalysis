# Local WordPress stack (retained)

**Status: Retained.** This is the original local development stack for the automation toolkit in `scripts/`. The current native release uses [`wordpress-native/compose.yaml`](../wordpress-native/compose.yaml) instead.

| Service | Purpose | Local address |
|---|---|---|
| `wordpress` | WordPress with the original plugin set | <http://localhost:8889> |
| `db` | MySQL 8.0 | host port 3307 |
| `phpmyadmin` | Database admin UI | <http://localhost:8082> |
| `cloudflared` | **Optional** demo tunnel (`demo-tunnel` profile) | — |

```bash
cd docker
cp .env.docker.sample .env             # Compose reads .env from this folder; set local-only passwords
docker compose up -d                   # no public tunnel
bash setup.sh                          # installs WP-CLI and the plugins, activates the API bridge
```

**Do not start the tunnel** (`docker compose --profile demo-tunnel up -d cloudflared`) unless the WordPress admin is protected by an access policy such as Cloudflare Access. Otherwise a local admin is exposed to the internet.

The compose file publishes ports on all host interfaces (for example `3307:3306`), and the sample passwords are weak defaults. Use it only on a trusted machine behind a firewall, or change the mappings to `127.0.0.1:…`. Never reuse the local passwords anywhere else.
