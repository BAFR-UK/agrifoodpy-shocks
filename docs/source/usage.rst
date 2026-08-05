Usage
=====

The project supports scripted pipeline definitions and YAML pipeline
configuration for registering interventions and crises.

Minimal example
---------------

.. code-block:: python

   from agrifoodpy_shocks.resilience.engine import (
       initialize_resilience_datasets,
       register_intervention,
       register_crisis,
       process_shocks,
   )

See the repository examples for end-to-end configurations.
