import attr

import clout


@attr.dataclass
class Person:
    name: str = attr.ib(metadata={"clout": {"cli": dict(envvar="EXAMPLE_NAME")}})
    age: int


@clout.command(Person)
def greet(person):
    print(f"Hello, {person.name}!")


if __name__ == "__main__":
    print(greet.main())
