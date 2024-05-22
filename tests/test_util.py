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


def test_check_type_convert():
    assert util.check_type_convert("12321", int)
    assert util.check_type_convert("12.432", float)
    assert util.check_type_convert("1", str)
    assert util.check_type_convert("1", int)
    assert util.check_type_convert("1", float)
    assert util.check_type_convert("one", str)
    assert not util.check_type_convert("one", int)
    assert not util.check_type_convert("one", float)


def test_get_metadata():
    # Create a temporary CSV file
    with tempfile.NamedTemporaryFile(delete=False, mode="w", newline="") as temp:
        writer = csv.writer(temp)
        writer.writerow(["key1", "value1"])
        writer.writerow(["key2", "value2", "extra"])
        # writer.writerow(["key3", "value3", "extra", "append=True"])
        writer.writerow(["key3", "value3", "extra"])
        writer.writerow(["key4", "value4", "type=int"])
        # writer.writerow(["key5", "value5", "type=int", "append=True"])
        writer.writerow(["key5", "value5", "type=int"])
        writer.writerow(["key6"])
        temp_path = temp.name

    # Call the get_metadata function with the temporary CSV file
    result = util.get_metadata(temp_path)

    # Check the result
    # appending is ignored, for now
    # assert result == {
    #    "key1": {"value": "value1", "append": False, "type": str},
    #    "key2": {"value": "value2,extra", "append": False, "type": str},
    #    "key3": {"value": "value3,extra", "append": True, "type": str},
    #    "key4": {"value": "value4", "append": False, "type": int},
    #    "key5": {"value": "value5", "append": True, "type": int},
    # }
    assert result == {
        "key1": {"value": "value1", "type": str},
        "key2": {"value": "value2,extra", "type": str},
        "key3": {"value": "value3,extra", "type": str},
        "key4": {"value": "value4", "type": int},
        "key5": {"value": "value5", "type": int},
    }

    # Delete the temporary CSV file
    os.remove(temp_path)


def test_get_metadata_different_formats():
    csv_file = "tests/test_metadata_files/test_csv.csv"
    yaml_file = "tests/test_metadata_files/test_yaml.yaml"
    json_file = "tests/test_metadata_files/test_json.json"
    xml_file = "tests/test_metadata_files/test_xml.xml"

    csv_result = util.get_metadata(csv_file)
    yaml_result = util.get_metadata(yaml_file)
    json_result = util.get_metadata(json_file)
    xml_result = util.get_metadata(xml_file)

    assert csv_result == yaml_result
    assert yaml_result == json_result
    assert json_result == xml_result


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
        ncfile = Dataset(temp.name, "w", format="NETCDF4_CLASSIC")
        ncfile.createDimension("dim", None)
        ncfile.createVariable("latitude", "f4", ("dim",))
        ncfile.createVariable("longitude", "f4", ("dim",))
        ncfile.key1 = "old_value1"
        ncfile.key3 = "old_value3"
        ncfile.key4 = "old_value4"
        temp_path = temp.name

    raw_metadata = util.get_metadata("tests/test_metadata_files/test_csv.csv")

    assert raw_metadata.keys() == {
        "key1",
        "key2",
        "key3",
        "key4",
        "key5",
        "latitude",
        "longitude",
    }
    assert raw_metadata["key4"]["value"] == "12"

    # Call the add_metadata_to_netcdf function with the temporary netCDF file and the temporary CSV file
    util.add_metadata_to_netcdf(ncfile, "tests/test_metadata_files/test_csv.csv")

    # Check the result
    # overwrite existing
    assert ncfile.getncattr("key1") == "value1"
    # "key2" should be added
    assert ncfile.getncattr("key2") == "value2"
    # appending doesnt work with netcdf4_classic
    ## appended value will only ever be a string
    # assert ncfile.getncattr("key3") == ["old_value3", "12"]
    assert ncfile.getncattr("key3") == 12
    # string number in csv is tidy string in netCDF
    assert ncfile.getncattr("key4") == "12"
    # value should be integer
    assert ncfile.getncattr("key5") == 12
    # latitude and longitude are added as variables
    assert np.allclose(ncfile.variables["latitude"][:], 12.34)
    assert np.allclose(ncfile.variables["longitude"][:], 56.78)

    ncfile.close()

    # Delete the temporary netCDF file and the temporary CSV file
    os.remove(temp_path)
    # os.remove(metadata_path)


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


def test_change_qc_flags():
    # Create a temporary netCDF file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".nc") as temp:
        ncfile = Dataset(temp.name, "w", format="NETCDF4")
        ncfile.createDimension("dim", 3)
        var = ncfile.createVariable("qc_var", "i4", ("dim",))
        var.flag_values = [0, 1, 2]
        var.flag_meanings = "not_used good_data suspect_data"

    # test error raised when invalid variable name given
    with pytest.raises(
        ValueError,
        match=r"Variable qc_flag not in netCDF file",
    ):
        util.change_qc_flags(ncfile, "qc_flag")

    # test warning on space in flag_meanings but then correctly converted
    flag_meanings = ["not used", "good_data", "strange_data"]
    with pytest.warns(
        UserWarning,
        match=r"Space found in flag meaning 'not used', changing to underscore.",
    ):
        util.change_qc_flags(ncfile, "qc_var", flag_meanings=flag_meanings)
    assert (
        ncfile["qc_var"].getncattr("flag_meanings") == "not_used good_data strange_data"
    )

    # test error raised when not_used is not first meaning
    flag_meanings = ["wrong_meaning", "good_data", "suspect_data"]
    with pytest.raises(
        ValueError,
        match=r"Invalid flag meanings - first two flag meanings must be 'not_used' and 'good_data', not 'wrong_meaning' and 'good_data'.",
    ):
        util.change_qc_flags(ncfile, "qc_var", flag_meanings=flag_meanings)

    # test error raised when good_data is not second meaning
    flag_meanings = ["not_used", "wrong_meaning", "suspect_data"]
    with pytest.raises(
        ValueError,
        match=r"Invalid flag meanings - first two flag meanings must be 'not_used' and 'good_data', not 'not_used' and 'wrong_meaning'.",
    ):
        util.change_qc_flags(ncfile, "qc_var", flag_meanings=flag_meanings)

    # test error raised when 0 is not first value
    flag_meanings = ["not_used", "good_data", "suspect_data"]
    flag_values = [3, 1, 2]
    with pytest.raises(
        ValueError,
        match=r"Invalid flag values - first two flag values must be 0 and 1, not 3 and 1.",
    ):
        util.change_qc_flags(
            ncfile, "qc_var", flag_meanings=flag_meanings, flag_values=flag_values
        )

    # test error raised when 1 is not second value
    flag_meanings = ["not_used", "good_data", "suspect_data"]
    flag_values = [0, 3, 2]
    with pytest.raises(
        ValueError,
        match=r"Invalid flag values - first two flag values must be 0 and 1, not 0 and 3.",
    ):
        util.change_qc_flags(
            ncfile, "qc_var", flag_meanings=flag_meanings, flag_values=flag_values
        )

    # test error raised when different number of meanings and values
    flag_meanings = ["not_used", "good_data", "suspect_data"]
    flag_values = [0, 1, 2, 3]
    with pytest.raises(
        ValueError,
        match=r"Different number of flag_values \(4\) and flag_meanings \(3\).",
    ):
        util.change_qc_flags(
            ncfile, "qc_var", flag_meanings=flag_meanings, flag_values=flag_values
        )

    # test works with values made when not defined
    flag_meanings = ["not_used", "good_data", "suspect_data", "more_suspect_data"]
    util.change_qc_flags(ncfile, "qc_var", flag_meanings=flag_meanings)
    assert (
        ncfile["qc_var"].getncattr("flag_meanings")
        == "not_used good_data suspect_data more_suspect_data"
    )
    assert all(ncfile["qc_var"].getncattr("flag_values") == [0, 1, 2, 3])

    # test works with correct meanings and values given
    flag_meanings = [
        "not_used",
        "good_data",
        "suspect_data",
        "more_suspect_data",
        "very_unlikely_data",
    ]
    flag_values = [0, 1, 2, 3, 4]
    util.change_qc_flags(
        ncfile, "qc_var", flag_meanings=flag_meanings, flag_values=flag_values
    )
    assert (
        ncfile["qc_var"].getncattr("flag_meanings")
        == "not_used good_data suspect_data more_suspect_data very_unlikely_data"
    )
    assert all(ncfile["qc_var"].getncattr("flag_values") == [0, 1, 2, 3, 4])


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
