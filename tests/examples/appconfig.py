#!/usr/bin/env python3

import os
import pathlib

import attr

import desert.encoders.toml
import desert.loaders.appfile
import desert.loaders.cli
import desert.loaders.env
import desert.loaders.multi
import desert.loaders.resource
from desert import encoders
from desert import loaders
from desert import runner

from .. import examples


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


def dance_(config):
    print("Dancing with config:\n", config)


def sing_(config):
    print("Singing with config:\n", config)


@attr.dataclass
class App:
    dance: Config = dance_
    sing: Config = lambda c=None: sing_


multi = loaders.multi.Multi(
    [
        loaders.cli.CLI(),
        loaders.env.Env(),
        loaders.resource.Resource(
            desert.encoders.toml.TOML(), examples, "appconfig.toml"
        ),
        loaders.appfile.AppFile(
            desert.encoders.toml.TOML(), path=os.environ["TEST_CONFIG_PATH"]
        ),
    ],
    data=dict(app_name="myapp"),
)

built = multi.build(App)
runner.run(built)
