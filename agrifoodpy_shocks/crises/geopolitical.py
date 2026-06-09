import xarray as xr
from agrifoodpy.pipeline import pipeline_node
from agrifoodpy.utils.dict_utils import item_parser
from agrifoodpy.food.food import FoodBalanceSheet

@pipeline_node(input_keys=['fbs'])
def rapid_imports_decrease(
    fbs: xr.Dataset,
    severity: float | xr.DataArray,
    items: str | int | float | list[str] | list[int] | list[float] | tuple,
    imports_element: str = 'imports',
    domestic_use_element: str | list[str] = 'food'
) -> xr.Dataset:
    """
    Apply a rapid imports decrease to the food balance sheet (FBS) dataset,
    while balancing supply and demand to maintain consistency.

    Parameters
    ----------
    fbs : xr.Dataset
        The input food balance sheet dataset.
    severity : float | xr.DataArray
        The factor by which to decrease imports.
    imports_element : str, optional
        The element of the FBS dataset to modify, by default 'imports'.
    domestic_use_element : str | list[str], optional
        The elements of the FBS dataset representing domestic use, by default
        'food'.
    items : str | int | float | list[str] | list[int] | list[float] | tuple
        Items to be impacted by the imports decrease.

    Returns
    -------
    xr.Dataset
        The modified food balance sheet dataset with decreased imports.
    """
    
    fbs = fbs.copy()
    ref = fbs.copy()

    items = item_parser(fbs, items)

    # Apply the imports decrease to the specified items
    fbs = fbs.fbs.scale_element(
        imports_element,
        severity,
        items=items
    )

    # Calculate the change in imports
    delta_imports = (ref[imports_element]
                  - fbs[imports_element]).sel(Item = items)
    
    if isinstance(domestic_use_element, str):
        domestic_use_element = [domestic_use_element]

    # Calculate the total domestic use for the specified items
    total_dom = (
        fbs[domestic_use_element]
        .sel(Item = items)
        .to_array("domestic_use_elements")
        .sum(dim="domestic_use_elements")
    )

    # Calculate the scaling factor for domestic use to maintain consistency
    dom_scale = 1 - (delta_imports / total_dom)

    for elem in domestic_use_element:
        fbs = fbs.fbs.scale_element(
            elem,
            dom_scale,
            items=items
        )

    return fbs