import typing as t

import attr
import toml


@attr.dataclass
class TOML:
    encoder: "toml.TomlEncoder" = toml.TomlEncoder
    cls: t.Type = dict

    def dumps(self, data, encoder=None) -> str:
        encoder = encoder or self.encoder
        return encoder.dumps(data, encoder=encoder)

    def loads(self, text: str, cls=None):
        return self.encoder.loads(text, _dict=cls or self.cls)
