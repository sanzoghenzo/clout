import collections
import typing as t

import attr

from . import mmdc


@attr.dataclass(frozen=True)
class Multi:
    loaders: t.List = attr.ib(factory=list)
    inherits: t.FrozenSet[str] = attr.ib(default=frozenset())
    metadata_key: str = "cli"

    def set(self, **kw):
        return attr.evolve(self, **kw)

    def prep(self, cls):
        return collections.ChainMap(*[loader.prep(cls) for loader in self.loaders])

    def build(self, cls):
        schema = mmdc.class_schema(cls)()
        return schema.load(self.prep(cls))
