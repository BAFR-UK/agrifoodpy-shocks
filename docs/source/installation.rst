############
Installation
############

This page outlines how to install one of the officially distributed
agrifoodpy_shocks releases and its dependencies, or install and test the latest
development version.

From PyPI
---------

agrifoodpy_shocks is distributed through the Python Package Index (PyPI_),
and can be installed using pip_:

.. code:: console

    $ pip install agrifoodpy-shocks

From GitHub
-----------

The latest development version of agrifoodpy_shocks can be found on the main
branch of the `BAFR-UK/agrifoodpy-shocks`_ GitHub repository.
This and any other branch or tag can be installed directly from GitHub using a
recent version of pip:

.. code:: console

    $ pip install agrifoodpy_shocks@git+https://github.com/BAFR-UK/agrifoodpy-shocks.git@main


.. _PyPI: https://pypi.org/project/agrifoodpy-shocks/
.. _pip: https://pip.pypa.io/
.. _BAFR-UK/agrifoodpy-shocks: https://github.com/BAFR-UK/agrifoodpy-shocks
.. _pytest: https://docs.pytest.org/

Dependencies
------------

agrifoodpy_shocks has been tested to be compatible with Python versions 3.9 or
later on Linux, macOS and Windows operating systems. It has the following core
dependencies:

- `xarray <https://docs.xarray.dev/en/stable/>`_
- `agrifoodpy>=0.2.1 <https://github.com/FixOurFood/agrifoodpy>`_

Installing using pip will automatically install or update these core
dependencies if necessary.