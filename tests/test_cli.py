import subprocess
import sys


def test_non_standalone_cli():
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
        [sys.executable, "-m", "tests.examples.cli"] + args,
        capture_output=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr.decode()

    output = proc.stdout.decode()
    expected = "Config(db=DB(host='example.com', port=9999, user=User(name='Bob')), debug=True, user=User(name='Alice'), priority=3.0, logging=True, dry_run=True)\n"
    assert output == expected
