import pytest
import os
from netCDF4 import Dataset
import numpy as np
import tempfile
import getpass
import socket
import datetime as dt

import ncas_amof_netcdf_template as nant


def test_main_process():
    nc = nant.create_netcdf.main(
        "ncas-aws-10", date="20221117", dimension_lengths={"time": 5}
    )
    assert os.path.exists("ncas-aws-10_iao_20221117_surface-met_v1.0.nc")
    assert nc["air_temperature"].size == 5
    nant.util.update_variable(nc, "air_temperature", [12.3, 14.54, 23.5, 12.4, 65.3])
    assert nc["air_temperature"].valid_min == np.float32(12.3)
    assert nc.getncattr("platform") == "iao"
    nc.close()
    os.remove("ncas-aws-10_iao_20221117_surface-met_v1.0.nc")

    # Same tests but defining platform
    nc = nant.create_netcdf.main(
        "ncas-aws-10",
        platform="somewhere-else",
        date="20221117",
        dimension_lengths={"time": 5},
    )
    assert os.path.exists("ncas-aws-10_somewhere-else_20221117_surface-met_v1.0.nc")
    assert nc["air_temperature"].size == 5
    nant.util.update_variable(nc, "air_temperature", [12.3, 14.54, 23.5, 12.4, 65.3])
    assert nc["air_temperature"].valid_min == np.float32(12.3)
    assert nc.getncattr("platform") == "somewhere-else"
    nc.close()
    os.remove("ncas-aws-10_somewhere-else_20221117_surface-met_v1.0.nc")


@pytest.mark.parametrize(
    "created_time",
    [
        "2022-01-01T00:00:00Z",
        None,
    ],
)
def test_add_attributes(created_time):
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
            "instrument_name": "instrument-name",
            "Mobile/Fixed (loc)": "location1",
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
    location = "location1"
    loc = "land"
    use_local_files = None
    tag = "v2.0.0"
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
        == "https://github.com/ncasuk/AMF_CVs/releases/tag/v2.0.0"
    )
    if created_time is not None:
        assert ncfile.getncattr("history") == history_text
        assert ncfile.getncattr("last_revised_date") == created_time
    else:
        # account for possibility of running test more than one second after making
        # file, hoping not to be unlucky enough to run just before midnight
        assert ncfile.getncattr("last_revised_date").startswith(
            dt.datetime.now(tz=dt.timezone.utc).strftime("%Y%m%dT")
        )
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

    with pytest.raises(ValueError, match=r".+'product' must be given.+"):
        # Create a temporary file for testing
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file.close()

        # Create a netCDF file for testing
        ncfile = Dataset(temp_file.name, "w", format="NETCDF4")
        nant.create_netcdf.add_attributes(
            ncfile,
            instrument_dict=instrument_dict,
            created_time=created_time,
            location=location,
            loc=loc,
            use_local_files=use_local_files,
            tag=tag,
        )

    with pytest.raises(ValueError, match="No instrument file info given"):
        # Create a temporary file for testing
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file.close()

        # Create a netCDF file for testing
        ncfile = Dataset(temp_file.name, "w", format="NETCDF4")
        nant.create_netcdf.add_attributes(
            ncfile,
        )


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
                    "compression": "zlib",
                },
                "variable3": {
                    "dimension": "time, height, latitude, longitude",
                    "type": "float32",
                    "units": "K",
                    "chunksizes": [2, 10, 5, 5],
                    "compression": "zlib",
                    "complevel": 8,
                    "shuffle": False,
                },
            }
        },
        "info": {
            "instrument_name": "instrument-name",
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
    assert not ncfile.variables["variable1"].filters()["zlib"]
    assert not ncfile.variables["variable1"].filters()["shuffle"]
    assert ncfile.variables["variable1"].filters()["complevel"] == 0
    assert ncfile.variables["variable1"].chunking() == "contiguous"
    assert "dimension" not in ncfile.variables["variable1"].ncattrs()
    assert "type" not in ncfile.variables["variable1"].ncattrs()

    assert "variable2" in ncfile.variables
    assert ncfile.variables["variable2"].standard_name == "air_pressure_at_sea_level"
    assert ncfile.variables["variable2"].units == "Pa"
    assert ncfile.variables["variable2"]._FillValue == -9999.0
    assert ncfile.variables["variable2"].filters()["zlib"]
    assert ncfile.variables["variable2"].filters()["shuffle"]
    assert ncfile.variables["variable2"].filters()["complevel"] == 4
    assert ncfile.variables["variable2"].chunking() == [10, 50, 5, 5]
    assert "dimension" not in ncfile.variables["variable2"].ncattrs()
    assert "type" not in ncfile.variables["variable2"].ncattrs()

    assert "variable3" in ncfile.variables
    assert "standard_name" not in ncfile.variables["variable3"].ncattrs()
    assert ncfile.variables["variable3"].units == "K"
    assert "_FillValue" not in ncfile.variables["variable3"].ncattrs()
    assert ncfile.variables["variable3"].filters()["zlib"]
    assert not ncfile.variables["variable3"].filters()["shuffle"]
    assert ncfile.variables["variable3"].filters()["complevel"] == 8
    assert ncfile.variables["variable3"].chunking() == [2, 10, 5, 5]
    assert "dimension" not in ncfile.variables["variable3"].ncattrs()
    assert "type" not in ncfile.variables["variable3"].ncattrs()

    # Close and delete the temporary file
    ncfile.close()
    os.remove(temp_file.name)


@pytest.mark.parametrize(
    "compression, complevel, shuffle",
    [
        (None, None, None),
        ("zlib", 5, True),
        ("zlib", 5, False),
        ("zlib", 5, None),
        ({"variable2": "zlib"}, {"variable2": 5}, {"variable2": False}),
    ],
)
def test_make_netcdf(compression, complevel, shuffle):
    # Test parameters
    instrument = "ncas-aws-10"
    platform = "iao"
    product = "surface-met"
    time = "20221117"
    instrument_dict = {
        "info": {
            "Mobile/Fixed (loc)": f"Fixed - {platform}",
            "Descriptor": "Instrument Description",
            "Manufacturer": "Manufacturer",
            "Model No.": "Model Number",
            "Serial Number": "Serial Number",
            "instrument_name": instrument,
        },
        "common": {
            "dimensions": {
                "time": {"Length": 5},
                "latitude": {"Length": 1},
                "longitude": {"Length": 1},
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
                    "dimension": "time",
                    "type": "float32",
                    "_FillValue": "-9999.0",
                    "standard_name": "air_pressure_at_sea_level",
                    "units": "Pa",
                },
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
    tag = "v2.0.0"
    chunk_by_dimension = {"time": 2}

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
        chunk_by_dimension=chunk_by_dimension,
        compression=compression,
        complevel=complevel,
        shuffle=shuffle,
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
        == "https://github.com/ncasuk/AMF_CVs/releases/tag/v2.0.0"
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

    # Check chunking
    if compression == "zlib":
        assert ncfile.variables["variable1"].chunking() == [5, 1, 1]
        assert ncfile.variables["variable1"].filters()["complevel"] == 5
        assert ncfile.variables["variable1"].filters()["zlib"]
        if isinstance(shuffle, bool) and not shuffle:
            assert not ncfile.variables["variable1"].filters()["shuffle"]
        else:
            assert ncfile.variables["variable1"].filters()["shuffle"]
    else:
        assert ncfile.variables["variable1"].chunking() == "contiguous"
        assert ncfile.variables["variable1"].filters()["complevel"] == 0
        assert not ncfile.variables["variable1"].filters()["zlib"]
        assert not ncfile.variables["variable1"].filters()["shuffle"]

    if (isinstance(shuffle, bool) and shuffle) or (
        compression is not None and shuffle is None
    ):
        assert ncfile.variables["variable2"].filters()["shuffle"]
    else:
        assert not ncfile.variables["variable2"].filters()["shuffle"]
    assert ncfile.variables["variable2"].chunking() == [2]

    # Close the file
    ncfile.close()
    os.remove(
        f"{file_location}/{instrument}_{platform}_{time}_{product}_v{product_version}.nc"
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
    # Test with return_open=False and using instrument_loc
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
    )
    assert os.path.exists("instrument1_location1_20221117_product1_v1.0.nc")
    nc.close()

    # Test with platform instead of instrument_loc
    nc = nant.create_netcdf.make_product_netcdf(
        "product1",
        "instrument1",
        date="20221117",
        dimension_lengths={"time": 5},
        platform="location1",
        deployment_loc="land",
        verbose=0,
        options="",
        product_version="1.0",
        file_location=".",
        use_local_files=None,
        tag="latest",
    )
    assert os.path.exists("instrument1_location1_20221117_product1_v1.0.nc")
    assert isinstance(nc, Dataset)
    assert nc.dimensions["time"].size == 5

    # Clean up
    nc.close()
    os.remove("instrument1_location1_20221117_product1_v1.0.nc")
