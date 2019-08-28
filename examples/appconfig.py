#!/usr/bin/env python3

import dataclasses
import os
import pathlib
import typing as t

import desert.loaders.appfile
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
class Owner:
    name: str
    dog: Dog
    cat: Cat
    age: t.Optional[int] = 21


config_file = pathlib.Path.home() / ".config/pets/config.toml"
config_file.parent.mkdir(exist_ok=True)
config_file.write_text('[dog.coat]\ncolor="brown"')

os.environ["OWNER_NAME"] = "Alice"

args = ["owner", "cat", "--claws", "long"]


multi = desert.loaders.multi.Multi(
    [
        desert.loaders.cli.CLI(),
        desert.loaders.env.Env(),
        desert.loaders.appfile.TOMLFile(),
    ],
    data=dict(app_name="pets"),
)


print(multi.build(Owner))


# $ appconfig.py owner cat --claws long
# Owner(name='Alice', dog=Dog(coat=Coat(color='brown')), cat=Cat(claws='long'), age=21)
