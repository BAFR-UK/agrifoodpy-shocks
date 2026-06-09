import xarray as xr
from agrifoodpy.pipeline import pipeline_node
from agrifoodpy.utils.dict_utils import item_parser
from agrifoodpy.food.food import FoodBalanceSheet

@pipeline_node(input_keys=['fbs'])
def rapid_production_decrease(
    fbs: xr.Dataset,
    severity: float | xr.DataArray,
    items: str | int | float | list[str] | list[int] | list[float] | tuple,
    production_element: str = 'production',
    domestic_use_element: str | list[str] = 'food',
) -> xr.Dataset:
    """
    Apply a rapid production decrease to the food balance sheet (FBS) dataset,
    while balancing supply and demand to maintain consistency.

    This model simulates a sudden drop in production for specific items,
    which can be caused by environmental shocks such as droughts, floods, or
    pest outbreaks. The decrease in production is applied to the specified
    production element, and the corresponding decrease in domestic use is
    applied to maintain consistency between supply and domestic use elements.

    Parameters
    ----------
    fbs : xr.Dataset
        The input food balance sheet dataset.
    severity : float | xr.DataArray
        The factor by which to decrease production.
    production_element : str, optional
        The element of the FBS dataset to modify, by default 'production'.
    domestic_use_element : str | list[str], optional
        The elements of the FBS dataset representing domestic use, by default
        'food'.
    items : str | int | float | list[str] | list[int] | list[float] | tuple
        Items to be impacted by the production decrease.

    Returns
    -------
    xr.Dataset
        The modified food balance sheet dataset with decreased production.
    """
    
    fbs = fbs.copy()
    ref = fbs.copy()

    items = item_parser(fbs, items)

    # Apply the production decrease to the specified items
    fbs = fbs.fbs.scale_element(
        production_element,
        severity,
        items=items
    )

    # Calculate the change in production
    delta_prod = (ref[production_element]
                  - fbs[production_element]).sel(Item = items)
    
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
    dom_scale = 1 - (delta_prod / total_dom)

    for elem in domestic_use_element:
        fbs = fbs.fbs.scale_element(
            elem,
            dom_scale,
            items=items
        )

    return fbs