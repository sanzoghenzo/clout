=======================================================
Desert: dry deserialization
=======================================================

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - | |travis|
        |
    * - package
      - | |version| |wheel| |supported-versions| |supported-implementations|
        | |commits-since|

.. |docs| image:: https://img.shields.io/readthedocs/desert
    :target: https://desert.readthedocs.org
    :alt: Documentation Status


.. |travis| image:: https://img.shields.io/travis/com/python-desert/desert
    :alt: Travis-CI Build Status
    :target: https://travis-ci.com/python-desert/desert

.. |version| image:: https://img.shields.io/pypi/v/desert.svg
    :alt: PyPI Package latest release
    :target: https://pypi.org/pypi/desert

.. |commits-since| image:: https://img.shields.io/github/commits-since/python-desert/desert/v0.1.7.svg
    :alt: Commits since latest release
    :target: https://github.com/python-desert/desert/compare/v0.1.7...master

.. |wheel| image:: https://img.shields.io/pypi/wheel/desert.svg
    :alt: PyPI Wheel
    :target: https://pypi.org/pypi/desert

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/desert.svg
    :alt: Supported versions
    :target: https://pypi.org/pypi/desert

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/desert.svg
    :alt: Supported implementations
    :target: https://pypi.org/pypi/desert


.. end-badges





Installation
============

::

    pip install desert

Documentation
=============


https://desert.readthedocs.io/

Usage
=====

..
    start-usage


**Deserialize to Python objects, while staying DRY.**


Writing code that's dry ("don't repeat youreslf") means less chance of errors. Desert
helps you write deserialization code that's dry.



Here's a demo of several features.

* Create a serialization schema from a dataclass (or attrs class).
* Creating objects from several sources: raw data, code, environment variables, configuration files.
* Create a command-line interface for building complex nested objects.


Define the objects we need:

.. code-block:: python

    #!/usr/bin/env python3

    import pathlib

    import appdirs
    import attr
    import click
    import toml

    import desert.loaders.cli
    import desert.loaders.env
    import desert.loaders.multi


    @attr.dataclass
    class User:
        name: str


    @attr.dataclass
    class DB:
        host: str
        port: int
        user: User


    @attr.dataclass
    class Config:
        db: DB
        debug: bool
        user: User
        priority: float = attr.ib(
            default=0,
            metadata={
                "desert": {
                    "cli": dict(param_decls=["--priority"], help="App priority value")
                }
            },
        )
        logging: bool = True
        dry_run: bool = False


Get the defaults from environment variables and a configuration file.

.. code-block:: python

    APP_NAME = "myapp"
    CONFIG_NAME = "config"

    # Read config file.
    CONFIG_FILE_PATH = pathlib.Path(appdirs.user_config_dir(APP_NAME)) / "config.toml"
    CONFIG_FILE_DATA = toml.loads(CONFIG_FILE_PATH.read_text())

    # Read from environment_variables prefixed `MYAPP_CONFIG_`.
    # XXX How to make this simpler?
    # Provide a `prefix=` argument? If it's `desert.load_env(Config, prefix=)`, then how to
    # provide the app name and config name separately? Is that useful?
    ENVVAR_DATA = desert.loaders.env.Env(app_name=APP_NAME).prep(Config, name=CONFIG_NAME)

    # Combine config file and envvars to set CLI defaults.
    # XXX make a function `desert.combine()`?
    CONTEXT_SETTINGS = dict(
        default_map=desert.loaders.multi.DeepChainMap(ENVVAR_DATA, CONFIG_FILE_DATA)
    )

Define the CLI:

.. code-block:: python

    # XXX Should it just be called `desert.Command()`?
    commands = [
        desert.loaders.cli.DesertCommand(
            "run",
            type=Config,
            context_settings=CONTEXT_SETTINGS,
            help="Run the app with given configuration object.",
        )
    ]
    cli = click.Group(commands={c.name: c for c in commands})


Run the CLI.

.. code-block:: python


    got = cli.main(standalone_mode=False)
    print(got)


.. code-block:: bash

    $ cat ~/.config/myapp/config.toml
    [config]
    dry_run=true

    # Run the script with an environment variable set.
    $ MYAPP_CONFIG_PRIORITY=7 minicli run config --debug  user --name Alice db --host example.com --port 9999 user --name Bob
    Config(db=DB(host='example.com', port=9999, user=User(name='Bob')), debug=True, user=User(name='Alice'), priority=7.0, logging=True, dry_run=True)

..
    end-usage


Why use Desert?
~~~~~~~~~~~~~~~~~~

Why not plain dicts?
---------------------


Plain dicts are json serializable natively, why do we need classes?

Classes allow for structure, documentation, type checking, and methods.


Why not ``dataclasses.asdict()`` or ``attr.asdict()``?
---------------------------------------------------------


``asdict()`` is great for getting from objects to dicts. But how do you go the other way?
The standard answer is ``C(**d)``, but that doesn't recurse into nested objects.



Why not Marshmallow_ directly?
-----------------------------------------------------------



Marshmallow is great, that's why we're using it. But using it directly means we have to
write a whole extra schema for every class, adding a lot of duplication, and duplication
means errors.


Why not marshmallow-dataclass_?
-----------------------------------------------------------


It's a useful package, that's why desert integrates features from it! Desert supports
Marshmallow 3, supports attrs_ (down to Python 3.5), provides loaders for various data
files, environment-variable loading, freedesktop-compliant app configuration, and
command-line interfaces for complex objects.





Acknowledgements
~~~~~~~~~~~~~~~~~~~

Desert gets a lot of its power from third-party code.

* The main schema work comes from Marshmallow_ and integrates code from marshmallow-dataclass_.
* The freedesktop standard location is gotten from appdirs_.
* The command-line interface uses Click_.
* The command-line is parsed using a custom parser generator built using Lark_.
* Of course, none of this would be possible without attrs_.

.. _Marshmallow: https://marshmallow.readthedocs.io
.. _marshmallow-dataclass: https://github.com/lovasoa/marshmallow_dataclass/
.. _appdirs: https://github.com/ActiveState/appdirs
.. _click: http://click.pocoo.org
.. _lark:  https://lark-parser.readthedocs.io/en/latest/
.. _attrs: http://attrs.org
