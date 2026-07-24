# agrifoodpy-shocks

AgriFoodPy-shocks is an extension package for resilience modeling in agrifood
systems, compatible with the [AgriFoodPy](https://github.com/FixOurFood/AgriFoodPy) framework. These models simulate the effects of food system **shocks**,
including resilience building **interventions** and vulnerability exposing
**crises**.
The effects include food supply and availability perturbations and land use
change.  

## Installation

agrifoodpy-shocks can be installed directly from this repository using *pip*:
```
pip install git+https://github.com/BAFR-UK/agrifoodpy-shocks.git
```

## Usage

The models included here are compatible with the AgriFoodPy framework and can
be included in a pipeline using the node structure through a Python script
interface or using a YAML pipeline configuration file. 

### Python Scripting

Python scripting provides a flexible environment to define fine tuned inputs
for the shock registering functions.

```python
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

# Define resilience array to be passed to the node constructor
resilience_array = xr.DataArray(
    data= [0.8, 0.0, 0.0, 0.0]
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
    data= np.zeros(len(years))
    coords= {"Year":years},
    dims= ["Year"]
)

vulnerability_array = xr.DataArray(
    data= [0.7, 0.0, 0.2, 0.0]
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
        "vulnerability_dataset":"resilience",
        "severity_dataset":"severity",
        "return_key":"resilience" 
        })
```

### Pipeline configuration YAML

The YAML configuration file approach allows for easy to read and share pipeline
definitions.


```yaml
#example.yaml

nodes:
...

  # Interventions
  - function: agrifoodpy_shocks.resilience.register_intervention
    name: "Drought-resistant crops"
    params:
      items: "Wheat"
      element: "production"
      adoption: !scale.linear [2020, 2020, 2030, 2050, 0.0, 1.0]
      resilience: !xarray.DataArray
        data: [0.8, 0.0, 0.0, 0.0]
        coords: {channels: ["Bio", "Log", "Lab", "Mark"]}
        dims: ["channels"]
      resilience_dataset: "resilience"
      return_key: "resilience"


  # Crises
  - function: agrifoodpy_shocks.resilience.register_crisis
    name: "Severe drought"
    params:
      items: "Wheat"
      element: "production"
      # fbs: "food"
      severity_dataset: "severity"
      vulnerability_dataset: "vulnerability"
      severity: !scale.piecewise_constant
        years: [2020, 2025, 2028, 2030, 2050]
        values: [0.0, 0.5, 0.2, 0.0, 0.0]
      vulnerability: !xarray.DataArray [
        [0.9, 0.0, 0.1, 0.0],
        {channels: ["Bio", "Log", "Lab", "Mark"]}, "channels"]
      return_key: ["vulnerability", "severity"]

```

The `examples` folder contains complete examples and notebooks to execute end
to end simulations of shocks to a food balance sheet. 


## Contributing

AgriFoodPy and AgriFoodPy-shocks are open-source projects which aim at
improving the transparency of evidence base food system interventions and
policy making.
As such, we are happy to hear the input and ideas from the community.

If you want to contribute, have a look at the discussions page or open a new
issue.

For a comprehensive guide, please refer to the contributing guidelines in the
main [AgriFoodPy](https://github.com/FixOurFood/AgriFoodPy) repository to open
a pull request to contribute new functionality.