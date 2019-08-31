=======================================================
Desert: Deserialize to Python objects
=======================================================

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

.. |docs| image:: https://img.shields.io/readthedocs/desert
    :target: https://desert.readthedocs.org
    :alt: Documentation Status


.. |travis| image:: https://travis-ci.org/python-desert/desert.svg?branch=master
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/python-desert/desert

.. |appveyor| image:: https://ci.appveyor.com/api/projects/status/github/python-desert/desert?branch=master&svg=true
    :alt: AppVeyor Build Status
    :target: https://ci.appveyor.com/project/python-desert/desert

.. |version| image:: https://img.shields.io/pypi/v/desert.svg
    :alt: PyPI Package latest release
    :target: https://pypi.org/pypi/desert

.. |commits-since| image:: https://img.shields.io/github/commits-since/python-desert/desert/v0.1.3.svg
    :alt: Commits since latest release
    :target: https://github.com/python-desert/desert/compare/v0.1.3...master

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



**Deserialize to Python objects, while staying DRY.**

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

Here's a demo of several features.

* Create a serialization schema from a dataclass (or attrs class).
* Creating objects from several sources: raw data, code, environment variables, configuration files.
* Create a command-line interface for building complex nested objects.



Create a serialization schema from a dataclass (or attrs class)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


Define some dataclasses, and it becomes easy to load and dump dicts into complex structured data.


.. code-block:: python


        from attr import dataclass

        import desert


        @dataclass
        class DB:
            host: str
            port: int


        @dataclass
        class Config:
            db: DB
            debug: bool
            logging: bool
            dry_run: bool = False


        # Define some nested data.
        data = {"db": {"host": "example.com", "port": 1234}, "debug": True, "logging": True}
        # Create a schema.
        schema = desert.schema(Config)
        # Use the schema to load the data into objects.
        config = schema.load(data)

        # Dump the objects back into raw data.
        assert schema.dump(config) == dict(data, dry_run=False)

        print(config)


.. code-block:: bash


    $ python example.py
    Config(db=DB(host="example.com", port=1234), debug=True, logging=True, dry_run=False)

Get data from code, environment variables, and config files.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Suppose we have data in environment variables and a configuration file, and the data
provided in source code is incomplete.

.. code-block:: python

    incomplete_data = {"db": {"host": "example.com", "port": 1234}}

    multi = loaders.multi.Multi(
        [
            loaders.raw.Raw(incomplete_data),
            loaders.env.Env(),
            loaders.appfile.AppFile(desert.encoders.toml.TOML(), filename="config.toml"),
        ],
        data=dict(app_name="myapp"),
    )

    built = multi.build(App)

    assert built == Config(DB(host="example.com", port=1234), debug=True, logging=True)
    print(built)


In a configuration file at ``~/.config/myapp/config.toml`` we set two variables:

.. code-block:: toml

    [config]
    debug = true
    logging = false


We enable logging with an environment variable:

.. code-block:: bash

    export MYAPP_CONFIG_LOGGING=1

Now running the program, we see all of the values have been set, and that the environment
variable's value for ``logging`` (True) has overridden the configuration file's value for
that variable (False). This precedence ordering is determined by the order in which you
list the loaders in `Multi([...])`. The final missing value, ``dry_run=False``, is
determined by the default value set on the dataclass.


.. code-block:: bash

    $ python example.py
    Config(DB(host="example.com", port=1234), debug=True, logging=True)


Create a command-line interface for building complex nested objects
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. note ::

    The command-line API is **experimental** and subject to change without notice.



As discussed above, Desert lets us create complex nested objects using raw data,
environment variables, and configuration files. We can create complex nested objects from
the command line.

For example,


.. code-block:: bash

    $ myapp config --no-logging --dry-run db --host=example.com --port=1234

will create a Python object like this:

.. code-block:: python

    Config(db=DB(host="example.com", port=1234), logging=False, dry_run=True)



A command-line demo
--------------------------


Set up the imports.

.. code-block:: python


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
        sing: Config = lambda c=None: sing_


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


.. code-block:: toml


    [dance]
    logging = true
    priority = 3


Run the app. The ``Config`` and ``DB`` objects are populated with data from the CLI, envvars, and config file, in the order specified in ``Multi()`` above.

.. code-block:: bash

    $ MYAPP_APP_CONFIG_DRY_RUN=1 appconfig.py myapp dance --debug db --host example.com --port 9999
    Dancing with config:
    Config(db=DB(host='example.com', port=9999), debug=True, priority=3.0, logging=True, dry_run=True)


..
    end-usage
