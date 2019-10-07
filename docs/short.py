import attr
import click

import desert


@attr.dataclass
class DB:
    host: str
    port: int


@attr.dataclass
class Config:
    db: DB
    dry_run: bool


cli = desert.Command("run", type=Config)

if __name__ == "__main__":
    print(cli.build())
