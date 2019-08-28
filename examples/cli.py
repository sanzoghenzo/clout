import typing as t

import click
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


args = [
    "person",
    "--name",
    "Alice",
    "dog",
    "coat",
    "--color",
    "brown",
    "cat",
    "--claws",
    "long",
]
result = desert.loaders.click.CLI().build(Person, args=args)
print(result)
