import pytest
import os
from netCDF4 import Dataset
import numpy as np
import os
import tempfile
import getpass
import socket

import ncas_amof_netcdf_template as nant


def test_main_process():
    nc = nant.create_netcdf.main(
        "ncas-aws-10", date="20221117", dimension_lengths={"time": 5}, return_open=True
    )
    assert os.path.exists("ncas-aws-10_iao_20221117_surface-met_v1.0.nc")
    assert nc["air_temperature"].size == 5
    nant.util.update_variable(nc, "air_temperature", [12.3, 14.54, 23.5, 12.4, 65.3])
    assert nc["air_temperature"].valid_min == np.float32(12.3)
    nc.close()
    os.remove("ncas-aws-10_iao_20221117_surface-met_v1.0.nc")


def test_add_attributes():
    # Create a temporary file for testing
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.close()

    # Create a netCDF file for testing
    ncfile = Dataset(temp_file.name, "w", format="NETCDF4")

    instrument_dict = {
        "info": {
            "Descriptor": "Instrument Description",
            "Manufacturer": "Manufacturer",
            "Model No.": "Model Number",
            "Serial Number": "Serial Number",
        },
        "common": {
            "attributes": {
                "source": {"Fixed Value": ""},
                "institution": {"Fixed Value": ""},
                "platform": {"Fixed Value": ""},
                "instrument_manufacturer": {"Fixed Value": ""},
                "instrument_model": {"Fixed Value": ""},
                "instrument_serial_number": {"Fixed Value": ""},
                "amf_vocabularies_release": {"Fixed Value": ""},
                "history": {"Fixed Value": ""},
                "last_revised_date": {"Fixed Value": ""},
                "deployment_mode": {"Fixed Value": ""},
                "defined_attribute": {"Fixed Value": "Defined Value"},
            }
        },
        "product1": {
            "attributes": {
                "attribute1": {"Fixed Value": "value1"},
                "attribute2": {"Fixed Value": "value2"},
            }
        },
    }

    product = "product1"
    created_time = "2022-01-01T00:00:00Z"
    location = "location1"
    loc = "land"
    use_local_files = None
    tag = "v1.2.3"
    user = getpass.getuser()
    machine = socket.gethostname()

    nant.create_netcdf.add_attributes(
        ncfile,
        instrument_dict,
        product,
        created_time,
        location,
        loc,
        use_local_files,
        tag,
    )

    history_text = (
        f"{created_time} - File created by {user} on {machine} using "
        f"the ncas_amof_netcdf_template v{nant.__version__} python package"
    )

    assert ncfile.getncattr("source") == instrument_dict["info"]["Descriptor"]
    assert (
        ncfile.getncattr("institution")
        == "National Centre for Atmospheric Science (NCAS)"
    )
    assert ncfile.getncattr("platform") == location
    assert (
        ncfile.getncattr("instrument_manufacturer")
        == instrument_dict["info"]["Manufacturer"]
    )
    assert ncfile.getncattr("instrument_model") == instrument_dict["info"]["Model No."]
    assert (
        ncfile.getncattr("instrument_serial_number")
        == instrument_dict["info"]["Serial Number"]
    )
    assert (
        ncfile.getncattr("amf_vocabularies_release")
        == "https://github.com/ncasuk/AMF_CVs/releases/tag/v1.2.3"
    )
    assert ncfile.getncattr("history") == history_text
    assert ncfile.getncattr("last_revised_date") == created_time
    assert ncfile.getncattr("deployment_mode") == loc
    assert (
        ncfile.getncattr("defined_attribute")
        == instrument_dict["common"]["attributes"]["defined_attribute"]["Fixed Value"]
    )
    assert ncfile.getncattr("attribute1") == "value1"
    assert ncfile.getncattr("attribute2") == "value2"

    # Close and delete the temporary file
    ncfile.close()
    os.remove(temp_file.name)


def test_add_dimensions():
    # Create a temporary file for testing
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.close()

    # Create a netCDF file for testing
    ncfile = Dataset(temp_file.name, "w", format="NETCDF4")

    instrument_dict = {
        "common": {
            "dimensions": {
                "time": None,
                "latitude": None,
                "longitude": None,
            }
        },
        "product1": {
            "dimensions": {
                "height": None,
            }
        },
    }

    product = "product1"
    dimension_lengths = {"time": 10, "latitude": 5, "longitude": 5, "height": 50}

    nant.create_netcdf.add_dimensions(
        ncfile, instrument_dict, product, dimension_lengths
    )

    assert "time" in ncfile.dimensions
    assert len(ncfile.dimensions["time"]) == dimension_lengths["time"]
    assert "latitude" in ncfile.dimensions
    assert len(ncfile.dimensions["latitude"]) == dimension_lengths["latitude"]
    assert "longitude" in ncfile.dimensions
    assert len(ncfile.dimensions["longitude"]) == dimension_lengths["longitude"]
    assert "height" in ncfile.dimensions
    assert len(ncfile.dimensions["height"]) == dimension_lengths["height"]

    # Close and delete the temporary file
    ncfile.close()
    os.remove(temp_file.name)


def test_add_variables():
    # Create a temporary file for testing
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.close()

    # Create a netCDF file for testing
    ncfile = Dataset(temp_file.name, "w", format="NETCDF4")

    instrument_dict = {
        "common": {
            "dimensions": {
                "time": None,
                "latitude": None,
                "longitude": None,
                "height": None,
            },
            "variables": {
                "variable1": {
                    "dimension": "time, latitude, longitude",
                    "type": "float32",
                    "_FillValue": "-9999.0",
                    "standard_name": "air_temperature",
                    "units": "K",
                }
            },
        },
        "product1": {
            "variables": {
                "variable2": {
                    "dimension": "time, height, latitude, longitude",
                    "type": "float32",
                    "_FillValue": "-9999.0",
                    "standard_name": "air_pressure_at_sea_level",
                    "units": "Pa",
                }
            }
        },
    }

    product = "product1"

    # need to add dimensions to be able to add variables
    ncfile.createDimension("time", 10)
    ncfile.createDimension("latitude", 5)
    ncfile.createDimension("longitude", 5)
    ncfile.createDimension("height", 50)

    nant.create_netcdf.add_variables(ncfile, instrument_dict, product)

    assert "variable1" in ncfile.variables
    assert ncfile.variables["variable1"].standard_name == "air_temperature"
    assert ncfile.variables["variable1"].units == "K"
    assert ncfile.variables["variable1"]._FillValue == -9999.0
    assert "dimension" not in ncfile.variables["variable1"].ncattrs()
    assert "type" not in ncfile.variables["variable1"].ncattrs()

    assert "variable2" in ncfile.variables
    assert ncfile.variables["variable2"].standard_name == "air_pressure_at_sea_level"
    assert ncfile.variables["variable2"].units == "Pa"
    assert ncfile.variables["variable2"]._FillValue == -9999.0
    assert "dimension" not in ncfile.variables["variable2"].ncattrs()
    assert "type" not in ncfile.variables["variable2"].ncattrs()

    # Close and delete the temporary file
    ncfile.close()
    os.remove(temp_file.name)


def test_make_netcdf():
    # Test parameters
    instrument = "ncas-aws-10"
    product = "surface-met"
    time = "20221117"
    instrument_dict = {
        "info": {
            "Mobile/Fixed (loc)": "Fixed - land",
            "Descriptor": "Instrument Description",
            "Manufacturer": "Manufacturer",
            "Model No.": "Model Number",
            "Serial Number": "Serial Number",
        },
        "common": {
            "dimensions": {
                "time": None,
                "latitude": None,
                "longitude": None,
            },
            "variables": {
                "variable1": {
                    "dimension": "time, latitude, longitude",
                    "type": "float32",
                    "_FillValue": "-9999.0",
                    "standard_name": "air_temperature",
                    "units": "K",
                }
            },
            "attributes": {
                "source": {"Fixed Value": ""},
                "institution": {"Fixed Value": ""},
                "platform": {"Fixed Value": ""},
                "instrument_manufacturer": {"Fixed Value": ""},
                "instrument_model": {"Fixed Value": ""},
                "instrument_serial_number": {"Fixed Value": ""},
                "amf_vocabularies_release": {"Fixed Value": ""},
                "history": {"Fixed Value": ""},
                "last_revised_date": {"Fixed Value": ""},
                "deployment_mode": {"Fixed Value": ""},
                "defined_attribute": {"Fixed Value": "Defined Value"},
            },
        },
        "surface-met": {
            "attributes": {
                "attribute1": {"Fixed Value": "value1"},
                "attribute2": {"Fixed Value": "value2"},
            },
            "variables": {
                "variable2": {
                    "dimension": "time, latitude, longitude",
                    "type": "float32",
                    "_FillValue": "-9999.0",
                    "standard_name": "air_pressure_at_sea_level",
                    "units": "Pa",
                }
            },
        },
    }
    loc = "land"
    dimension_lengths = {"time": 5, "latitude": 1, "longitude": 1}
    verbose = 0
    options = ""
    product_version = "1.0"
    file_location = "."
    use_local_files = None
    tag = "v1.2.3"
    return_open = True

    # Call the function
    ncfile = nant.create_netcdf.make_netcdf(
        instrument,
        product,
        time,
        instrument_dict,
        loc,
        dimension_lengths,
        verbose,
        options,
        product_version,
        file_location,
        use_local_files,
        tag,
        return_open,
    )

    # Check the returned object
    assert isinstance(ncfile, Dataset)
    assert ncfile.file_format == "NETCDF4_CLASSIC"

    # Check the file attributes
    assert ncfile.getncattr("source") == instrument_dict["info"]["Descriptor"]
    assert (
        ncfile.getncattr("institution")
        == "National Centre for Atmospheric Science (NCAS)"
    )
    assert (
        ncfile.getncattr("platform")
        == instrument_dict["info"]["Mobile/Fixed (loc)"].split("-")[-1].strip().lower()
    )
    assert (
        ncfile.getncattr("instrument_manufacturer")
        == instrument_dict["info"]["Manufacturer"]
    )
    assert ncfile.getncattr("instrument_model") == instrument_dict["info"]["Model No."]
    assert (
        ncfile.getncattr("instrument_serial_number")
        == instrument_dict["info"]["Serial Number"]
    )
    assert (
        ncfile.getncattr("amf_vocabularies_release")
        == "https://github.com/ncasuk/AMF_CVs/releases/tag/v1.2.3"
    )
    assert ncfile.getncattr("deployment_mode") == loc
    assert (
        ncfile.getncattr("defined_attribute")
        == instrument_dict["common"]["attributes"]["defined_attribute"]["Fixed Value"]
    )
    assert ncfile.getncattr("attribute1") == "value1"
    assert ncfile.getncattr("attribute2") == "value2"

    # Check the dimensions
    assert "time" in ncfile.dimensions
    assert ncfile.dimensions["time"].size == dimension_lengths["time"]

    # Close the file
    ncfile.close()
    os.remove(
        f"{file_location}/{instrument}_{loc}_{time}_{product}_v{product_version}.nc"
    )


@pytest.mark.parametrize(
    "instrument, products",
    [
        ("ncas-ceilometer-3", ["aerosol-backscatter", "cloud-base", "cloud-coverage"]),
        ("ncas-aws-10", ["surface-met"]),
    ],
)
def test_list_products(instrument, products):
    test_products = nant.create_netcdf.list_products(instrument)
    assert test_products == products


def test_make_product_netcdf():
    # Test with return_open=False
    nant.create_netcdf.make_product_netcdf(
        "product1",
        "instrument1",
        date="20221117",
        dimension_lengths={"time": 5},
        instrument_loc="location1",
        deployment_loc="land",
        verbose=0,
        options="",
        product_version="1.0",
        file_location=".",
        use_local_files=None,
        tag="latest",
        return_open=False,
    )
    assert os.path.exists("instrument1_location1_20221117_product1_v1.0.nc")

    # Test with return_open=True
    nc = nant.create_netcdf.make_product_netcdf(
        "product1",
        "instrument1",
        date="20221117",
        dimension_lengths={"time": 5},
        instrument_loc="location1",
        deployment_loc="land",
        verbose=0,
        options="",
        product_version="1.0",
        file_location=".",
        use_local_files=None,
        tag="latest",
        return_open=True,
    )
    assert isinstance(nc, Dataset)
    assert nc.dimensions["time"].size == 5

    # Clean up
    nc.close()
    os.remove("instrument1_location1_20221117_product1_v1.0.nc")
