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


Development
===========

To run the all tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox
