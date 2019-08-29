import desert.loaders.multi


def test_deep_chainmap():
    """Get values from the nth dict even if the first dict has the first key."""
    maps = [{"a": {}}, {"a": {"b": {}}}, {"a": {"b": {"c": 1337}}}]
    dcm = desert.loaders.multi.DeepChainMap(*maps)
    assert dcm["a"]["b"]["c"] == 1337
