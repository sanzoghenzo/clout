import pathlib
import typing as t

import appdirs
import attr
import importlib_resources

from .. import core
from . import mmdc


@attr.dataclass(frozen=True)
class Resource:
    encoder: core.Encoder
    package_name: str = None
    filename: str
    inherits: t.FrozenSet[str] = attr.ib(default=frozenset({"package_name"}))
    metadata_key: str = "resource"
    allow_missing_file: bool = False

    def prep(self, cls):
        try:
            text = importlib_resources.read_text(self.package_name, self.filename)
        except FileNotFoundError:
            if self.allow_missing_file:
                return {}
            raise
        return self.encoder.loads(text)

    def build(self, cls):
        schema = mmdc.class_schema(cls)()
        return schema.load(self.prep(cls))

    def set(self, **kw):
        return attr.evolve(self, **kw)
