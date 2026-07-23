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

if __name__ == "__main__":
    test_data = generate_test_data()
    print(test_data)

    # Save the test dataset to a NetCDF file
    test_data.to_netcdf("test_data.nc")

    test_data_without_years = test_data.isel(Year=-1).drop_vars("Year")
    print(test_data_without_years)

    test_data_without_years.to_netcdf("test_data_without_years.nc")