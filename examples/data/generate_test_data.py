import xarray as xr

def generate_test_data() -> xr.Dataset:
    """
    Generate a test dataset for demonstration purposes.

    Returns
    -------
    xr.Dataset
        A test dataset containing sample data.
    """
    # Create a sample dataset with dimensions and coordinates
    items = ["Beef", "Apples"]
    years = [2020, 2021]

    ds = xr.Dataset(
        data_vars=dict(
            imports=(["Year", "Item"], [[10, 20], [30, 40]]),
            exports=(["Year", "Item"], [[5, 10], [15, 20]]),
            production=(["Year", "Item"], [[50, 60], [70, 80]]),
            domestic=(["Year", "Item"], [[55, 70], [85, 100]])
            ),

    coords=dict(Item=("Item", items), Year=("Year", years))
    )
    
    return ds

def generate_test_data_high_dimensional() -> xr.Dataset:
    """
    Generate a high-dimensional test dataset for demonstration purposes.

    Returns
    -------
    xr.Dataset
        A high-dimensional test dataset containing sample data.
    """
    items = ["Beef", "Apples", "Wheat", "Poultry"]
    years = list(range(2020, 2051))

    imports = []
    exports = []
    production = []
    domestic = []

    for year_index, _year in enumerate(years):
        year_imports = []
        year_exports = []
        year_production = []
        year_domestic = []

        for item_index, _item in enumerate(items):
            import_value = 10 + (year_index * 2) + (item_index * 3)
            export_value = 5 + year_index + item_index
            production_value = 60 + (year_index * 4) + (item_index * 5)
            domestic_value = import_value + production_value - export_value

            year_imports.append(import_value)
            year_exports.append(export_value)
            year_production.append(production_value)
            year_domestic.append(domestic_value)

        imports.append(year_imports)
        exports.append(year_exports)
        production.append(year_production)
        domestic.append(year_domestic)

    ds = xr.Dataset(
        data_vars=dict(
            imports=(["Year", "Item"], imports),
            exports=(["Year", "Item"], exports),
            production=(["Year", "Item"], production),
            domestic=(["Year", "Item"], domestic)
        ),
        coords=dict(Item=("Item", items), Year=("Year", years))
    )

    return ds

if __name__ == "__main__":
    test_data = generate_test_data()
    print(test_data)
    test_data.to_netcdf("test_data.nc")

    test_data_without_years = test_data.isel(Year=-1).drop_vars("Year")
    print(test_data_without_years)
    test_data_without_years.to_netcdf("test_data_without_years.nc")

    test_data_high_dimensional = generate_test_data_high_dimensional()
    print(test_data_high_dimensional)
    test_data_high_dimensional.to_netcdf("test_data_high_dimensional.nc")