import typing as t

import dataclasses

import desert.loaders.click


@dataclasses.dataclass
class Dog:
    color: str


@dataclasses.dataclass
class Person:
    name: str
    pet: Dog
    age: t.Optional[int] = 21


cli = desert.loaders.click.CLI().make_field(typ=Person, metadata={"name": "cfg"})
print(cli)

result = cli()

print(result)
