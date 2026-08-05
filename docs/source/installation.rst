Installation
============

From source
-----------

Install the package and optional docs dependencies:

.. code-block:: bash

   pip install -e .[docs]

Build documentation locally
---------------------------

.. code-block:: bash

   sphinx-build -b html docs/source docs/_build/html -W --keep-going
