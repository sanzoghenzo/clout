#!/usr/bin/env python3

import pathlib

import appdirs
import attr
import click
import toml

# XXX Should this be renamed to something like `click_dataclass`?
import desert


@attr.dataclass
class User:
    name: str


@attr.dataclass
class DB:
    host: str
    port: int
    user: User


@attr.dataclass
class Config:
    db: DB
    debug: bool
    user: User
    priority: float = attr.ib(
        default=0,
        metadata={
            "desert": {
                "cli": dict(param_decls=["--priority"], help="App priority value")
            }
        },
    )
    logging: bool = True
    dry_run: bool = False


APP_NAME = "myapp"


# Read config file.
# XXX This is a lot of boilerplate. Should this have a wrapper function?
config_file_path = pathlib.Path(appdirs.user_config_dir(APP_NAME)) / "config.toml"
try:
    config_file_text = config_file_path.read_text()
except FileNotFoundError:
    CONFIG_FILE_DATA = {}
else:
    CONFIG_FILE_DATA = toml.loads(config_file_text)


# Read from environment_variables prefixed `MYAPP_`,
# such as MYAPP_CONFIG_PRIORITY=10.
ENVVAR_DATA = desert.load_env(Config, prefix=f"{APP_NAME}")


# Combine config file and envvars to set CLI defaults.
# XXX make a function `desert.combine()`?
# XXX Is it safe to combine like this? What if you *wanted* to have an empty dict as the value,
# but it got replaced with a lower-priority value?
CONTEXT_SETTINGS = dict(default_map=desert.DeepChainMap(ENVVAR_DATA, CONFIG_FILE_DATA))

# Define the CLI.
commands = [
    desert.Command(
        "run",
        type=Config,
        context_settings=CONTEXT_SETTINGS,
        help="Run the app with given configuration object.",
    )
]
cli = click.Group(commands={c.name: c for c in commands})

# Run the CLI.
# XXX This is a bit of boilerplate. Should it get a wrapper function?
got = cli.main(standalone_mode=False)
print(got)

# $ cat ~/.config/myapp/config.toml
# [config]
# dry_run=true

# Run the script with an environment variable set.
# $ MYAPP_CONFIG_PRIORITY=7 minicli run config --debug  user --name Alice db --host example.com --port 9999 user --name Bob
# Config(db=DB(host='example.com', port=9999, user=User(name='Bob')), debug=True, user=User(name='Alice'), priority=7.0, logging=True, dry_run=True)
