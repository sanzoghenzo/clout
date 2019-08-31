#!/usr/bin/env python3

import os
import pathlib

import attr
import click

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


cli = click.Group(commands={"run": desert.loaders.cli.class_cli_command(Config)})

got = cli.main(standalone_mode=False)

print(got)


# $ appconfig  run myapp --debug  user --name Alice db --host example.com --port 9999 user --name Bob
# Config(db=DB(host='example.com', port=9999, user=User(name='Bob')), debug=True, user=User(name='Alice'), priority=0, logging=True, dry_run=False)
