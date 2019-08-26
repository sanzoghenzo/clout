import typing as t

import attr

import desert.loaders.click


@attr.dataclass
class Person:
    name: str
    age: t.Optional[int]


desert.loaders.click.CLI().make_field(typ=Person, metadata={"name": "cfg"})()
