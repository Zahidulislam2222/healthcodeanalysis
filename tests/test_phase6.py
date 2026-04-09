"""
Phase 6 Tests: Site cloning automation (cPanel API, script generation).
All tests run in dry-run mode.
"""

import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from clone_site import CPanelClient, SiteCloner

PASSED = 0
FAILED = 0


def test(name, condition, detail=""):
    global PASSED, FAILED
    if condition:
        PASSED += 1
        print(f"  PASS: {name}")
    else:
        FAILED += 1
        print(f"  FAIL: {name} {detail}")


def test_cpanel_client_init():
    """Test cPanel client initialization."""
    print("\n=== Test: CPanelClient Init ===")
    client = CPanelClient(
        url="https://server.com:2083",
        username="testuser",
        api_token="testtoken",
        dry_run=True,
    )
    test("URL set", client.url == "https://server.com:2083")
    test("Username set", client.username == "testuser")
    test("Dry run mode", client.dry_run is True)


def test_cpanel_uapi_dry_run():
    """Test cPanel UAPI calls in dry-run mode."""
    print("\n=== Test: CPanelClient UAPI (dry-run) ===")
    client = CPanelClient(url="https://server.com:2083", username="testuser", dry_run=True)

    result = client.list_domains()
    test("List domains returns dry_run", result.get("dry_run") is True)
    test("List domains has URL", "DomainInfo" in result.get("url", ""))

    result = client.create_database("testuser_newdb")
    test("Create DB returns dry_run", result.get("dry_run") is True)
    test("Create DB has params", result["params"]["name"] == "testuser_newdb")

    result = client.create_db_user("testuser_newdb", "password123")
    test("Create user returns dry_run", result.get("dry_run") is True)

    result = client.set_privileges("testuser_newdb", "testuser_newdb")
    test("Set privileges returns dry_run", result.get("dry_run") is True)


def test_site_cloner_clone():
    """Test site cloning in dry-run."""
    print("\n=== Test: SiteCloner.clone (dry-run) ===")
    client = CPanelClient(url="https://server.com:2083", username="mehzsolu", dry_run=True)
    cloner = SiteCloner(client, verbose=False)

    results = cloner.clone(
        source_domain="healthcodeanalysis.com",
        target_domain="newcustomer.com",
        target_db_name="mehzsolu_newcust",
        target_db_user="mehzsolu_newcust",
        target_db_pass="securepass123",
    )

    test("Returns results dict", isinstance(results, dict))
    test("Has create_db", "create_db" in results)
    test("Has create_user", "create_user" in results)
    test("Has set_privileges", "set_privileges" in results)
    test("Has commands list", "commands" in results)
    test("Commands include cp", any("cp -r" in cmd for cmd in results["commands"]))
    test("Commands include search-replace", any("search-replace" in cmd for cmd in results["commands"]))
    test("Commands reference source domain", any("healthcodeanalysis.com" in cmd for cmd in results["commands"]))
    test("Commands reference target domain", any("newcustomer.com" in cmd for cmd in results["commands"]))
    test("Commands reference mehzsolu path", any("mehzsolu" in cmd for cmd in results["commands"]))


def test_site_cloner_auto_db_name():
    """Test automatic DB name generation."""
    print("\n=== Test: SiteCloner auto DB name ===")
    client = CPanelClient(url="https://server.com:2083", username="mehzsolu", dry_run=True)
    cloner = SiteCloner(client, verbose=False)

    results = cloner.clone("healthcodeanalysis.com", "customer-site.com")
    commands = results["commands"]
    commands_str = "\n".join(commands)

    test("Auto-generated DB name present", "mehzsolu_" in commands_str)
    test("Commands are non-empty", len(commands) > 5)


def test_generate_full_pipeline_script():
    """Test full pipeline bash script generation."""
    print("\n=== Test: SiteCloner pipeline script ===")
    client = CPanelClient(url="https://server.com:2083", username="mehzsolu", dry_run=True)
    cloner = SiteCloner(client, verbose=False)

    script = cloner.generate_full_pipeline_script(
        source_domain="healthcodeanalysis.com",
        target_domain="newcustomer.com",
        config_path="configs/customer-newcustomer.json",
        db_name="mehzsolu_newcust",
        db_user="mehzsolu_newcust",
        db_pass="testpass123",
    )

    test("Script is a string", isinstance(script, str))
    test("Script has shebang", script.startswith("#!/bin/bash"))
    test("Script has set -e", "set -e" in script)
    test("Script has source domain", "healthcodeanalysis.com" in script)
    test("Script has target domain", "newcustomer.com" in script)
    test("Script has DB name", "mehzsolu_newcust" in script)
    test("Script has cp command", "cp -r" in script)
    test("Script has search-replace", "search-replace" in script)
    test("Script has wp-config update", "wp-config.php" in script)
    test("Script has cache flush", "cache flush" in script)
    test("Script references deploy_customer.py", "deploy_customer.py" in script)
    test("Script references config path", "configs/customer-newcustomer.json" in script)

    # Test file output
    with tempfile.NamedTemporaryFile(suffix=".sh", delete=False, mode="w") as f:
        f.write(script)
        tmp_path = f.name
    try:
        test("Script file created", os.path.exists(tmp_path))
        test("Script file non-empty", os.path.getsize(tmp_path) > 100)
    finally:
        os.unlink(tmp_path)


def test_clone_site_cli_dry_run():
    """Test clone_site.py CLI in dry-run mode."""
    print("\n=== Test: clone_site.py CLI (dry-run) ===")

    # Test --generate-script flag
    import subprocess

    result = subprocess.run(
        [
            sys.executable,
            "scripts/clone_site.py",
            "--source",
            "healthcodeanalysis.com",
            "--target",
            "newcustomer.com",
            "--dry-run",
            "--generate-script",
        ],
        capture_output=True,
        text=True,
        timeout=10,
        cwd=os.path.join(os.path.dirname(__file__), ".."),
    )
    test("CLI exits successfully", result.returncode == 0)
    test("CLI outputs bash script", "#!/bin/bash" in result.stdout)
    test("CLI has target domain", "newcustomer.com" in result.stdout)


if __name__ == "__main__":
    print("=" * 60)
    print("PHASE 6 TESTS")
    print("=" * 60)

    test_cpanel_client_init()
    test_cpanel_uapi_dry_run()
    test_site_cloner_clone()
    test_site_cloner_auto_db_name()
    test_generate_full_pipeline_script()
    test_clone_site_cli_dry_run()

    print()
    print("=" * 60)
    total = PASSED + FAILED
    print(f"RESULTS: {PASSED}/{total} passed, {FAILED} failed")
    print("=" * 60)

    sys.exit(0 if FAILED == 0 else 1)
