import typing as t

import attr
import black
import click
import typing_inspect


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


class Debug:
    def __repr__(self):
        pairs = ", ".join(
            (
                f"{k}={repr(v)}"
                for k, v in vars(self).items()
                if not k.startswith("_") and not callable(v)
                if is_python_syntax(k) and is_python_syntax(repr(v))
            )
        )
        name = type(self).__name__
        return black.format_str(f"{name}({pairs})", line_length=88)


class Option(Debug, click.Option):
    pass


class Group(Debug, click.Group):
    def __call__(self, *args, **kwargs):
        try:
            return super().__call__(*args, **kwargs, standalone_mode=False)
        except SystemExit as e:
            if e.code != 0:
                raise


class Command(Debug, click.Command):
    def __call__(self, *args, **kwargs):
        try:
            return super().__call__(*args, **kwargs)
        except SystemExit:
            if e.code != 0:
                raise


@register_type(bool)
def _(typ, metadata, default):
    return Option(["--" + metadata["field_name"]], is_flag=True, default=default)


@register_type(int)
@register_type(float)
@register_type(str)
@register_type(bool)
def __(typ, metadata, default):

    return Option(
        ["--" + metadata["field_name"]],
        type=typ,
        default=None if default in {NO_DEFAULT, attr.NOTHING} else default,
        required=default in {NO_DEFAULT, attr.NOTHING},
    )


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

        cli_metadata = cli_metadata.copy() if cli_metadata else {}

        origin = typing_inspect.get_origin(typ)
        if origin:

            arguments = typing_inspect.get_args(typ, True)

            if origin in (list, t.List):
                cli_metadata["multiple"] = True
                return self.make_field(
                    typ=arguments[0],
                    metadata=dict(metadata, **{self.metadata_key: cli_metadata}),
                    default=default,
                )
            elif origin in (tuple, t.Tuple):
                cli_metadata["nargs"] = len(arguments)
                raise NotImplementedError("tuple not supported")
                return marshmallow.fields.Tuple(
                    tuple(field_for_schema(arg) for arg in arguments), **metadata
                )
            elif origin in (dict, t.Dict):
                raise NotImplementedError("dict not supported")
                return marshmallow.fields.Dict(
                    keys=field_for_schema(arguments[0]),
                    values=field_for_schema(arguments[1]),
                    **metadata,
                )
            elif typing_inspect.is_optional_type(typ):
                [subtyp] = (t for t in arguments if t is not NoneType)
                # Treat optional types as types with a None default
                metadata["default"] = metadata.get("default", None)
                metadata["missing"] = metadata.get("missing", None)
                metadata["required"] = False
                return self.make_field(
                    subtyp,
                    default=metadata["default"] or default,
                    metadata=dict(metadata, **{self.metadata_key: cli_metadata}),
                )
                return field_for_schema(subtyp, metadata=metadata)
            elif typing_inspect.is_union_type(typ):
                raise NotImplementedError("Union")
                subfields = [
                    field_for_schema(subtyp, metadata=metadata) for subtyp in arguments
                ]

                import marshmallow_union

                return marshmallow_union.Union(subfields, **metadata)

        for candidate_type in native_to_click.keys():
            # TODO use a better linearization algorithm.
            if issubclass(typ, candidate_type):
                return native_to_click[candidate_type](typ, metadata, default)

        if attr.has(typ):

            params = []
            subcommands = []
            for hint, attr_field in zip(
                t.get_type_hints(typ).values(), attr.fields(typ)
            ):
                field = self.make_field(
                    typ=hint,
                    metadata=dict(attr_field.metadata, field_name=attr_field.name),
                    default=attr_field.default,
                )
                if attr.has(hint):
                    subcommands.append(field)
                else:
                    params.append(field)

            name = metadata.get("name", metadata.get("field_name"))
            if subcommands:
                return Group(
                    name=name,
                    commands={c.name: c for c in subcommands},
                    params=params,
                    chain=True,
                    result_callback=identity,
                )
            return Command(name=name, params=params, callback=identity)

        if isinstance(cli_metadata, dict):
            raise NotImplementedError("Dict isn't supported at this time.")

        raise TypeError("Unexpected type", type(metadata), "of", metadata)


def identity(*args, **kw):
    return kw
