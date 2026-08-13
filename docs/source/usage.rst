#####
Usage
#####

The models included in this package are compatible with the AgriFoodPy
framework and can be included in a pipeline using the node structure through a
Python script interface or using a YAML pipeline configuration file.

-------------------------------
Resilience-vulnerability engine
-------------------------------

The resilience-vulnerability engine models the impact of crises on a food
balance sheet and the mitigating effect of resilience-building interventions.
The interaction of crises and interventions is modeled through resilience-vulnerability
channels which define the boundaries and the strength of the interaction
between crises and interventions.

To initialize the resilience-vulnerability engine, the user must define a set of
resilience-vulnerability channels and the corresponding resilience and vulnerability
datasets. The user can then register interventions and crises to the pipeline
using the `register_intervention` and `register_crisis` functions. The user can
also define time dependent severity of crises and adoption of interventions using
the `scale` module.


Python Scripting
----------------

Python scripting provides a flexible environment to define fine tuned inputs
for the shock registering functions.
The first step is to initialize the resilience-vulnerability engine by defining the
resilience-vulnerability channels and the corresponding resilience and vulnerability
datasets.

.. code:: python
   
   from agrifoodpy.pipeline import Pipeline
   from agrifoodpy_shocks.resilience import (
      initialize_resilience_datasets,
      register_intervention,
      register_crisis,
      process_shocks
   )

   # Create pipeline object
   fs = Pipeline()

   # Load datablock data
   ...

   # Add node to initialize resilience datasets and register interventions
   fs.add_node(
      function=initialize_resilience_datasets,
      name="Initialize",
      params={
         "fbs": "food",
         "channels":["Bio", "Log", "Lab", "Mark"]},
         "return_key":["resilience", "vulnerability", "severity"])

Next, interventions and crises can be registered to the pipeline using the
`register_intervention` and `register_crisis` functions. The user can define
resilience and vulnerability arrays to be passed to the node constructor.

.. code:: python

   # Define resilience array to be passed to the node constructor
   resilience_array = xr.DataArray(
      data= [0.8, 0.0, 0.0, 0.0],
      coords= {"channels":["Bio", "Log", "Lab", "Mark"]},
      dims= ["channels"]
   )

   # Add node to register intervention
   fs.add_node(
      function=register_intervention,
      name="Drought-resistant crops",
      params= {
         "items":"Wheat",
         "element":"production",
         "resilience":resilience_array,
         "resilience_dataset":"resilience",
         "return_key":"resilience" 
         })

   # Define time dependent severity array to be passed to node constructor 
   years = np.arange(2020, 2050)
   severity_array = xr.DataArray(
      data= np.zeros(len(years)),
      coords= {"Year":years},
      dims= ["Year"]
   )

   vulnerability_array = xr.DataArray(
      data= [0.7, 0.0, 0.2, 0.0],
      coords= {"channels":["Bio", "Log", "Lab", "Mark"]},
      dims= ["channels"]
   )

   # Add node to register crisis
   fs.add_node(
      function=register_crisis,
      name="Severe drought",
      params= {
         "items":"Wheat",
         "element":"production",
         "vulnerability":vulnerability_array,
         "severity":severity_array,
         "vulnerability_dataset":"vulnerability",
         "severity_dataset":"severity",
         "return_key":["vulnerability", "severity"]
        })

Finally, a processing node needs to be added to the pipeline to compute the
impact of the registered crises and interventions on the food balance sheet.

.. code:: python

   # Add node to process shocks
   fs.add_node(
      function=process_shocks,
      name="Process shocks",
      params={
         "resilience_dataset":"resilience",
         "severity_dataset":"severity",
         "vulnerability_dataset":"vulnerability",
         "domestic_use_element":["food", "seed", "feed", "processing"],
         "fbs":"food_projected",
         "return_key":"food"
      })

   fs.run()

Pipeline configuration YAML
---------------------------

The YAML configuration file approach allows for easy to read and share pipeline
definitions.

.. code:: yaml

   #example.yaml
   
   nodes:
   ...

   # Initialize resilience datasets
   -  function: agrifoodpy_shocks.resilience.initialize_resilience_datasets
      name: "Initialize resilience datasets"
      params:
         fbs: "food_projected"
         channels:
            - "Biophysical"
            - "Logistics"
            - "Labour"
            - "Markets"
      return_key:
            - "resilience"
            - "vulnerability"
            - "severity"

   # Interventions
   -  function: agrifoodpy_shocks.resilience.register_intervention
      name: "Drought-resistant crops"
      params:
         items: "Wheat"
         element: "production"
         adoption: !scale.linear [2020, 2020, 2030, 2050, 0.0, 1.0]
         resilience: !xarray.DataArray
            data: [0.8, 0.0, 0.0, 0.0]
            coords: {channels: ["Biophysical", "Logistics", "Labour", "Markets"]}
            dims: ["channels"]
         resilience_dataset: "resilience"
         return_key: "resilience"


   # Crises
   -  function: agrifoodpy_shocks.resilience.register_crisis
      name: "Severe drought"
      params:
         items: "Wheat"
         element: "production"
         severity_dataset: "severity"
         vulnerability_dataset: "vulnerability"
         severity: !scale.piecewise_constant
         years: [2020, 2025, 2028, 2030, 2050]
         values: [0.0, 0.5, 0.2, 0.0, 0.0]
         vulnerability: !xarray.DataArray
            data: [0.9, 0.0, 0.1, 0.0]
            coords: {channels: ["Biophysical", "Logistics", "Labour", "Markets"]}
            dims: ["channels"]
         return_key: ["vulnerability", "severity"]

   # Execution node
   -  function: agrifoodpy_shocks.resilience.process_shocks
      name: "Process shocks"
      params:
         resilience_dataset: "resilience"
         severity_dataset: "severity"
         vulnerability_dataset: "vulnerability"
         domestic_use_element: ["food", "seed", "feed", "processing"]
         fbs: "food_projected"
         return_key: "food"


The examples folder contains complete examples and notebooks to execute end
to end simulations of shocks to a food balance sheet. 