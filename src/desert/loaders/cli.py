import functools
import sys
import typing as t

import attr
import click
import inflection
import marshmallow
import typing_inspect

from .. import schemas
from .. import util
from . import clout


NO_DEFAULT = "__NO_DEFAULT__"
TOP_LEVEL_NAME = "top_level_name"
NoneType = type(None)


def is_python_syntax(s: str) -> bool:
    import black

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
        import black

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
            raise click.BadParameter(ctx=ctx, param=param, message=str(e)) from e


MM_TO_CLICK = {
    marshmallow.fields.String: click.STRING,
    marshmallow.fields.Int: click.INT,
    marshmallow.fields.Float: click.FLOAT,
    marshmallow.fields.Raw: click.STRING,
    marshmallow.fields.Bool: click.BOOL,
}


def make_help_command():
    return Command(name="--help", hidden=True)


@functools.singledispatch
def make_param_from_field(field: marshmallow.fields.Field, data) -> click.Parameter:

    if data:
        data = data.copy()
        if "type" not in data:
            data["type"] = MM_TO_CLICK[type(field)]
        return Option(**data)

    return Option(
        ["--" + field.name],
        type=MarshmallowFieldParam(field),
        required=False,
        default=field.default,
    )


@make_param_from_field.register(marshmallow.fields.Boolean)
def _(field: marshmallow.fields.Boolean, data) -> Option:
    if data:
        return Option(**data)

    return Option(
        [util.dasherize(f"--{field.name}/--no-{field.name}")],
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
def _(field, data) -> Option:
    if data:
        data = data.copy()

        if "type" not in data:
            data["type"] = MM_TO_CLICK[type(field)]
        return Option(**data)
    param_type = MM_TO_CLICK[type(field)]
    return Option(["--" + field.name], type=param_type)


@attr.dataclass(frozen=True)
class CLI:
    inherits: t.FrozenSet[str] = frozenset({"app_name"})
    metadata_key: str = "cli"
    args: t.List[str] = attr.ib(factory=list)
    app_name: str = None

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
                user_specified = field.metadata.get("cli")
                param = make_param_from_field(field, user_specified)
                params.append(param)
            else:
                raise TypeError(field)

        commands.append(make_help_command())

        help = getattr(schema, "help", None)
        if commands:
            return Group(
                name=name,
                commands={c.name: c for c in commands},
                params=params,
                chain=True,
                result_callback=lambda *a, **kw: (a, kw),
                help=help,
                short_help=help,
            )
        return Command(
            name=name, params=params, callback=identity, help=help, short_help=help
        )

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
            name = metadata.get("name", util.dasherize(self.app_name))

            schema = schemas.class_schema(typ)()
            command = self.make_command_from_schema(schema, name=name)
            command.callback = schema.load

        command = Group(
            name=TOP_LEVEL_NAME,
            commands={c.name: c for c in [command, make_help_command()]},
        )
        return command

    def prep(
        self,
        typ: t.Type,
        default=NO_DEFAULT,
        metadata: t.Mapping[str, t.Any] = None,
        args=(),
    ):

        command = self.get_command(typ, default, metadata, args)

        parser = clout.Parser(command, callback=command.callback, use_defaults=False)
        cli_args = [TOP_LEVEL_NAME] + (args or self.args or sys.argv[1:])
        import lark

        try:
            result = parser.parse_args(cli_args)
        except (lark.exceptions.ParseError, lark.exceptions.UnexpectedCharacters):
            print(command.get_help(click.Context(command)))
            raise
        [value] = result.values()
        return value

    def build(
        self,
        typ: t.Type,
        default=NO_DEFAULT,
        metadata: t.Mapping[str, t.Any] = None,
        args=(),
    ):
        command = self.get_command(typ, default, metadata, args)
        return command.callback(self.prep(typ, default, metadata, args))

    def set(self, **kw):
        return attr.evolve(self, **kw)


def identity(*args, **kw):
    return kw
