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


@register_type(bool)
def _(typ, metadata, default):
    return click.Option("--" + metadata["field_name"], is_flag=True, default=default)


@register_type(int)
@register_type(float)
@register_type(str)
@register_type(bool)
def __(typ, metadata, default):
    return click.Option("--" + metadata["field_name"], type=typ, default=default)


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

        if typ in native_to_click:
            return native_to_click[typ](typ, metadata, default)

        if isinstance(cli_metadata, dict):
            raise NotImplementedError("Dict isn't supported at this time.")

        raise TypeError("Unexpected type", type(metadata), "of", metadata)
