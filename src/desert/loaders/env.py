import os
import typing as t

import attr
import environs
import glom
import marshmallow

from . import mmdc


@attr.dataclass
class Env:
    metadata_key: str = "env"
    inherits: t.List[str] = attr.ib(factory=list)
    env: t.Dict[str, t.Any] = attr.ib(factory=dict)

    def make_path_to_field(
        self, schema: marshmallow.Schema, path=()
    ) -> t.Dict[str, marshmallow.fields.Field]:

        d = {}
        for field in schema.fields.values():

            if isinstance(field, marshmallow.fields.Nested):
                d.update(
                    self.make_path_to_field(field.schema, path=path + (field.name,))
                )

            elif isinstance(field, marshmallow.fields.Field):
                d[path + (field.name,)] = field
            else:
                raise TypeError(field)

        return d

    def make_envvar_name(self, path: t.Tuple[str]) -> str:
        return "_".join(path).upper()

    def prep(self, typ, metadata=None, default=None, env=None):
        # TODO make sure this handles lists correctly.
        # If a field is a list, this should return a list, not a single member.
        metadata = metadata or {}
        top_name = typ.__name__.lower()

        schema = mmdc.class_schema(typ)()
        path_to_field = self.make_path_to_field(schema, path=(top_name,))

        d = {}
        for path, field in path_to_field.items():
            name = self.make_envvar_name(path)

            value = os.environ.get(name)
            if value is not None:
                d[path] = field.deserialize(value)
        return make_nested(d)[top_name]

    def set(self, **kw):
        return attr.evolve(self, **kw)


def make_nested(path_to_value: t.Dict[t.Tuple, t.Any]) -> dict:
    d = {}
    for path, value in sorted(
        path_to_value.items(), key=lambda path_value: len(path_value[0])
    ):
        func = dict
        glom.assign(d, ".".join(path), value, missing=func)
    return d
