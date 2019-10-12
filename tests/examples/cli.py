#!/usr/bin/env python3

import attr
import click

import clout.loaders.cli


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


cli = click.Group(commands={"run": clout.loaders.cli.class_cli_command(Config)})

got = cli.main(standalone_mode=False)

print(got)


# $ cli run config --debug  user --name Alice db --host example.com --port 9999 user --name Bob
# Config(db=DB(host='example.com', port=9999, user=User(name='Bob')), debug=True, user=User(name='Alice'), priority=0, logging=True, dry_run=False)
