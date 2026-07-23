import xarray as xr

from agrifoodpy_shocks.crises.supply import rapid_supply_decrease
from agrifoodpy_shocks.resilience.engine import process_shocks


def test_process_shocks_applies_supply_impacts_via_rapid_supply_decrease():
    items = ["Beef", "Apples"]
    years = [2020, 2021]
    channels = ["channel_0"]

    fbs = xr.Dataset(
        data_vars={
            "production": (["Year", "Item"], [[100.0, 80.0], [120.0, 90.0]]),
            "imports": (["Year", "Item"], [[20.0, 10.0], [30.0, 15.0]]),
            "food": (["Year", "Item"], [[60.0, 50.0], [70.0, 55.0]]),
        },
        coords={"Year": years, "Item": items},
    )

    vulnerability_dataset = xr.Dataset(
        data_vars={
            "production": (
                ["channels", "Year", "Item"],
                [[[1.0, 0.0], [1.0, 0.0]]],
            ),
            "imports": (
                ["channels", "Year", "Item"],
                [[[0.0, 0.5], [0.0, 0.5]]],
            ),
            "food": (
                ["channels", "Year", "Item"],
                [[[0.0, 0.0], [0.0, 0.0]]],
            ),
        },
        coords={"channels": channels, "Year": years, "Item": items},
    )

    severity_dataset = xr.Dataset(
        data_vars={
            "production": (["Year", "Item"], [[0.2, 0.0], [0.1, 0.0]]),
            "imports": (["Year", "Item"], [[0.0, 0.4], [0.0, 0.2]]),
            "food": (["Year", "Item"], [[0.0, 0.0], [0.0, 0.0]]),
        },
        coords={"Year": years, "Item": items},
    )

    resilience_dataset = xr.Dataset(
        data_vars={
            "production": (
                ["channels", "Year", "Item"],
                [[[0.25, 0.0], [0.25, 0.0]]],
            ),
            "imports": (
                ["channels", "Year", "Item"],
                [[[0.0, 0.4], [0.0, 0.4]]],
            ),
            "food": (
                ["channels", "Year", "Item"],
                [[[0.0, 0.0], [0.0, 0.0]]],
            ),
        },
        coords={"channels": channels, "Year": years, "Item": items},
    )

    result = process_shocks(
        fbs=fbs,
        vulnerability_dataset=vulnerability_dataset,
        severity_dataset=severity_dataset,
        resilience_dataset=resilience_dataset,
        production_element="production",
        imports_element="imports",
        domestic_use_element="food",
    )

    effective_channel_protection = xr.Dataset()
    for element in vulnerability_dataset.data_vars:
        effective_channel_protection[element] = xr.dot(
            vulnerability_dataset[element],
            resilience_dataset[element],
            dim="channels",
        )

    impact = severity_dataset * (1 - effective_channel_protection)

    expected = rapid_supply_decrease(
        fbs=fbs,
        severity=impact["production"].sel(Item=["Beef"]),
        items=["Beef"],
        supply_element="production",
        domestic_use_element="food",
    )
    expected = rapid_supply_decrease(
        fbs=expected,
        severity=impact["imports"].sel(Item=["Apples"]),
        items=["Apples"],
        supply_element="imports",
        domestic_use_element="food",
    )

    xr.testing.assert_equal(result, expected)