import attr
import click

import clout


@attr.dataclass
class DB:
    host: str
    port: int


@attr.dataclass
class Config:
    db: DB
    dry_run: bool


cli = clout.Command(type=Config)

if __name__ == "__main__":
    print(cli.build())
