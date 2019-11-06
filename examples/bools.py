import attr
import click

import clout


@attr.dataclass
class Person:
    name: str
    tall: bool


def greet(person):
    print(f"Hello, {person.name}!")


cli = clout.Command(Person, callback=greet)

if __name__ == "__main__":
    cli.main()
