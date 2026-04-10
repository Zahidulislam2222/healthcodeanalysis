"""
Site Cloning via cPanel API / Softaculous.
Clones a WordPress template site to a new domain on the same cPanel account.

Usage:
    python clone_site.py --source healthcodeanalysis.com --target newcustomer.com [--dry-run]
"""

import argparse
import json
import os
import sys
from pathlib import Path

try:
    import requests
except ImportError:
    print("ERROR: 'requests' package required. Install with: pip install requests")
    sys.exit(1)


class CPanelClient:
    """cPanel UAPI client for site management."""

    def __init__(self, url=None, username=None, api_token=None, dry_run=False):
        self.url = (url or os.getenv("CPANEL_URL", "")).rstrip("/")
        self.username = username or os.getenv("CPANEL_USERNAME", "")
        self.api_token = api_token or os.getenv("CPANEL_API_TOKEN", "")
        self.dry_run = dry_run
        self.session = requests.Session()

        if self.username and self.api_token:
            self.session.headers.update(
                {
                    "Authorization": f"cpanel {self.username}:{self.api_token}",
                }
            )

    def _uapi(self, module, function, params=None):
        """Call cPanel UAPI endpoint."""
        url = f"{self.url}/execute/{module}/{function}"
        if self.dry_run:
            return {
                "dry_run": True,
                "url": url,
                "params": params,
                "status": 1,
                "data": None,
            }
        resp = self.session.get(url, params=params or {}, timeout=30, verify=True)
        if resp.status_code != 200:
            raise RuntimeError(f"cPanel API error ({resp.status_code}): {resp.text[:300]}")
        return resp.json()

    def list_domains(self):
        """List all domains on the cPanel account."""
        return self._uapi("DomainInfo", "list_domains")

    def list_databases(self):
        """List all MySQL databases."""
        return self._uapi("Mysql", "list_databases")

    def create_database(self, db_name):
        """Create a new MySQL database."""
        return self._uapi("Mysql", "create_database", {"name": db_name})

    def create_db_user(self, username, password):
        """Create a new MySQL user."""
        return self._uapi("Mysql", "create_user", {"name": username, "password": password})

    def set_privileges(self, db_name, db_user):
        """Grant all privileges to user on database."""
        return self._uapi(
            "Mysql",
            "set_privileges_on_database",
            {
                "user": db_user,
                "database": db_name,
                "privileges": "ALL PRIVILEGES",
            },
        )

    def list_installed_apps(self):
        """List WordPress installs via Softaculous (if available)."""
        if self.dry_run:
            return {"dry_run": True, "action": "list_installed_apps"}
        # Softaculous API endpoint
        url = f"{self.url}/frontend/starter/softaculous/index.live.php"
        resp = self.session.get(url, params={"act": "installations", "api": "json"}, timeout=30)
        if resp.status_code == 200:
            try:
                return resp.json()
            except json.JSONDecodeError:
                return {"error": "Softaculous not available or returned non-JSON"}
        return {"error": f"HTTP {resp.status_code}"}


class SiteCloner:
    """Clone a WordPress site to a new domain."""

    def __init__(self, cpanel: CPanelClient, verbose=True):
        self.cpanel = cpanel
        self.verbose = verbose

    def log(self, msg):
        if self.verbose:
            print(f"  {msg}")

    def clone(self, source_domain, target_domain, target_db_name=None, target_db_user=None, target_db_pass=None):
        """
        Clone a WordPress site from source to target domain.

        Steps:
        1. Create new database + user
        2. Copy files from source to target document root
        3. Import database with search-replace
        4. Update wp-config.php

        Returns dict with results.
        """
        results = {}

        # Generate DB credentials if not provided
        if not target_db_name:
            short = target_domain.replace(".", "").replace("-", "")[:8]
            target_db_name = f"{self.cpanel.username}_{short}"
        if not target_db_user:
            target_db_user = target_db_name
        if not target_db_pass:
            import secrets

            target_db_pass = secrets.token_urlsafe(16)

        self.log(f"[CLONE] {source_domain} -> {target_domain}")
        self.log(f"[DB] {target_db_name} / {target_db_user}")

        # Step 1: Create database
        self.log("[STEP 1] Creating database...")
        result = self.cpanel.create_database(target_db_name)
        results["create_db"] = result

        # Step 2: Create DB user
        self.log("[STEP 2] Creating database user...")
        result = self.cpanel.create_db_user(target_db_user, target_db_pass)
        results["create_user"] = result

        # Step 3: Grant privileges
        self.log("[STEP 3] Granting privileges...")
        result = self.cpanel.set_privileges(target_db_name, target_db_user)
        results["set_privileges"] = result

        # Step 4: Generate WP-CLI commands for the user to run
        # (We don't execute these directly — user runs them via SSH or cPanel Terminal)
        commands = self._generate_clone_commands(
            source_domain,
            target_domain,
            target_db_name,
            target_db_user,
            target_db_pass,
        )
        results["commands"] = commands

        self.log("")
        self.log("[READY] Database created. Run these commands on the server:")
        self.log("")
        for cmd in commands:
            self.log(f"  $ {cmd}")

        return results

    def _generate_clone_commands(self, source, target, db_name, db_user, db_pass):
        """Generate shell commands for server-side execution."""
        cpanel_user = self.cpanel.username
        # Main domain uses public_html; addon domains go under public_html/domain
        source_path = f"/home/{cpanel_user}/public_html"
        target_path = f"/home/{cpanel_user}/{target}"

        commands = [
            "# Step 1: Copy WordPress files",
            f"cp -r {source_path} {target_path}",
            "",
            "# Step 2: Export source database",
            f"wp db export /tmp/{source.replace('.', '_')}_dump.sql --path={source_path}",
            "",
            "# Step 3: Update wp-config.php for new database",
            f'DB_PASS="{db_pass}"',
            f"sed -i \"s/define.*DB_NAME.*/define('DB_NAME', '{db_name}');/\" {target_path}/wp-config.php",
            f"sed -i \"s/define.*DB_USER.*/define('DB_USER', '{db_user}');/\" {target_path}/wp-config.php",
            f"sed -i \"s/define.*DB_PASSWORD.*/define('DB_PASSWORD', '$DB_PASS');/\" {target_path}/wp-config.php",
            'unset DB_PASS',
            "",
            "# Step 4: Import database to new DB",
            f"wp db import /tmp/{source.replace('.', '_')}_dump.sql --path={target_path}",
            "",
            "# Step 5: Search-replace domain in database",
            f"wp search-replace '{source}' '{target}' --path={target_path} --all-tables",
            "",
            "# Step 6: Flush permalinks and cache",
            f"wp rewrite flush --path={target_path}",
            f"wp cache flush --path={target_path}",
            "",
            "# Step 7: Clean up",
            f"rm /tmp/{source.replace('.', '_')}_dump.sql",
        ]
        return commands

    def generate_full_pipeline_script(
        self, source_domain, target_domain, config_path, db_name=None, db_user=None, db_pass=None
    ):
        """
        Generate a complete bash script that:
        1. Clones the site
        2. Runs deploy_customer.py to swap content

        Returns the script as a string.
        """
        if not db_name:
            short = target_domain.replace(".", "").replace("-", "")[:8]
            db_name = f"{self.cpanel.username}_{short}"
        if not db_user:
            db_user = db_name
        if not db_pass:
            import secrets

            db_pass = secrets.token_urlsafe(16)

        cpanel_user = self.cpanel.username
        # Main domain uses public_html; addon domains go under public_html/domain
        source_path = f"/home/{cpanel_user}/public_html"
        target_path = f"/home/{cpanel_user}/{target_domain}"

        script = f"""#!/bin/bash
# ============================================================
# Full Deployment Pipeline: {target_domain}
# Generated by HealthCode Analysis Automation
# ============================================================

set -e  # Exit on error

SOURCE_DOMAIN="{source_domain}"
TARGET_DOMAIN="{target_domain}"
SOURCE_PATH="{source_path}"
TARGET_PATH="{target_path}"
DB_NAME="{db_name}"
DB_USER="{db_user}"
DB_PASS="{db_pass}"

echo "=== Step 1: Clone WordPress Files ==="
cp -r "$SOURCE_PATH" "$TARGET_PATH"
echo "Files copied."

echo "=== Step 2: Create Database ==="
# Database should already be created via cPanel API
# If not, uncomment: mysql -e "CREATE DATABASE $DB_NAME;"

echo "=== Step 3: Update wp-config.php ==="
sed -i "s/define.*DB_NAME.*/define('DB_NAME', '$DB_NAME');/" "$TARGET_PATH/wp-config.php"
sed -i "s/define.*DB_USER.*/define('DB_USER', '$DB_USER');/" "$TARGET_PATH/wp-config.php"
sed -i "s/define.*DB_PASSWORD.*/define('DB_PASSWORD', '$DB_PASS');/" "$TARGET_PATH/wp-config.php"
echo "wp-config.php updated."

echo "=== Step 4: Export & Import Database ==="
wp db export /tmp/source_dump.sql --path="$SOURCE_PATH"
wp db import /tmp/source_dump.sql --path="$TARGET_PATH"
rm /tmp/source_dump.sql
echo "Database imported."

echo "=== Step 5: Search-Replace Domain ==="
wp search-replace "$SOURCE_DOMAIN" "$TARGET_DOMAIN" --path="$TARGET_PATH" --all-tables
echo "Domain replaced."

echo "=== Step 6: Flush Caches ==="
wp rewrite flush --path="$TARGET_PATH"
wp cache flush --path="$TARGET_PATH"
unset DB_PASS
echo "Caches flushed."

echo "=== Step 7: Swap Content via API ==="
echo "Now run from your local machine:"
echo "  python scripts/deploy_customer.py {config_path} --site-url https://$TARGET_DOMAIN"

echo ""
echo "=== DONE ==="
echo "Site cloned to: https://$TARGET_DOMAIN"
"""
        return script


def main():
    parser = argparse.ArgumentParser(description="Clone WordPress site via cPanel")
    parser.add_argument("--source", required=True, help="Source domain to clone from")
    parser.add_argument("--target", required=True, help="Target domain to clone to")
    parser.add_argument("--config", help="Customer config JSON for content swap after clone")
    parser.add_argument("--db-name", help="Target database name")
    parser.add_argument("--db-user", help="Target database user")
    parser.add_argument("--db-pass", help="Target database password")
    parser.add_argument("--dry-run", action="store_true", help="Preview without changes")
    parser.add_argument("--generate-script", action="store_true", help="Generate bash script instead of executing")
    parser.add_argument("--output", help="Output file for generated script")

    args = parser.parse_args()

    # Load env
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    os.environ.setdefault(key.strip(), val.strip().strip('"'))

    cpanel = CPanelClient(dry_run=args.dry_run)
    cloner = SiteCloner(cpanel)

    if args.generate_script:
        script = cloner.generate_full_pipeline_script(
            args.source,
            args.target,
            args.config or f"configs/customer-{args.target.split('.')[0]}.json",
            args.db_name,
            args.db_user,
            args.db_pass,
        )
        if args.output:
            with open(args.output, "w") as f:
                f.write(script)
            print(f"Script written to: {args.output}")
        else:
            print(script)
    else:
        results = cloner.clone(
            args.source,
            args.target,
            args.db_name,
            args.db_user,
            args.db_pass,
        )
        print(json.dumps(results, indent=2, default=str))


if __name__ == "__main__":
    main()
