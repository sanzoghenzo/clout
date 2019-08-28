#!/usr/bin/env python3

import dataclasses
import os
import pathlib
import typing as t

from . import loaders
from .loaders import appfile
from .loaders import cli
from .loaders import env
from .loaders import multi


@dataclasses.dataclass
class Coat:
    """A colorful coat."""

    color: str


@dataclasses.dataclass
class Dog:
    """Canis canis."""

    coat: Coat


@dataclasses.dataclass
class Cat:
    """Cats are sneaky."""

    claws: str
    outdoor: bool


@dataclasses.dataclass
class PetOwner:
    """This is an owner."""

    name: str
    dog: Dog
    cat: Cat
    age: t.Optional[int] = 21


config_file = pathlib.Path.home() / ".config/pets/config.toml"
config_file.parent.mkdir(exist_ok=True)
config_file.write_text('[dog.coat]\ncolor="brown"')

os.environ["PETOWNER_NAME"] = "Alice"

args = ["pet-owner", "cat", "--claws", "long"]


multi = loaders.multi.Multi(
    [loaders.cli.CLI(), loaders.env.Env(), loaders.appfile.TOMLFile()],
    data=dict(app_name="pets"),
)


print(multi.build(PetOwner))


# $ appconfig.py owner cat --claws=long
# Owner(name='Alice', dog=Dog(coat=Coat(color='brown')), cat=Cat(claws='long'), age=21)
