========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - | |travis| |appveyor|
        |
    * - package
      - | |version| |wheel| |supported-versions| |supported-implementations|
        | |commits-since|

.. |docs| image:: https://readthedocs.org/projects/python-desert/badge/?style=flat
    :target: https://readthedocs.org/projects/python-desert
    :alt: Documentation Status


.. |travis| image:: https://travis-ci.org/python-desert/python-desert.svg?branch=master
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/python-desert/python-desert

.. |appveyor| image:: https://ci.appveyor.com/api/projects/status/github/python-desert/python-desert?branch=master&svg=true
    :alt: AppVeyor Build Status
    :target: https://ci.appveyor.com/project/python-desert/python-desert

.. |version| image:: https://img.shields.io/pypi/v/desert.svg
    :alt: PyPI Package latest release
    :target: https://pypi.org/pypi/desert

.. |commits-since| image:: https://img.shields.io/github/commits-since/python-desert/python-desert/v0.1.0.svg
    :alt: Commits since latest release
    :target: https://github.com/python-desert/python-desert/compare/v0.1.0...master

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

Deserialize to objects.

* Free software: BSD 2-Clause License

Installation
============

::

    pip install desert

Documentation
=============


https://python-desert.readthedocs.io/

Usage
=====

Desert does four things.

* Create a serialization schema from a dataclass (or attrs class).
* Provides utilities for creating objects from several sources, such as using appdirs and toml.
* Creates a command-line interface for building complex objects
* Allows combining multiple serialization backends with different priorities, so settings from the command line override envvars, which override the config file.

.. code-block:: python

    #!/usr/bin/env python3


    import os
    import pathlib
    import typing as t

    import attr


    from .. import encoders
    from .. import loaders
    from .. import runner
    from ..encoders import toml
    from ..loaders import appfile
    from ..loaders import cli
    from ..loaders import env
    from ..loaders import multi


    @attr.dataclass
    class DB:
        host: str
        port: int


    @attr.dataclass
    class Config:
        db: DB
        debug: bool
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


    def dance_(config):
        print("Dancing with config:", config)


    def sing_(config):
        print("Singing with config:", config)


    @attr.dataclass
    class App:
        dance: Config = dance_
        sing: Config = sing_


    config_file = pathlib.Path.home() / ".config/myapp/config.toml"
    config_file.parent.mkdir(exist_ok=True)
    config_file.write_text(
        """\
    [dance]
    logging = true
    priority = 3
    """
    )


    os.environ["MYAPP_APP_DANCE_DRY_RUN"] = "1"


    multi = loaders.multi.Multi(
        [
            loaders.cli.CLI(),
            loaders.env.Env(),
            loaders.appfile.AppFile(encoders.toml.TOML(), filename="config.toml"),
        ],
        data=dict(app_name="myapp"),
    )

    built = multi.build(App)
    runner.run(built)


    # $ myapp app dance   --debug db --host example.com --port 9999
    # Dancing with config: Config(db=DB(host='example.com', port=9999), debug=True, priority=3.0, logging=True, dry_run=True)
