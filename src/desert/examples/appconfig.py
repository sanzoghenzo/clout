#!/usr/bin/env python3

import dataclasses
import os
import pathlib
import typing as t

import attr
import click

from .. import encoders
from .. import loaders
from ..encoders import toml
from ..loaders import appfile
from ..loaders import cli
from ..loaders import env
from ..loaders import multi


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


config_file = pathlib.Path.home() / ".config/myapp/config.toml"
config_file.parent.mkdir(exist_ok=True)
config_file.write_text(
    """\
logging = true
priority = 3
"""
)


os.environ["MYAPP_CONFIG_DRY_RUN"] = "1"


multi = loaders.multi.Multi(
    [
        loaders.cli.CLI(),
        loaders.env.Env(),
        loaders.appfile.AppFile(encoders.toml.TOML(), filename="config.toml"),
    ],
    data=dict(app_name="myapp"),
)


print(multi.build(Config))

# $ myapp config  --debug db --host example.com --port 9999
# Config(db=DB(host='example.com', port=9999), debug=True, priority=3.0, logging=True, dry_run=True)
