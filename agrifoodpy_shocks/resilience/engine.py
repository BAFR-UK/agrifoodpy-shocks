import xarray as xr
import numpy as np
import agrifoodpy
from agrifoodpy.pipeline import pipeline_node
from agrifoodpy.utils.dict_utils import item_parser
from agrifoodpy_shocks.crises.supply import rapid_supply_decrease

@pipeline_node(input_keys=['fbs', 'resilience_dataset'])
def register_intervention(
    items: str | int | float | list[str] | list[int] | list[float] | tuple,
    element: str,
    resilience: list[float] | xr.DataArray,
    resilience_dataset: xr.Dataset = None,
    fbs: xr.Dataset = None,
) -> xr.Dataset:
    """
    Register the vulnerability channels resilience values associated with a
    specific item and element combination in the food balance sheet (FBS)
    dataset.
    
    Parameters
    ----------
    fbs : xr.Dataset
        The input food balance sheet dataset to be used as a reference for the
        resilience registration.
    items : str | int | float | list[str] | list[int] | list[float] | tuple
        Items to be impacted by the resilience registration.
    element : str
        The element of the FBS dataset to modify.
    resilience : list[float] | xr.DataArray
        The resilience values for the specified channels.
    resilience_dataset : xr.Dataset, optional
        The resilience dataset to be modified, by default None.

    Returns
    -------
    xr.Dataset
        The modified resilience dataset with registered resilience values for
        the specified item and element combination.
    """

    if isinstance(resilience, xr.DataArray):
        channels_da = resilience.copy()

        if "channels" not in channels_da.dims:
            if channels_da.ndim != 1:
                raise ValueError(
                    "When 'channels' is a DataArray, it must either include a "
                    "'channels' dimension or be one-dimensional."
                )

            channels_da = channels_da.rename({channels_da.dims[0]: "channels"})

        if "channels" not in channels_da.coords:
            channels_da = channels_da.assign_coords(
                channels=np.arange(channels_da.sizes["channels"])
            )

    else:
        channels_da = xr.DataArray(
            resilience,
            dims=["channels"],
            coords={"channels": resilience}
        )

    if resilience_dataset is None:
        if fbs is None:
            raise ValueError(
                "Either 'resilience_dataset' or 'fbs' must be provided.")

        else:
            resilience_dataset = xr.zeros_like(fbs).expand_dims(
                dim={"channels": channels_da.coords["channels"].values}
            )
            items = item_parser(fbs, items)

    else:
        items = item_parser(resilience_dataset, items)

    if element not in resilience_dataset:
        raise KeyError(f"Element '{element}' not found in resilience dataset.")

    if "channels" not in resilience_dataset.dims:
        raise ValueError(
            "Resilience dataset must include a 'channels' dimension.")

    existing_channels = list(resilience_dataset.coords["channels"].values)
    incoming_channels = list(channels_da.coords["channels"].values)
    for channel in incoming_channels:
        if channel not in existing_channels:
            existing_channels.append(channel)

    resilience_dataset = resilience_dataset.reindex(
        channels=existing_channels, fill_value=0)

    item_selector = slice(None) if items is None else items

    current = resilience_dataset[element].loc[{"Item": item_selector}]

    shared_dims = [dim for dim in channels_da.dims if dim in current.dims]
    if shared_dims:
        channels_da = channels_da.reindex(
            {dim: current.coords[dim] for dim in shared_dims},
            fill_value=0
        )

    updated = 1 - (1 - current) * (1 - channels_da)
    resilience_dataset[element].loc[{"Item": item_selector}] = \
        updated.clip(min=0, max=1)

    return resilience_dataset

@pipeline_node(input_keys=['fbs', 'vulnerability_dataset', 'severity_dataset'])
def register_crisis(
    items: str | int | float | list[str] | list[int] | list[float] | tuple,
    element: str,
    vulnerability: list[float] | xr.DataArray,
    severity: float | xr.DataArray,
    vulnerability_dataset: xr.Dataset = None,
    severity_dataset: xr.DataArray = None,
    fbs: xr.Dataset = None,

) -> xr.Dataset:
    """
    Register the shocks for the specified item and element combination in the
    vulnerability dataset.

    Parameters
    ----------
    fbs : xr.Dataset
        The input food balance sheet dataset.
    items : str | int | float | list[str] | list[int] | list[float] | tuple
        Items to be impacted by the shocks registration.
    element : str
        The element of the FBS dataset to modify.
    vulnerability : list[float] | xr.DataArray
        The vulnerability values to be assigned to each channel.
    severity : float | xr.DataArray
        The magnitude of the shock to be registered.
    vulnerability_dataset : xr.Dataset
        The vulnerability dataset containing registered shocks for the
        specified item and element combination and for each channel.
    severity_dataset : xr.DataArray
        The severity dataset containing the severity values for the registered
        shocks.

    Returns
    -------
    xr.Dataset
        The modified vulnerability dataset with registered shocks.
    """
    
    if isinstance(vulnerability, xr.DataArray):
        channels_da = vulnerability.copy()

        if "channels" not in channels_da.dims:
            if channels_da.ndim != 1:
                raise ValueError(
                    "When 'channels' is a DataArray, it must either include a "
                    "'channels' dimension or be one-dimensional."
                )

            channels_da = channels_da.rename({channels_da.dims[0]: "channels"})

        if "channels" not in channels_da.coords:
            channels_da = channels_da.assign_coords(
                channels=np.arange(channels_da.sizes["channels"])
            )

    else:
        channels_da = xr.DataArray(
            vulnerability,
            dims=["channels"],
            coords={"channels": vulnerability}
        )

    if vulnerability_dataset is None and severity_dataset is None:
        if fbs is None:
            raise ValueError(
                "Either both 'vulnerability_dataset' and 'severity_dataset'"
                " or 'fbs' must be provided."
            )

        else:
            vulnerability_dataset = xr.zeros_like(fbs).expand_dims(
                dim={"channels": channels_da.coords["channels"].values}
            )

            severity_dataset = xr.zeros_like(fbs)

            items = item_parser(fbs, items)

    else:
        items = item_parser(vulnerability_dataset, items)

    if element not in vulnerability_dataset:
        raise KeyError(
            f"Element '{element}' not found in vulnerability dataset.")

    if element not in severity_dataset:
        raise KeyError(f"Element '{element}' not found in severity dataset.")

    if "channels" not in vulnerability_dataset.dims:
        raise ValueError(
            "Vulnerability dataset must include a 'channels' dimension.")

    existing_channels = list(vulnerability_dataset.coords["channels"].values)
    incoming_channels = list(channels_da.coords["channels"].values)
    for channel in incoming_channels:
        if channel not in existing_channels:
            existing_channels.append(channel)

    vulnerability_dataset = vulnerability_dataset.reindex(
        channels=existing_channels, fill_value=0)

    item_selector = slice(None) if items is None else items

    current_vulnerability = \
        vulnerability_dataset[element].loc[{"Item": item_selector}]
    
    current_severity = severity_dataset[element].loc[{"Item": item_selector}]

    shared_dims = [
        dim for dim in channels_da.dims if dim in current_vulnerability.dims]
    
    if shared_dims:
        channels_da = channels_da.reindex(
            {dim: current_vulnerability.coords[dim] for dim in shared_dims},
            fill_value=0
        )

    severity_new = severity
    if isinstance(severity_new, xr.DataArray):
        severity_shared_dims = [
            dim for dim in severity_new.dims if dim in current_severity.dims
        ]
        if severity_shared_dims:
            severity_new = severity_new.reindex(
                {dim: current_severity.coords[dim] for dim in severity_shared_dims},
                fill_value=0
            )

    # Update vulnerability values using severity-weighted averaging
    severity_total = current_severity + severity_new
    updated_vulnerability = xr.where(
        severity_total > 0,
        (
            current_severity * current_vulnerability
            + severity_new * channels_da
        ) / severity_total,
        current_vulnerability,
    )
    vulnerability_dataset[element].loc[{"Item": item_selector}] = \
        updated_vulnerability.clip(min=0, max=1)

    # Update severity values using diminishing returns formula
    updated_severity = 1 - (1 - current_severity) * (1 - severity)
    severity_dataset[element].loc[{"Item": item_selector}] = \
        updated_severity.clip(min=0, max=1)

    return vulnerability_dataset, severity_dataset

@pipeline_node(input_keys=[
    'fbs',
    'vulnerability_dataset',
    'severity_dataset',
    'resilience_dataset'
    ])
def process_shocks(
    fbs: xr.Dataset,
    vulnerability_dataset: xr.Dataset = None,
    severity_dataset: xr.DataArray = None,
    resilience_dataset: xr.DataArray = None,
    production_element: str = 'production',
    domestic_use_element: str | list[str] = 'food',
    imports_element: str | list[str] = 'imports',
):
    """
    Process the shocks by applying the registered vulnerability and severity to
    the food balance sheet (FBS) dataset.

    Parameters
    ----------
    fbs : xr.Dataset
        The input food balance sheet dataset to modify
    vulnerability_dataset : xr.Dataset
        The vulnerability dataset containing registered vulnerability channels.
    severity_dataset : xr.DataArray
        The severity dataset containing the severity values for the registered
        shocks.
    resilience_dataset : xr.DataArray
        The resilience dataset containing the resilience values for the
        registered shocks.

    Returns
    -------
    xr.Dataset
        The modified food balance sheet dataset with applied shocks.
    """

    # Check and align the datasets
    if "channels" not in vulnerability_dataset.dims:
        raise ValueError(
            "vulnerability_dataset must include a 'channels' dimension."
        )

    if "channels" not in resilience_dataset.dims:
        raise ValueError(
            "resilience_dataset must include a 'channels' dimension."
        )

    missing_in_resilience = [
        var for var in vulnerability_dataset.data_vars
        if var not in resilience_dataset.data_vars
    ]
    if missing_in_resilience:
        raise KeyError(
            "The following elements are missing in resilience_dataset: "
            f"{missing_in_resilience}"
        )

    vulnerability_aligned, resilience_aligned = xr.align(
        vulnerability_dataset,
        resilience_dataset,
        join="outer",
        fill_value=0,
    )

    
    effective_channel_protection = xr.Dataset()
    for element in vulnerability_dataset.data_vars:
        effective_channel_protection[element] = xr.dot(
            vulnerability_aligned[element],
            resilience_aligned[element],
            dim="channels",
        )

    severity_aligned, protection_aligned = xr.align(
        severity_dataset,
        effective_channel_protection,
        join="outer",
        fill_value=0,
    )

    impact = severity_aligned * (1 - protection_aligned)

    # Apply the impact to the FBS dataset
    fbs = fbs.copy()

    supply_elements = []
    for configured_elements in (production_element, imports_element):
        if isinstance(configured_elements, str):
            configured_elements = [configured_elements]

        for element in configured_elements:
            if element not in supply_elements:
                supply_elements.append(element)

    for element in supply_elements:
        if element not in impact:
            continue

        element_impact = impact[element].fillna(0)
        reduced_dims = [dim for dim in element_impact.dims if dim != "Item"]
        impacted_items_mask = element_impact != 0

        if reduced_dims:
            impacted_items_mask = impacted_items_mask.any(dim=reduced_dims)

        impacted_items = element_impact.coords["Item"].values[
            np.asarray(impacted_items_mask.values)
        ].tolist()

        if not impacted_items:
            continue

        element_severity = element_impact.sel(Item=impacted_items)
        fbs = rapid_supply_decrease(
            fbs=fbs,
            severity=element_severity,
            items=impacted_items,
            supply_element=element,
            domestic_use_element=domestic_use_element,
        )


    return fbs


