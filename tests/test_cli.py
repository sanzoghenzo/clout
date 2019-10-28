import os
import subprocess
import sys


def test_long_example():
    """Build and run a non-standalone command using click."""
    args = [
        "config",
        "--debug",
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
        [sys.executable, "docs/long.py"] + args,
        capture_output=True,
        check=False,
        env=dict(**{"MYAPP_PRIORITY": "2"}, **os.environ),
    )
    assert proc.returncode == 0, proc.stderr.decode()

    output = proc.stdout.decode()
    expected = "Config(db=DB(host='example.com', port=9999, user=User(name='Bob')), debug=True, user=User(name='Alice'), priority=2.0, logging=True, dry_run=True)\n"
    assert output == expected


def test_short_example():
    """Build and run a short command using click."""
    args = ["--dry-run", "db", "--host", "example.com", "--port", "9999"]
    proc = subprocess.run(
        [sys.executable, "docs/short.py"] + args, capture_output=True, check=False
    )
    assert proc.returncode == 0, proc.stderr.decode()

    output = proc.stdout.decode()
    expected = "Config(db=DB(host='example.com', port=9999), dry_run=True)\n"

    assert output == expected


def test_show_missing_args():
    """Show help for missing args."""
    args = ["--dry-run", "db"]
    proc = subprocess.run(
        [sys.executable, "docs/short.py"] + args, capture_output=True, check=False
    )
    assert proc.returncode == 0, proc.stderr.decode()

    output = proc.stdout.decode()
    assert output.startswith("Usage:")


def test_show_missing_data_args():
    """When validation fails for missing data, explain the problem to the user."""
    args = ["--dry-run", "db", "--port", "3"]
    proc = subprocess.run(
        [sys.executable, "docs/short.py"] + args, capture_output=True, check=False
    )
    assert proc.returncode == 1, proc.stderr.decode()

    assert "Missing data for required field" in proc.stderr.decode()
