import attr

import clout._loaders.multi


def test_deep_chainmap():
    """Get values from the nth dict even if the first dict has the first key."""
    maps = [{"a": {}}, {"a": {"b": {}}}, {"a": {"b": {"c": 1337}}}]
    dcm = clout._loaders.multi.DeepChainMap(*maps)
    assert dcm["a"]["b"]["c"] == 1337


def test_defaults():
    """Default values are loaded."""

    @attr.dataclass(frozen=True)
    class DB:
        host: str = "example.com"
        port: int = 12345

    @attr.dataclass(frozen=True)
    class Config:
        db: DB = attr.ib(factory=DB)
        logging: bool = True
        dry_run: bool = False

    built = clout._loaders.multi.Multi([]).build(Config)

    assert built == Config(DB("example.com", 12345), True, False)
