IPython `pdb` 3
===============
ipdbx_ is an improved version of ipdb_ that provides extra functionality and customisation.

Python 2 support has been dropped to make way for new features.

Use
---

``ipdbx`` exports functions to access the IPython_ debugger, which features
tab completion, syntax highlighting, better tracebacks, better introspection
with the same interface as the ``pdb`` module.

Example usage:

.. code-block:: python

        import ipdbx
        ipdbx.set_trace()
        ipdbx.set_trace(context=5)  # will show five lines of code
                                   # instead of the default three lines
                                   # or you can set it via IPDB_CONTEXT_SIZE env variable
                                   # or setup.cfg file
        ipdbx.set_trace(pretrace='/useful/debug/tools.py')  # can be set via IPDB_PRETRACE
                                                           # env variable. pretrace also
                                                           # accepts the same type of args
                                                           # as ipdbx.run(), ipdbx.runcall()
                                                           # and ipdbx.runeval()
        ipdbx.pm()
        ipdbx.run('x[0] = 3')
        result = ipdbx.runcall(function, arg0, arg1, kwarg='foo')
        result = ipdbx.runeval('f(1,2) - 3')



Patching ``sys.breakpointhook`` to call ``ipdbx`` when calling ``breakpoint()``:

.. code-block:: python

    import ipdbx
    import sys
    sys.breakpointhook = ipdbx.set_trace

    # You can also call set_trace with default arguments, likewise:

    from functools import partial
    sys.breakpointhook = partial(ipdbx.set_trace, context=30, pretrace='/my/favourite/things.py')

Arguments for ``ipdbx.set_trace``
+++++++++++++++++++++++++++++++++

The ``ipdbx.set_trace`` function accepts the following optional parameters:

* ``frame``, a `frame` object (defaults to last);
* ``context: int``, which will show as many lines of code as defined;
* ``cond: bool``, which accepts boolean values (such as ``abc == 17``) and will start ipdb's interface whenever ``cond`` equals to ``True``;
* ``pretrace``, which accepts a file path, a python statement string, or a code object, which it will execute immediately before starting the debugger.


Using configuration file
++++++++++++++++++++++++

It's possible to set up context using a `.ipdb` file on your home folder or `setup.cfg`
on your project folder. You can also set your file location via env var `$IPDB_CONFIG`.
Your environment variable has priority over the home configuration file,
which in turn has priority over the setup config file. Currently, only context setting
is available.

A valid setup.cfg is as follows

::

        [ipdb]
        context=5
        pretrace=./file.py


A valid .ipdb is as follows

::

        context=5
        pretrace="import inspect"


The post-mortem function, ``ipdbx.pm()``, is equivalent to the magic function
``%debug``.

.. _IPython: http://ipython.org
.. _ipdb: https://github.com/gotcha/ipdb
.. _ipdbx: https://github.com/giladbarnea/ipdbx

If you install ``ipdbx`` with a tool which supports ``setuptools`` entry points,
an ``ipdbx`` script is made for you. You can use it to debug your python scripts like

::

        $ bin/ipdbx mymodule.py

You can also enclose code with the ``with`` statement to launch ipdb if an exception is raised:

.. code-block:: python

        from ipdbx import launch_ipdb_on_exception

        with launch_ipdb_on_exception():
            ...



Issues with ``stdout``
----------------------

Some tools, like ``nose`` fiddle with ``stdout``.

If you use a tool that fiddles with ``stdout``, you should
explicitly ask for ``stdout`` fiddling by using ``ipdbx`` like this

.. code-block:: python

        import ipdbx
        ipdbx.sset_trace()
        ipdbx.spm()

        from ipdbx import slaunch_ipdb_on_exception
        with slaunch_ipdb_on_exception():
            ...


Development
-----------

``ipdbx`` source code and tracker are at https://github.com/giladbarnea/ipdbx.

Pull requests should take care of updating the changelog ``HISTORY.txt``.

Manual testing
++++++++++++++

To test your changes, make use of ``manual_test.py``. Create a virtual environment,
install IPython and run ``python manual_test.py`` and check if your changes are in effect.
If possible, create automated tests for better behaviour control.

