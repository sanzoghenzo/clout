import attr
import click

import clout


@attr.dataclass
class Person:
    name: str
    age: int


@clout.command(Person)
def greet(person):
    print(f"Hello, {person.name}!")


if __name__ == "__main__":
    greet.main()
