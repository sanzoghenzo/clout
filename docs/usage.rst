=====
Usage
=====

.. include:: ../README.rst
   :start-after: start-usage
   :end-before: end-usage


Extended example
--------------------

Now for a longer example.

* Define a nested configuration object.
* Load the object from the CLI, getting missing values from environment variables,
  configuration file, and dataclass ``default=`` values.


.. literalinclude:: long.py
    :language: python
