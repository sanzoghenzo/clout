import os
import typing as t

import click
import dataclasses

import desert.loaders.cli
import desert.loaders.env
import desert.loaders.multi


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


args = ["person", "dog", "coat", "--color", "brown", "cat", "--claws", "long"]


os.environ["PERSON_NAME"] = "Alice"


multi = desert.loaders.multi.Multi(
    [desert.loaders.cli.CLI(args=args), desert.loaders.env.Env()]
)
print(multi.prep(Person))


print(multi.build(Person))
