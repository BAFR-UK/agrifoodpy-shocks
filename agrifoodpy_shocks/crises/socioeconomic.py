import xarray as xr
from agrifoodpy.pipeline import pipeline_node

@pipeline_node(input_keys=['fbs'])
def rapid_demand_shift(
    fbs: xr.Dataset,
    severity: float | xr.DataArray,
    items: str | int | float | list[str] | list[int] | list[float] | tuple,
    demand_element: str = 'food'
) -> xr.Dataset:
    """
    Apply a rapid demand shift to the food balance sheet (FBS) dataset,
    while balancing supply and demand to maintain consistency.

    Parameters
    ----------
    fbs : xr.Dataset
        The input food balance sheet dataset.
    severity : float | xr.DataArray
        The factor by which to shift demand.
    demand_element : str, optional
        The element of the FBS dataset to modify, by default 'food'.
    items : str | int | float | list[str] | list[int] | list[float] | tuple
        Items to be impacted by the demand shift.

    Returns
    -------
    xr.Dataset
        The modified food balance sheet dataset with shifted demand.
    """
    
    fbs = fbs.copy()
    for item in items:
        fbs[demand_element].loc[dict(item=item)] = fbs[demand_element].loc[dict(item=item)] * severity
    return fbs