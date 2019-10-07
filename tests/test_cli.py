import subprocess
import sys


def test_long_example():
    """Build and run a non-standalone command using click."""
    args = [
        "run",
        "config",
        "--dry-run",
        "--debug",
        "--priority",
        "3",
        "user",
        "--name",
        "Alice",
        "db",
        "--host",
        "example.com",
        "--port",
        "9999",
        "user",
        "--name",
        "Bob",
    ]
    proc = subprocess.run(
        [sys.executable, "docs/long.py"] + args, capture_output=True, check=False
    )
    assert proc.returncode == 0, proc.stderr.decode()

    output = proc.stdout.decode()
    expected = "Config(db=DB(host='example.com', port=9999, user=User(name='Bob')), debug=True, user=User(name='Alice'), priority=3.0, logging=True, dry_run=True)\n"
    assert output == expected


def test_short_example():
    """Build and run a short command using click."""
    args = ["config", "--dry-run", "db", "--host", "example.com", "--port", "9999"]
    proc = subprocess.run(
        [sys.executable, "docs/short.py"] + args, capture_output=True, check=False
    )
    assert proc.returncode == 0, proc.stderr.decode()

    output = proc.stdout.decode()
    expected = "Config(db=DB(host='example.com', port=9999), dry_run=True)\n"

    assert output == expected
