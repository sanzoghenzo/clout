#!/usr/bin/env python3

import dataclasses
import os
import pathlib
import typing as t

import attr
import click

import desert.encoders.toml
import desert.loaders.appfile
import desert.loaders.cli
import desert.loaders.env
import desert.loaders.multi
from desert import encoders
from desert import loaders
from desert import runner


@attr.dataclass
class DB:
    host: str
    port: int


@attr.dataclass
class Config:
    db: DB
    debug: bool
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


def dance_(config):
    print("Dancing with config:", config)


def sing_(config):
    print("Singing with config:", config)


@attr.dataclass
class App:
    dance: Config = dance_
    sing: Config = sing_


config_file = pathlib.Path.home() / ".config/myapp/config.toml"
config_file.parent.mkdir(exist_ok=True)
config_file.write_text(
    """\
[dance]
logging = true
priority = 3
"""
)


os.environ["MYAPP_APP_DANCE_DRY_RUN"] = "1"


multi = loaders.multi.Multi(
    [
        loaders.cli.CLI(),
        loaders.env.Env(),
        loaders.appfile.AppFile(desert.encoders.toml.TOML(), filename="config.toml"),
    ],
    data=dict(app_name="myapp"),
)

built = multi.build(App)
runner.run(built)


# examples/appconfig.py app dance   --debug db --host example.com --port 9999
# Dancing with config: Config(db=DB(host='example.com', port=9999), debug=True, priority=3.0, logging=True, dry_run=True)
