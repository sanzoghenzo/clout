=======================================================
Desert: Build command-line interfaces from dataclasses
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
      - | |version|
        | |wheel|
        | |supported-versions|
        | |supported-implementations|
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



..
    start-usage



Writing code that's dry ("don't repeat yourself") means less chance of errors. Desert
helps you write code that's dry.


Quickstart
---------------


To install, use

.. code-block:: bash

    pip install desert


Define some dataclasses and convert them into a command-line interface.


.. code-block:: python

    import attr
    import click

    import desert


    @attr.dataclass
    class DB:
        host: str
        port: int


    @attr.dataclass
    class Config:
        db: DB
        dry_run: bool


    cli = desert.Command("run", type=Config)

    print(cli.build())


.. code-block:: bash

    $ myapp config --dry-run db --host example.com --port 9999
    Config(db=DB(host='example.com', port=9999), dry_run=True)


..
    end-usage

See the full docs for more information: https://desert.readthedocs.io/
