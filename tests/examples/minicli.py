#!/usr/bin/env python3

import pathlib

import appdirs
import attr
import click
import toml

import desert.loaders.cli
import desert.loaders.env
import desert.loaders.multi


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
CONFIG_NAME = "config"

# Read config file.
CONFIG_FILE_PATH = pathlib.Path(appdirs.user_config_dir(APP_NAME)) / "config.toml"
CONFIG_FILE_DATA = toml.loads(CONFIG_FILE_PATH.read_text())

# Read from environment_variables prefixed `MYAPP_CONFIG_`.
# XXX How to make this simpler?
# Provide a `prefix=` argument? If it's `desert.load_env(Config, prefix=)`, then how to
# provide the app name and config name separately? Is that useful?
ENVVAR_DATA = desert.loaders.env.Env(app_name=APP_NAME).prep(Config, name=CONFIG_NAME)

# Combine config file and envvars to set CLI defaults.
# XXX make a function `desert.combine()`?
CONTEXT_SETTINGS = dict(
    default_map=desert.loaders.multi.DeepChainMap(ENVVAR_DATA, CONFIG_FILE_DATA)
)

# Define the CLI.
# XXX Should it just be called `desert.Command()`?
commands = [
    desert.loaders.cli.DesertCommand(
        "run",
        type=Config,
        context_settings=CONTEXT_SETTINGS,
        help="Run the app with given configuration object.",
    )
]

# XXX Define `desert.Group()` overriding the constructor to take a `commands` list?
cli = click.Group(commands={c.name: c for c in commands})

# Run the CLI.
got = cli.main(standalone_mode=False)
print(got)

# $ MYAPP_CONFIG_PRIORITY=7 minicli run config --debug  user --name Alice db --host example.com --port 9999 user --name Bob
# Config(db=DB(host='example.com', port=9999, user=User(name='Bob')), debug=True, user=User(name='Alice'), priority=7.0, logging=True, dry_run=True)
