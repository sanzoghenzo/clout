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
class AppConfig:
    db: DB
    debug: bool
    logging: bool = True
    dry_run: bool = False
    level: int = 4


config_file = pathlib.Path.home() / ".config/myapp/config.toml"
config_file.parent.mkdir(exist_ok=True)
config_file.write_text(
    """\
[db]
host= "example.com"
port= 9999
"""
)


os.environ["APP_CONFIG_DRY_RUN"] = "1"


multi = loaders.multi.Multi(
    [
        loaders.cli.CLI(),
        loaders.env.Env(),
        loaders.appfile.AppFile(encoders.toml.TOML(), filename="config.toml"),
    ],
    data=dict(app_name="myapp"),
)


print(multi.build(AppConfig))


# $ appconfig.py owner cat --claws=long
# Owner(name='Alice', dog=Dog(coat=Coat(color='brown')), cat=Cat(claws='long'), age=21)
