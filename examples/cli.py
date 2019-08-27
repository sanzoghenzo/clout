import typing as t

import click
import dataclasses

import desert.loaders.click
import desert.loaders.clout


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

parser = desert.loaders.clout.Parser(cli, callback=cli.callback)


line = "cfg --name Alice dog coat --color brown cat --claws long"
result = parser.invoke_string(line)
print(result)
