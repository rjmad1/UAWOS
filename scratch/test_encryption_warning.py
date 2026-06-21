import os
import subprocess
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
python_exe = sys.executable


def test_warning_when_key_absent():
    env = os.environ.copy()
    if "UAWOS_ENCRYPTION_KEY" in env:
        del env["UAWOS_ENCRYPTION_KEY"]

    cmd = [python_exe, "-c", "import uawos_integrations"]
    res = subprocess.run(cmd, capture_output=True, text=True, env=env, cwd=project_root)

    assert "WARNING: UAWOS_ENCRYPTION_KEY environment variable is not set" in res.stderr
    assert "THIS IS INSECURE FOR PRODUCTION" in res.stderr


def test_no_warning_when_key_present():
    env = os.environ.copy()
    import cryptography.fernet

    # Generate a valid Fernet key
    key = cryptography.fernet.Fernet.generate_key().decode()
    env["UAWOS_ENCRYPTION_KEY"] = key

    cmd = [python_exe, "-c", "import uawos_integrations"]
    res = subprocess.run(cmd, capture_output=True, text=True, env=env, cwd=project_root)

    assert "WARNING: UAWOS_ENCRYPTION_KEY" not in res.stderr


if __name__ == "__main__":
    test_warning_when_key_absent()
    test_no_warning_when_key_present()
    print("Symmetric key fallback warning verification tests passed successfully!")
