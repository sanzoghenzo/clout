import pathlib

import appdirs
import attr
import click
import toml

# XXX Should this be renamed to something like `click_dataclass`?
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
# XXX Would it be better as `MYAPP_PRIORITY` without inferring basd on the class name?
ENVVAR_DATA = clout.load_env(Config, prefix=APP_NAME)


# Combine config file and envvars to set CLI defaults.
# XXX make a function `combine()` or `chain()`?
# XXX Is it safe to combine like this? What if you *wanted* to have an empty dict as the value,
# but it got replaced with a lower-priority value?
CONTEXT_SETTINGS = dict(default_map=clout.DeepChainMap(ENVVAR_DATA, CONFIG_FILE_DATA))

# Define the CLI.
commands = [
    clout.Command(
        "run",
        type=Config,
        context_settings=CONTEXT_SETTINGS,
        help="Run the app with given configuration object.",
    )
]
cli = click.Group(commands={c.name: c for c in commands})


if __name__ == "__main__":
    # Run the CLI.
    print(cli.main(standalone_mode=False))
