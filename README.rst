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

.. |commits-since| image:: https://img.shields.io/github/commits-since/python-desert/python-desert/v0.1.2.svg
    :alt: Commits since latest release
    :target: https://github.com/python-desert/python-desert/compare/v0.1.2...master

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


https://desert.readthedocs.io/

Usage
=====


Usage
=====

Here's a demo of four features

* Create a serialization schema from a dataclass (or attrs class).
* Creating objects from several sources, such as using appdirs and toml.
* Create a command-line interface for building complex nested objects.
* Use settings from multiple backends at once, falling to the next when one is missing a value.

.. code-block:: python

    #!/usr/bin/env python3

    import os
    import pathlib
    import typing as t

    import attr

    from desert import encoders
    from desert import loaders
    from desert import runner
    import desert.encoders.toml
    import desert.loaders.appfile
    import desert.loaders.cli
    import desert.loaders.env
    import desert.loaders.multi


First we define some classes.

.. code-block:: python

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


Define the command-line interface.

.. code-block:: python

    def dance_(config):
        print("Dancing with config:\n", config)


    def sing_(config):
        print("Singing with config:\n", config)


    @attr.dataclass
    class App:
        dance: Config = dance_
        sing: Config = sing_


    multi = loaders.multi.Multi(
        [
            loaders.cli.CLI(),
            loaders.env.Env(),
            loaders.appfile.AppFile(desert.encoders.toml.TOML(), filename="config.toml"),
        ],
        data=dict(app_name="myapp"),
    )

    built = multi.build(App)
    runner.run(built)



Create a configuration file for the demo.


.. code-block:: python

    config_file = pathlib.Path.home() / ".config/myapp/config.toml"
    config_file.parent.mkdir(exist_ok=True)
    config_file.write_text(
        """\
    [dance]
    logging = true
    priority = 3
    """
    )


Run the app. The ``Config`` and ``DB`` objects are populated with data from the CLI, envvars, and config file, in the order specified in ``Multi()`` above.

.. code-block:: bash

    $ appconfig.py myapp dance --debug db --host example.com --port 9999
    Dancing with config:
    Config(db=DB(host='example.com', port=9999), debug=True, priority=3.0, logging=True, dry_run=True)
