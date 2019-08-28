import typing as t

import attr
import toml


@attr.dataclass
class TOML:
    encoder: toml.TomlEncoder = toml.TomlEncoder
    cls: t.Type = dict

    def dumps(self, data, encoder=None) -> str:
        return encoder.dumps(data, encoder=encoder or self.encoder)

    def loads(self, text: str, cls=None):
        return toml.loads(text, _dict=cls or self.cls)
