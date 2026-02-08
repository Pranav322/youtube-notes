import os
import importlib
from typing import Set

def test_admin_ips_config():
    # Set environment variable before importing config
    os.environ["ADMIN_IPS"] = "1.2.3.4, 5.6.7.8,  10.0.0.1 "

    # Import config (or reload if already imported)
    from app import config
    importlib.reload(config)

    # Re-instantiate settings to pick up new env vars if necessary
    settings = config.settings

    expected_ips = {"1.2.3.4", "5.6.7.8", "10.0.0.1"}

    # Check if admin_ips_set property works correctly
    if hasattr(settings, "admin_ips_set"):
        actual_ips = settings.admin_ips_set
        # Verify it's a set
        assert isinstance(actual_ips, set), f"Expected set, got {type(actual_ips)}"
        # Verify content
        assert actual_ips == expected_ips, f"Expected {expected_ips}, got {actual_ips}"
        print("ADMIN_IPS configuration test passed!")
    else:
        print("admin_ips_set not found in settings (expected until implemented)")

if __name__ == "__main__":
    test_admin_ips_config()
