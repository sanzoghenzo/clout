import desert.loaders.multi


def test_deep_chainmap():
    maps = [{"a": {}}, {"a": {"b": {}}}, {"a": {"b": {"c": 1337}}}]
    dcm = desert.loaders.multi.DeepChainMap(*maps)
    assert dcm["a"]["b"]["c"] == 1337
