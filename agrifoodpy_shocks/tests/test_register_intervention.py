import pytest
import xarray as xr

from agrifoodpy_shocks.resilience.engine import register_intervention


def _build_fbs_with_year() -> xr.Dataset:
    return xr.Dataset(
        data_vars={
            "production": (
                ["Year", "Item"],
                [
                    [100.0, 80.0],
                    [120.0, 90.0],
                ],
            ),
        },
        coords={"Year": [2020, 2021], "Item": ["Beef", "Apples"]},
    )


def _build_fbs_without_year() -> xr.Dataset:
    return xr.Dataset(
        data_vars={
            "production": (
                ["Item"],
                [100.0, 80.0],
            ),
        },
        coords={"Item": ["Beef", "Apples"]},
    )


def test_register_intervention_without_adoption_keeps_existing_behavior():
    fbs = _build_fbs_with_year()

    resilience = xr.DataArray(
        [0.8, 0.2],
        dims=["channels"],
        coords={"channels": ["Bio", "Log"]},
    )

    result = register_intervention(
        items="Beef",
        element="production",
        resilience=resilience,
        fbs=fbs,
    )

    expected_beef = xr.DataArray(
        [[0.8, 0.8], [0.2, 0.2]],
        dims=["channels", "Year"],
        coords={"channels": ["Bio", "Log"], "Year": [2020, 2021]},
    )

    xr.testing.assert_allclose(
        result["production"].sel(Item="Beef").transpose("channels", "Year"),
        expected_beef,
    )
    xr.testing.assert_allclose(
        result["production"].sel(Item="Apples"),
        0,
    )


def test_register_intervention_with_adoption_modulates_resilience_over_years():
    fbs = _build_fbs_with_year()

    resilience = xr.DataArray(
        [0.8, 0.2],
        dims=["channels"],
        coords={"channels": ["Bio", "Log"]},
    )
    adoption = xr.DataArray(
        [0.0, 0.5],
        dims=["Year"],
        coords={"Year": [2020, 2021]},
    )

    result = register_intervention(
        items="Beef",
        element="production",
        resilience=resilience,
        adoption=adoption,
        fbs=fbs,
    )

    expected_beef = xr.DataArray(
        [[0.0, 0.4], [0.0, 0.1]],
        dims=["channels", "Year"],
        coords={"channels": ["Bio", "Log"], "Year": [2020, 2021]},
    )

    xr.testing.assert_allclose(
        result["production"].sel(Item="Beef").transpose("channels", "Year"),
        expected_beef,
    )


def test_register_intervention_with_yearly_resilience_and_adoption():
    fbs = _build_fbs_with_year()

    resilience = xr.DataArray(
        [[0.2, 0.6], [0.4, 0.8]],
        dims=["Year", "channels"],
        coords={"Year": [2020, 2021], "channels": ["Bio", "Log"]},
    )
    adoption = xr.DataArray(
        [0.5, 1.0],
        dims=["Year"],
        coords={"Year": [2020, 2021]},
    )

    result = register_intervention(
        items="Beef",
        element="production",
        resilience=resilience,
        adoption=adoption,
        fbs=fbs,
    )

    expected_beef = xr.DataArray(
        [[0.1, 0.4], [0.3, 0.8]],
        dims=["channels", "Year"],
        coords={"channels": ["Bio", "Log"], "Year": [2020, 2021]},
    )

    xr.testing.assert_allclose(
        result["production"].sel(Item="Beef").transpose("channels", "Year"),
        expected_beef,
    )


def test_register_intervention_adoption_requires_year_dimension_in_target():
    fbs = _build_fbs_without_year()
    adoption = xr.DataArray(
        [0.0, 0.5],
        dims=["Year"],
        coords={"Year": [2020, 2021]},
    )

    with pytest.raises(ValueError, match="does not include a 'Year' dimension"):
        register_intervention(
            items="Beef",
            element="production",
            resilience=[0.8, 0.2],
            adoption=adoption,
            fbs=fbs,
        )
