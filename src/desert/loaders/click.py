import typing as t

import attr
import click


NO_DEFAULT = "__NO_DEFAULT__"

native_to_click = {}


def register_type(typ):
    def register_function(func):
        native_to_click[typ] = func
        return func

    return register_function


class Debug:
    def __repr__(self):
        pairs = ", ".join(
            (
                f"{k}={v}"
                for k, v in vars(self).items()
                if not k.startswith("_") and not callable(v)
            )
        )
        name = type(self).__name__
        return f"{name}({pairs})"


class Option(Debug, click.Option):
    pass


class Group(Debug, click.Group):
    pass


class Command(Debug, click.Command):
    pass


@register_type(bool)
def _(typ, metadata, default):
    return Option(["--" + metadata["field_name"]], is_flag=True, default=default)


@register_type(int)
@register_type(float)
@register_type(str)
@register_type(bool)
def __(typ, metadata, default):
    return Option(["--" + metadata["field_name"]], type=typ, default=default)


@attr.dataclass(frozen=True)
class CLI:
    inherits: t.FrozenSet[str] = attr.ib(default=frozenset())
    metadata_key: str = "cli"

    def make_field(
        self, typ: t.Type, default=NO_DEFAULT, metadata: t.Mapping[str, t.Any] = None
    ):
        metadata = metadata or {}

        cli_metadata: t.Union[
            t.Dict[str, t.Any], click.BaseCommand, click.Parameter
        ] = metadata.get(self.metadata_key, None)

        if cli_metadata is not None and not isinstance(cli_metadata, dict):
            return cli_metadata

        for candidate_type in native_to_click.keys():
            # TODO use a better linearization algorithm.
            if issubclass(typ, candidate_type):
                return native_to_click[candidate_type](typ, metadata, default)

        if attr.has(typ):
            group = Group(name=metadata["name"])
            for hint, attr_field in zip(
                t.get_type_hints(typ).values(), attr.fields(typ)
            ):
                field = self.make_field(
                    typ=hint,
                    metadata=dict(attr_field.metadata, field_name=attr_field.name),
                    default=attr_field.default,
                )
                if attr.has(hint):
                    group.commands.append(field)
                else:
                    group.params.append(field)

            return group

        if isinstance(cli_metadata, dict):
            raise NotImplementedError("Dict isn't supported at this time.")

        raise TypeError("Unexpected type", type(metadata), "of", metadata)
