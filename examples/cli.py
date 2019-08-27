import typing as t

import dataclasses

import desert.loaders.click


@dataclasses.dataclass
class Coat:
    color: str


@dataclasses.dataclass
class Dog:
    coat: Coat


@dataclasses.dataclass
class Cat:
    claws: str


@dataclasses.dataclass
class Person:
    name: str
    dog: Dog
    cat: Cat
    age: t.Optional[int] = 21


cli = desert.loaders.click.CLI().make_field(typ=Person, metadata={"name": "cfg"})
print(cli)

result = cli()

print(result)
