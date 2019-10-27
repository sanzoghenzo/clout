import pathlib

import appdirs
import attr
import click
import toml

import clout


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
            "clout": {
                "cli": dict(param_decls=["--priority"], help="App priority value")
            }
        },
    )
    logging: bool = True
    dry_run: bool = False


APP_NAME = "myapp"


# Read config file.
config_file_path = pathlib.Path(appdirs.user_config_dir(APP_NAME)) / "config.toml"
try:
    config_file_text = config_file_path.read_text()
except FileNotFoundError:
    CONFIG_FILE_DATA = {}
else:
    CONFIG_FILE_DATA = toml.loads(config_file_text)


# Read from environment_variables prefixed `MYAPP_`,
# such as MYAPP_PRIORITY=10.
ENVVAR_DATA = clout.load_env(Config, prefix=APP_NAME)


# Combine config file and envvars to set CLI defaults.
CONTEXT_SETTINGS = dict(default_map=clout.DeepChainMap(ENVVAR_DATA, CONFIG_FILE_DATA))

# Define the CLI.
commands = [
    clout.Command(
        name="run",
        type=Config,
        context_settings=CONTEXT_SETTINGS,
        help="Run the app with given configuration object.",
    )
]
cli = click.Group(commands={c.name: c for c in commands})


if __name__ == "__main__":
    # Run the CLI.
    print(cli.main(standalone_mode=False))
