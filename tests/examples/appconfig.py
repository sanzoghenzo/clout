#!/usr/bin/env python3

import os
import pathlib

import attr

import clout.encoders.toml
import clout.loaders.appfile
import clout.loaders.cli
import clout.loaders.env
import clout.loaders.multi
import clout.loaders.resource
from clout import encoders
from clout import loaders
from clout import runner

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
            "clout": {
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
    dance: Config = dance_  # type: ignore
    sing: Config = lambda c=None: sing_  # type: ignore


multi = loaders.multi.Multi(
    [
        loaders.cli.CLI(),
        loaders.env.Env(),
        loaders.resource.Resource(
            clout.encoders.toml.TOML(), examples, "appconfig.toml"
        ),
        loaders.appfile.AppFile(
            clout.encoders.toml.TOML(), path=os.environ["TEST_CONFIG_PATH"]
        ),
    ],
    data=dict(app_name="myapp"),
)

built = multi.build(App)
runner.run(built)
