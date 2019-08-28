import collections
import typing as t

import attr
import marshmallow

from .. import exceptions
from . import mmdc


@attr.dataclass(frozen=True)
class Multi:
    loaders: t.List = attr.ib(factory=list)
    inherits: t.FrozenSet[str] = attr.ib(default=frozenset())
    metadata_key: str = "cli"
    data: dict = attr.ib(factory=dict)

    def set(self, **kw):
        return attr.evolve(self, **kw)

    def set_data_on_loaders(self,):
        loaders = []
        for loader in self.loaders:
            loaders.append(
                loader.set(
                    **{k: v for k, v in self.data.items() if k in loader.inherits}
                )
            )
        return self.set(loaders=loaders)

    def prep(self, cls):
        multi = self.set_data_on_loaders()
        return collections.ChainMap(
            *[loader.prep(cls) or {} for loader in multi.loaders]
        )

    def build(self, cls):
        schema = mmdc.class_schema(cls)()
        prepped = self.prep(cls)

        try:
            return schema.load(prepped)
        except marshmallow.exceptions.ValidationError as e:
            raise exceptions.ValidationError(*e.args) from e
