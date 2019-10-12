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


cli = clout.Command("run", type=Config)

print(cli.build())


# $ myapp config --dry-run db --host example.com --port 9999
# Config(db=DB(host='example.com', port=9999), dry_run=True)
