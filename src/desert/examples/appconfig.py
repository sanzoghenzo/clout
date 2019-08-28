#!/usr/bin/env python3

import os
import pathlib
import typing as t
from dataclasses import dataclass

from .. import encoders
from .. import loaders
from ..encoders import toml
from ..loaders import appfile
from ..loaders import cli
from ..loaders import env
from ..loaders import multi


@dataclass
class DB:
    host: str
    port: int


@dataclass
class Config:
    db: DB
    debug: bool
    priority: int = 0
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
