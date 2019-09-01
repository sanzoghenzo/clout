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
CONFIG_FILE_DATA = toml.loads(
    pathlib.Path(appdirs.user_config_dir(APP_NAME)).joinpath("config.toml").read_text()
)
ENVVAR_DATA = desert.loaders.env.Env(app_name=APP_NAME).prep(Config, name=CONFIG_NAME)
DEFAULT_MAP = desert.loaders.multi.DeepChainMap(ENVVAR_DATA, CONFIG_FILE_DATA)
CONTEXT_SETTINGS = dict(default_map=DEFAULT_MAP)

commands = [
    desert.loaders.cli.DesertCommand(
        "run", type=Config, context_settings=CONTEXT_SETTINGS
    )
]
cli = click.Group(commands={c.name: c for c in commands})

got = cli.main(standalone_mode=False)
print(got)

# $ MYAPP_CONFIG_PRIORITY=7 minicli run config --debug  user --name Alice db --host example.com --port 9999 user --name Bob
# Config(db=DB(host='example.com', port=9999, user=User(name='Bob')), debug=True, user=User(name='Alice'), priority=7.0, logging=True, dry_run=True)
