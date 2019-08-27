import typing as t

import attr

import desert.loaders.click


@attr.dataclass
class Dog:
    color: str


@attr.dataclass
class Person:
    name: str
    pet: Dog
    age: t.Optional[int] = 21


cli = desert.loaders.click.CLI().make_field(typ=Person, metadata={"name": "cfg"})
print(cli)

result = cli()

print(result)
