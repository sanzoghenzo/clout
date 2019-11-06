=====
Usage
=====

.. include:: ../README.rst
   :start-after: start-usage
   :end-before: end-usage



A decorator
-------------

To run a function with the built object, you can use a decorator, :func:`clout.command()`.
Using :meth:`clout.Command.main()`, the program will exit immediately afterwards.

.. literalinclude:: ../examples/decorator.py
    :language: python

.. code-block:: bash

    $ EXAMPLE_NAME=Alice python examples/decorator.py --age 21
    Hello, Alice!


A callback
-----------------

If you don't want to use a decorator, you can use :class:`clout.Command()` directly, and
pass the ``callback=`` argument.

.. literalinclude:: ../examples/callback.py
    :language: python



Extended example
--------------------

Now for a longer example.

* Define a nested configuration object.
* Load the object from the CLI, getting missing values from environment variables,
  configuration file, and dataclass ``default=`` values.


Here we define the config file in the Freedesktop standard directory.

.. code-block:: toml

    # ~/.config/myapp/config.toml
    [config]
    dry_run=true


Set an environment variable and run the app.


.. code-block:: bash

    % MYAPP_PRIORITY=2 python examples/long.py --debug  user --name Alice db --host example.com --port 9999 user --name Bob
    Config(db=DB(host='example.com', port=9999, user=User(name='Bob')), debug=True, dry_run=True, user=User(name='Alice'), priority=2.0, logging=True)



The code:

.. literalinclude:: ../examples/long.py
    :language: python
