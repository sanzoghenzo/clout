import attr

import desert


# export MYAPP_DB_HOST=lolcathost
# export MYAPP_DB_PORT=10101


@desert.type
class DatabaseSpec:
    host: str
    port: int


@desert.type
class AppConfig:
    db: DatabaseSpec
    debug: bool
    verbose: bool = attr.ib(
        metadata={"desert": {"cli": {"help": "Whether the output should be verbose."}}}
    )


config = desert.EnvReader(AppConfig).read()

assert config.db.host == "lolcathost"
assert config.db.port == 10101


config = (
    desert.MultiReader(
        name="foo",
        readers=[
            desert.loaders.CLI(metadata_key="cli"),
            desert.loaders.Env(),
            desert.loaders.EnvFile(recurse=False),
            desert.loaders.TOMLFile(),
        ],
    )
    .into(AppConfig, name="cfg")
    .read()
)
print(config)

# $ echo export FOO_PASSWORD=secr3t > .env
# $ echo '[cfg.db]\nport=9999' > ~/.config/foo/config.toml
# $ FOO_VERBOSE=1 foo cfg --debug db --host myhost.com
# AppConfig(db=DatabaseSpec(host="myhost.com", port=9999), debug=True, verbose=True)
