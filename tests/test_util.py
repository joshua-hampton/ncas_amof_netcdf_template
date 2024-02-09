from ncas_amof_netcdf_template import util
import csv
import os
import tempfile
from netCDF4 import Dataset
import numpy as np
import datetime as dt
import pytest


def test_check_int():
    assert util.check_int("12321")
    assert not util.check_int("12.432")
    assert not util.check_int("one")


def test_check_float():
    assert util.check_float("12321")
    assert util.check_float("12.432")
    assert not util.check_float("one")


def test_get_metadata():
    # Create a temporary CSV file
    with tempfile.NamedTemporaryFile(delete=False, mode="w", newline="") as temp:
        writer = csv.writer(temp)
        writer.writerow(["key1", "value1"])
        writer.writerow(["key2", "value2", "extra"])
        writer.writerow(["key3"])
        temp_path = temp.name

    # Call the get_metadata function with the temporary CSV file
    result = util.get_metadata(temp_path)

    # Check the result
    assert result == {"key1": "value1", "key2": "value2,extra"}

    # Delete the temporary CSV file
    os.remove(temp_path)


def test_get_metadata_with_empty_file():
    # Create a temporary CSV file
    with tempfile.NamedTemporaryFile(delete=False, mode="w", newline="") as temp:
        temp_path = temp.name

    # Call the get_metadata function with the empty temporary CSV file
    result = util.get_metadata(temp_path)

    # Check the result
    assert result == {}

    # Delete the temporary CSV file
    os.remove(temp_path)


def test_add_metadata_to_netcdf():
    # Create a temporary netCDF file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".nc") as temp:
        ncfile = Dataset(temp.name, "w", format="NETCDF4")
        ncfile.createDimension("dim", None)
        ncfile.createVariable("latitude", "f4", ("dim",))
        ncfile.createVariable("longitude", "f4", ("dim",))
        ncfile.key1 = "old_value1"
        ncfile.key3 = "old_value3"
        ncfile.key4 = "old_value4"
        temp_path = temp.name

    # Create a temporary CSV file with metadata
    #with tempfile.NamedTemporaryFile(delete=False, mode="w", newline="") as temp:
    #with open("./test_csv", "w") as temp:
    #    writer = csv.writer(temp)
    #    writer.writerow(["key1", "value1"])
    #    writer.writerow(["key2", "value2"])
    #    writer.writerow(["key3", 12])
    #    writer.writerow(["key4", str("12")])
    #    writer.writerow(["latitude", "12.34"])
    #    writer.writerow(["longitude", "56.78"])
    #    metadata_path = temp.name

    with open("tests/test_csv.csv", "rt") as meta:
        raw_metadata = {}
        metaread = csv.reader(meta)
        metaread = meta.readlines()
        for row in metaread:
            if len(row.split(",")) >= 2:
                raw_metadata[row.split(",")[0]] = ",".join(row.split(",")[1:]).strip()
    
    assert raw_metadata.keys() == {"key1", "key2", "key3", "key4", "latitude", "longitude"}
    assert raw_metadata["key4"] == "'12'"

    # Call the add_metadata_to_netcdf function with the temporary netCDF file and the temporary CSV file
    util.add_metadata_to_netcdf(ncfile, "tests/test_csv.csv")

    # Check the result
    # overwrite existing
    assert ncfile.getncattr("key1") == "value1"
    # non-existing ignored
    assert "key2" not in ncfile.ncattrs()
    # integer in csv is integer in netCDF
    assert ncfile.getncattr("key3") == 12
    # string number in csv is tidy string in netCDF
    assert ncfile.getncattr("key4") == "12"
    # latitude and longitude are added as variables
    assert np.allclose(ncfile.variables["latitude"][:], 12.34)
    assert np.allclose(ncfile.variables["longitude"][:], 56.78)

    ncfile.close()

    # Delete the temporary netCDF file and the temporary CSV file
    os.remove(temp_path)
    #os.remove(metadata_path)


def test_get_times():
    # Prepare a list of datetime objects
    dt_times = [
        dt.datetime(2022, 1, 1, 0, 0, 0),
        dt.datetime(2022, 1, 1, 12, 0, 0),
        dt.datetime(2022, 1, 2, 0, 0, 0),
    ]

    # Call the get_times function with the list of datetime objects
    result = util.get_times(dt_times)

    # Check the result
    assert np.allclose(
        result[0], [1640995200.0, 1641038400.0, 1641081600.0]
    )  # unix_times
    assert np.allclose(result[1], [1.0, 1.5, 2.0])  # doy
    assert result[2] == [2022, 2022, 2022]  # years
    assert result[3] == [1, 1, 1]  # months
    assert result[4] == [1, 1, 2]  # days
    assert result[5] == [0, 12, 0]  # hours
    assert result[6] == [0, 0, 0]  # minutes
    assert np.allclose(result[7], [0.0, 0.0, 0.0])  # seconds
    assert result[8] == 1640995200.0  # time_coverage_start_dt
    assert result[9] == 1641081600.0  # time_coverage_end_dt
    assert result[10] == "202201"  # file_date

    # Same again but with date times all within 1 second
    # Prepare a list of datetime objects
    dt_times = [
        dt.datetime(2022, 1, 1, 1, 5, 2, 1),
        dt.datetime(2022, 1, 1, 1, 5, 2, 2),
        dt.datetime(2022, 1, 1, 1, 5, 2, 3),
    ]

    # Call the get_times function with the list of datetime objects
    result = util.get_times(dt_times)

    # Check the result
    assert np.allclose(
        result[0], [1640999102.000001, 1640999102.000002, 1640999102.000003]
    )  # unix_times
    assert np.allclose(
        result[1], [1.0451631944433408, 1.0451643518524039, 1.0451655092587075]
    )  # doy
    assert result[2] == [2022, 2022, 2022]  # years
    assert result[3] == [1, 1, 1]  # months
    assert result[4] == [1, 1, 1]  # days
    assert result[5] == [1, 1, 1]  # hours
    assert result[6] == [5, 5, 5]  # minutes
    assert np.allclose(result[7], [2.000001, 2.000002, 2.000003])  # seconds
    assert result[8] == 1640999102.000001  # time_coverage_start_dt
    assert result[9] == 1640999102.000003  # time_coverage_end_dt
    assert result[10] == "20220101-010502"  # file_date


def test_get_times_with_incompatible_dates():
    # Prepare a list of datetime objects
    dt_times = [
        dt.datetime(2021, 12, 31, 23, 59, 59),
        dt.datetime(2022, 1, 1, 0, 0, 0),
    ]

    # Call the get_times function with the list of datetime objects and check if it raises a ValueError
    with pytest.raises(ValueError, match="Incompatible dates - data from over 2 years"):
        util.get_times(dt_times)


def test_update_variable():
    # Create a temporary netCDF file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".nc") as temp:
        ncfile = Dataset(temp.name, "w", format="NETCDF4")
        ncfile.createDimension("dim", 3)
        var = ncfile.createVariable("var", "f4", ("dim",))  # f4 is a float32
        var.valid_min = 0.0
        var.valid_max = 1.0
        temp_path = temp.name

    # Call the update_variable function with the temporary netCDF file and new data
    util.update_variable(ncfile, "var", [0.5, 0.6, 0.7])

    # Check the result
    assert np.allclose(ncfile.variables["var"][:], [0.5, 0.6, 0.7])
    assert ncfile.variables["var"].valid_min == np.float32(0.5)
    assert ncfile.variables["var"].valid_max == np.float32(0.7)

    ncfile.close()

    # Delete the temporary netCDF file
    os.remove(temp_path)


def test_update_variable_with_qc_flag():
    # Create a temporary netCDF file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".nc") as temp:
        ncfile = Dataset(temp.name, "w", format="NETCDF4")
        ncfile.createDimension("dim", 3)
        var = ncfile.createVariable("qc_var", "i4", ("dim",))
        var.flag_values = [0, 1, 2]
        temp_path = temp.name

    # Call the update_variable function with the temporary netCDF file and new data
    util.update_variable(ncfile, "qc_var", [0, 1, 2])

    # Check the result
    assert np.allclose(ncfile.variables["qc_var"][:], [0, 1, 2])

    ncfile.close()

    # Delete the temporary netCDF file
    os.remove(temp_path)


def test_update_variable_with_invalid_qc_flag():
    # Create a temporary netCDF file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".nc") as temp:
        ncfile = Dataset(temp.name, "w", format="NETCDF4")
        ncfile.createDimension("dim", 3)
        var = ncfile.createVariable("qc_var", "i4", ("dim",))
        var.flag_values = [0, 1, 2]
        temp_path = temp.name

    # Call the update_variable function with the temporary netCDF file and invalid data and check if it raises a ValueError
    with pytest.raises(
        ValueError,
        match=r"Invalid data being added to QC variable, only \[0, 1, 2\] are allowed.",
    ):
        util.update_variable(ncfile, "qc_var", [0, 1, 3])

    ncfile.close()

    # Delete the temporary netCDF file
    os.remove(temp_path)


def test_zero_pad_number():
    # Test single digit number
    result = util.zero_pad_number(3)
    assert result == "03"

    # Test multiple digit number
    result = util.zero_pad_number(12)
    assert result == "12"

    # Test zero
    result = util.zero_pad_number(0)
    assert result == "00"

    # Test negative single digit number
    result = util.zero_pad_number(-3)
    assert result == "-3"

    # Test negative multiple digit number
    result = util.zero_pad_number(-12)
    assert result == "-12"
