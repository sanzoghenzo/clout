import functools
import sys
import typing as t

import attr
import black
import click
import marshmallow
import typing_inspect

from .. import util
from . import clout
from . import mmdc


NO_DEFAULT = "__NO_DEFAULT__"
NoneType = type(None)

native_to_click = {}


def register_type(typ):
    def register_function(func):
        native_to_click[typ] = func
        return func

    return register_function


def is_python_syntax(s: str) -> bool:
    try:
        black.format_str(s, 88)
    except black.InvalidInput:
        return False
    return True


def pythonify(obj):
    if is_python_syntax(repr(obj)):
        return repr(obj)
    if callable(obj) and is_python_syntax(obj.__name__):
        return obj.__name__
    return "..."


class Debug:
    def __repr__(self):
        pairs = ", ".join(
            (
                f"{k}={pythonify(v)}"
                for k, v in vars(self).items()
                if not k.startswith("_")
            )
        )
        name = type(self).__name__
        return black.format_str(f"{name}({pairs})", line_length=88)


class Option(Debug, click.Option):
    pass


class Group(Debug, clout.CountingGroup):
    def __call__(self, *args, **kwargs):
        try:
            return super().__call__(*args, **kwargs, standalone_mode=False)
        except SystemExit as e:
            if e.code != 0:
                raise


class Command(Debug, clout.CountingCommand):
    def __call__(self, *args, **kwargs):
        try:
            return super().__call__(*args, **kwargs)
        except SystemExit:
            if e.code != 0:
                raise


@register_type(bool)
def _(typ, metadata, default=util.UNSET):
    return Option(["--" + metadata["field_name"]], is_flag=True, default=default)


@register_type(int)
@register_type(float)
@register_type(str)
@register_type(bool)
def __(typ, metadata, default=util.UNSET):

    return Option(
        ["--" + metadata["field_name"]],
        type=typ,
        default=None if default in {NO_DEFAULT, attr.NOTHING} else default,
        required=default in {NO_DEFAULT, attr.NOTHING},
    )


class MarshmallowFieldParam(click.ParamType):
    def __init__(self, field):
        self.field = field

    @property
    def name(self):
        return type(self.field).__name__.split(".")[-1]

    def convert(self, value, param, ctx):

        try:
            return self.field.deserialize(value)
        except marshmallow.exceptions.ValidationError as e:
            raise click.BadParameter(ctx=ctx, param=param) from e


MM_TO_CLICK = {
    marshmallow.fields.String: click.STRING,
    marshmallow.fields.Int: click.INT,
    marshmallow.fields.Float: click.FLOAT,
    marshmallow.fields.Raw: click.STRING,
}


@attr.dataclass(frozen=True)
class CLI:
    inherits: t.FrozenSet[str] = attr.ib(default=frozenset())
    metadata_key: str = "cli"
    args: t.List[str] = attr.ib(factory=list)

    @functools.singledispatch
    def make_param_from_field(self, field: marshmallow.fields.Field) -> click.Parameter:

        return click.Option(
            ["--" + field.name],
            type=MarshmallowFieldParam(field),
            required=field.missing == marshmallow.missing,
            default=field.default,
        )

    @make_param_from_field.register
    def _(self, field: marshmallow.fields.Boolean) -> Option:

        return Option(
            ["--" + field.name],
            default=field.default,
            required=field.missing == marshmallow.missing,
            is_flag=True,
        )

    @make_param_from_field.register(marshmallow.fields.String)
    @make_param_from_field.register(marshmallow.fields.Int)
    @make_param_from_field.register(marshmallow.fields.Float)
    @make_param_from_field.register(marshmallow.fields.Date)
    @make_param_from_field.register(marshmallow.fields.DateTime)
    @make_param_from_field.register(marshmallow.fields.Raw)
    def _(self, field) -> Option:
        param_type = MM_TO_CLICK[type(field)]
        return Option(["--" + field.name], type=param_type)

    def make_command_from_schema(
        self, schema: marshmallow.Schema, name: str
    ) -> click.BaseCommand:
        params = []
        commands = []
        # import pudb; pudb.set_trace()
        for field in schema.fields.values():

            if isinstance(field, marshmallow.fields.Nested):
                commands.append(
                    self.make_command_from_schema(field.schema, name=field.name)
                )
            elif isinstance(field, marshmallow.fields.Field):
                params.append(self.make_param_from_field(field))
            else:
                raise TypeError(field)

        if commands:
            return Group(
                name=name,
                commands={c.name: c for c in commands},
                params=params,
                chain=True,
                result_callback=lambda *a, **kw: (a, kw),
            )
        return Command(name=name, params=params, callback=identity)

    def get_command(
        self,
        typ: t.Type,
        default=NO_DEFAULT,
        metadata: t.Mapping[str, t.Any] = None,
        args=(),
    ):
        metadata = metadata or {}

        cli_metadata: t.Union[
            t.Dict[str, t.Any], click.BaseCommand, click.Parameter
        ] = metadata.get(self.metadata_key, None)
        if isinstance(cli_metadata, (click.BaseCommand, click.Parameter)):
            command = cli_metadata
        else:
            schema = mmdc.class_schema(typ)()
            command = self.make_command_from_schema(
                schema, name=metadata.get("name", typ.__name__.lower())
            )
            command.callback = schema.load
        return command

    def prep(
        self,
        typ: t.Type,
        default=NO_DEFAULT,
        metadata: t.Mapping[str, t.Any] = None,
        args=(),
    ):
        command = self.get_command(typ, default, metadata, args)

        return clout.Parser(command, callback=command.callback).parse_args(
            args or self.args or sys.argv
        )

    def build(
        self,
        typ: t.Type,
        default=NO_DEFAULT,
        metadata: t.Mapping[str, t.Any] = None,
        args=(),
    ):
        command = self.get_command(typ, default, metadata, args)

        return clout.Parser(command, callback=command.callback).invoke_args(
            args or self.args or sys.argv
        )

    def set(self, **kw):
        return attr.evolve(self, **kw)


def identity(*args, **kw):
    return kw