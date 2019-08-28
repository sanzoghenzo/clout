import pathlib
import typing as t

import appdirs
import attr
import toml

from . import mmdc


@attr.dataclass(frozen=True)
class TOMLFile:
    app_name: str = None
    _filename: str = "config.toml"
    _path: t.Optional[pathlib.Path] = None
    inherits: t.FrozenSet[str] = attr.ib(default=frozenset({"app_name"}))
    metadata_key: str = "toml"
    allow_missing_file: bool = False

    @property
    def path(self):
        if self._path is not None:
            return pathlib.Path(self._path)
        if self.app_name is None:
            raise TypeError(self.app_name)
        return pathlib.Path(appdirs.user_config_dir(self.app_name)) / self._filename

    def prep(self, cls):
        try:
            return toml.loads(self.path.read_text())
        except FileNotFoundError:
            if self.allow_missing_file:
                return {}
            raise

    def build(self, cls):

        schema = mmdc.class_schema(cls)()
        return schema.load(self.prep(cls))

    def set(self, **kw):
        return attr.evolve(self, **kw)
