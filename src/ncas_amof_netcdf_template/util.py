"""
Reasonably helpful functions that can be often used.

"""

import csv
import datetime as dt
from netCDF4 import Dataset
import numpy as np
import warnings
import json
import yaml
import xml.etree.ElementTree as ET
from typing import Any, Union, Optional


def _map_data_type(data_type: str) -> type:
    types_dict = {
        "str": str,
        "string": str,
        "int": int,
        "integer": int,
        "float": float,
        "bool": bool,
    }
    return types_dict[data_type]


def check_int(value: Any) -> bool:
    """
    Returns True if value can be converted to integer, otherwise returns False.

    Args:
        value (str): string to test

    Returns:
        bool: True if value is an integer
    """
    try:
        int(value)
        return True
    except ValueError:
        return False
    except:
        raise


def check_float(value: Any) -> bool:
    """
    Returns True if value can be converted to float, otherwise returns False.

    Args:
        value (str): string to test

    Returns:
        bool: True if value is a float
    """
    try:
        float(value)
        return True
    except ValueError:
        return False
    except:
        raise


def check_type_convert(value: Any, dtype: type) -> bool:
    """
    Returns True if value can be converted to type dtype, otherwise returns False.

    Args:
        value (str): string to test
        dtype (type): type to test

    Returns:
        bool: True if value can be of type dtype
    """
    try:
        dtype(value)
        return True
    except ValueError:
        return False
    except:
        raise


def read_csv_metadata(metafile: str) -> dict[str, dict[str, Union[str, type]]]:
    """
    Returns a dict from a csv with metadata.
    Can also include latitude and longitude variables if
    they are single values (e.g. point deployment).

    Args:
        metafile (file): csv file with metadata, one attribute per line

    Returns:
        dict: metadata from csv as dictionary
    """
    with open(metafile, "rt") as meta:
        raw_metadata = {}  # empty dict
        metaread = csv.reader(meta)
        for row in metaread:
            if len(row) >= 2:
                # raw_metadata[row[0]] = {"value": "", "append": "False", "type": "str"}
                raw_metadata[row[0]] = {"value": "", "type": "str"}
                n = None
                # if row[-1].strip().startswith("type=") or row[-1].strip().startswith(
                #    "append="
                # ):
                if row[-1].strip().startswith("type="):
                    # raw_metadata[row[0]][row[-1].strip().split("=")[0]] = (
                    #    row[-1].strip().split("=")[1]
                    # )
                    # if row[-2].strip().startswith("type=") or row[
                    #    -2
                    # ].strip().startswith("append="):
                    #    n = -2
                    #    raw_metadata[row[0]][row[-2].strip().split("=")[0]] = (
                    #        row[-2].strip().split("=")[1]
                    #    )
                    # else:
                    #    n = -1
                    raw_metadata[row[0]]["type"] = row[-1].strip().split("=")[1]
                    n = -1
                raw_metadata[row[0]]["value"] = ",".join(row[1:n]).strip()
                raw_metadata[row[0]]["type"] = _map_data_type(
                    raw_metadata[row[0]]["type"]
                )
                # raw_metadata[row[0]]["append"] = (
                #    True if raw_metadata[row[0]]["append"].lower() == "true" else False
                # )
    return raw_metadata


def read_json_metadata(metafile: str) -> dict[str, dict[str, Union[str, type]]]:
    """
    Returns a dict from a JSON with metadata.
    Can also include latitude and longitude variables if
    they are single values (e.g. point deployment).

    Args:
        metafile (file): JSON file with metadata

    Returns:
        dict: metadata from JSON as dictionary
    """
    with open(metafile, "rt") as meta:
        raw_metadata = json.load(meta)
    for key, value in raw_metadata.items():
        # Convert all values to strings for now, type will convert later
        if not isinstance(value, dict):
            # raw_metadata[key] = {"value": str(value), "type": "str", "append": "False"}
            raw_metadata[key] = {"value": str(value), "type": "str"}
        elif not isinstance(value["value"], str):
            raw_metadata[key]["value"] = str(value["value"])
        # Set defaults if not present, convert where needed
        if "type" not in raw_metadata[key]:
            raw_metadata[key]["type"] = "str"
        raw_metadata[key]["type"] = _map_data_type(raw_metadata[key]["type"])
        # if "append" not in raw_metadata[key]:
        #    raw_metadata[key]["append"] = False
        # elif not isinstance(raw_metadata[key]["append"], bool):
        #    raw_metadata[key]["append"] = (
        #        True if raw_metadata[key]["append"].lower() == "true" else False
        #    )
    return raw_metadata


def read_yaml_metadata(metafile: str) -> dict[str, dict[str, Union[str, type]]]:
    """
    Returns a dict from a YAML with metadata.
    Can also include latitude and longitude variables if
    they are single values (e.g. point deployment).

    Args:
        metafile (file): YAML file with metadata

    Returns:
        dict: metadata from YAML as dictionary
    """
    with open(metafile, "rt") as meta:
        raw_metadata = yaml.safe_load(meta)
    for key, value in raw_metadata.items():
        # Convert all values to strings for now, type will convert later
        if not isinstance(value, dict):
            # raw_metadata[key] = {"value": str(value), "type": "str", "append": "False"}
            raw_metadata[key] = {"value": str(value), "type": "str"}
        elif not isinstance(value["value"], str):
            raw_metadata[key]["value"] = str(value["value"])
        # Set defaults if not present, convert where needed
        if "type" not in raw_metadata[key]:
            raw_metadata[key]["type"] = "str"
        raw_metadata[key]["type"] = _map_data_type(raw_metadata[key]["type"])
        # if "append" not in raw_metadata[key]:
        #    raw_metadata[key]["append"] = False
        # else:
        #    raw_metadata[key]["append"] = (
        #        True if raw_metadata[key]["append"].lower() == "true" else False
        #    )
    return raw_metadata


def read_xml_metadata(metafile: str) -> dict[str, dict[str, Union[str, type]]]:
    """
    Returns a dict from a XML with metadata.
    Can also include latitude and longitude variables if
    they are single values (e.g. point deployment).

    Args:
        metafile (file): XML file with metadata

    Returns:
        dict: metadata from XML as dictionary
    """
    raw_metadata = {}
    tree = ET.parse(metafile)
    root = tree.getroot()
    for child in root:
        # raw_metadata[child.tag] = {"value": "", "append": False, "type": str}
        raw_metadata[child.tag] = {"value": "", "type": str}
        for subchild in child:
            if subchild.tag == "type":
                raw_metadata[child.tag]["type"] = _map_data_type(subchild.text)
            # elif subchild.tag == "append":
            #    raw_metadata[child.tag]["append"] = (
            #        True if subchild.text.lower() == "true" else False
            #    )
            elif subchild.tag == "value":
                raw_metadata[child.tag]["value"] = subchild.text
    return raw_metadata


def get_metadata(metafile: str) -> dict[str, dict[str, Union[str, type]]]:
    """
    Returns a dict from of metadata from file. Metadata can be in a CSV, JSON, YAML, or XML file.
    Can also include latitude and longitude variables if
    they are single values (e.g. point deployment).

    Args:
        metafile (file): file with metadata

    Returns:
        dict: metadata as dictionary
    """
    if metafile.endswith(".csv"):
        return read_csv_metadata(metafile)
    elif metafile.endswith(".json"):
        return read_json_metadata(metafile)
    elif metafile.endswith(".yaml") or metafile.endswith(".yml"):
        return read_yaml_metadata(metafile)
    elif metafile.endswith(".xml"):
        return read_xml_metadata(metafile)
    else:
        warnings.warn(
            "Unknown metadata file type, trying csv...", UserWarning, stacklevel=2
        )
        return read_csv_metadata(metafile)


def add_metadata_to_netcdf(
    ncfile: Dataset, metadata_file: Optional[str] = None
) -> None:
    """
    Reads metadata from csv file using get_metadata, adds values to
    global attributes in netCDF file.
    Numbers in metadata file are converted to integers or floats unless
    they are strings in the format 'number' (e.g. '123').
    Can also include latitude and longitude variables if they are
    single values (e.g. point deployment), using update_variable function.

    Args:
        ncfile (netCDF Dataset): Dataset object of netCDF file.
        metadata_file (file): csv file with metadata, one attribute per line
    """
    if metadata_file is not None:
        raw_metadata = get_metadata(metadata_file)
        for attr, attr_info in raw_metadata.items():
            value = attr_info["value"]
            # append_value = attr_info["append"]
            valuetype = attr_info["type"]
            # if value can be converted to valuetype, do so, otherwise keep as string
            if check_type_convert(value, valuetype):
                value = valuetype(value)
            else:
                warnings.warn(
                    f"Value '{value}' for attribute '{attr}' could not be converted to type '{valuetype}'",
                    UserWarning,
                    stacklevel=2,
                )
            if attr == "latitude" or attr == "longitude":
                update_variable(ncfile, attr, value)
            # elif append_value and attr in ncfile.ncattrs():
            #    current_value = ncfile.getncattr(attr)
            #    if isinstance(current_value, list):
            #        new_value = current_value.append(value)
            #    else:
            #        new_value = [current_value, value]
            #    ncfile.setncattr(attr, new_value)
            else:
                ncfile.setncattr(attr, value)


def get_times(
    dt_times: list[dt.datetime],
) -> tuple[
    list[float],
    list[float],
    list[int],
    list[int],
    list[int],
    list[int],
    list[int],
    list[float],
    float,
    float,
    str,
]:
    """
    Returns all time units for AMOF netCDF files from series of datetime objects.

    Args:
        dt_times (list-like object): object with datetime objects for times

    Returns:
        lists: unix_times, day-of-year, years, months, days, hours, minutes, seconds
        floats: unix time of first and last times (time_coverage_start and
        time_coverage_end)
        str: date in YYYYmmdd format of first time, (file_date)
    """
    unix_times = [i.replace(tzinfo=dt.timezone.utc).timestamp() for i in dt_times]
    doy = [i.timetuple().tm_yday for i in dt_times]
    years = [i.year for i in dt_times]
    months = [i.month for i in dt_times]
    days = [i.day for i in dt_times]
    hours = [i.hour for i in dt_times]
    minutes = [i.minute for i in dt_times]
    seconds = [i.second + i.microsecond / 1000000 for i in dt_times]
    time_coverage_start_dt = unix_times[0]
    time_coverage_end_dt = unix_times[-1]
    doy = list(
        np.array(doy)
        + np.array([i / 24 for i in hours])
        + np.array([i / (24 * 60) for i in minutes])
        + np.array([i / (24 * 60 * 60) for i in seconds])
    )
    file_date = ""
    if years[0] == years[-1]:
        file_date += str(years[0])
        if months[0] == months[-1]:
            file_date += str(zero_pad_number(months[0]))
            if days[0] == days[-1]:
                file_date += str(zero_pad_number(days[0]))
                if hours[0] == hours[-1]:
                    file_date += f"-{zero_pad_number(hours[0])}"
                    if minutes[0] == minutes[-1]:
                        file_date += str(zero_pad_number(minutes[0]))
                        if int(seconds[0]) == int(seconds[-1]):
                            file_date += str(zero_pad_number(int(seconds[0])))
    else:
        raise ValueError("Incompatible dates - data from over 2 years")
    return (
        unix_times,
        doy,
        years,
        months,
        days,
        hours,
        minutes,
        seconds,
        time_coverage_start_dt,
        time_coverage_end_dt,
        file_date,
    )


def change_qc_flags(
    ncfile: Dataset,
    ncfile_varname: str,
    flag_meanings: list[str] = [],
    flag_values: Optional[list[int]] = None,
) -> None:
    """
    Change the flag meanings and flag values in a quality control variable from
    the default options. The first two flag meanings must be "not_used" and
    "good_data", and all spaces in flag meanings will be replaced with underscores.
    If given, the first two flag values must be 0 and 1. If not given, flag values
    will be worked out based on the number of flag meanings and will be sequential
    values.

    Args:
        ncfile (netCDF Dataset): Dataset object of netCDF file.
        ncfile_varname (str): Name of variable in netCDF file.
        flag_meanings (list): List of flag meanings to be used in variable.
        flag_values (list): List of integer flag values to be used in variable. Will
                            be automatically worked out if not provided.
    """
    if ncfile_varname not in ncfile.variables.keys():
        msg = f"Variable {ncfile_varname} not in netCDF file"
        raise ValueError(msg)

    for i, meaning in enumerate(flag_meanings):
        if " " in meaning:
            msg = f"Space found in flag meaning '{meaning}', changing to underscore."
            warnings.warn(msg)
            flag_meanings[i] = meaning.replace(" ", "_")

    if flag_meanings[0] != "not_used" or flag_meanings[1] != "good_data":
        msg = (
            "Invalid flag meanings - first two flag meanings must be 'not_used' "
            f"and 'good_data', not '{flag_meanings[0]}' and '{flag_meanings[1]}'."
        )
        raise ValueError(msg)

    if flag_values:
        if flag_values[0] != 0 or flag_values[1] != 1:
            msg = (
                "Invalid flag values - first two flag values must be 0 and 1, "
                f"not {flag_values[0]} and {flag_values[1]}."
            )
            raise ValueError(msg)
        if len(flag_values) != len(flag_meanings):
            msg = (
                f"Different number of flag_values ({len(flag_values)}) "
                f"and flag_meanings ({len(flag_meanings)})."
            )
            raise ValueError(msg)
    else:
        flag_values = list(range(len(flag_meanings)))

    var_type = ncfile[ncfile_varname].dtype
    flag_value_array = np.array(flag_values, dtype=var_type)

    ncfile[ncfile_varname].setncattr("flag_values", flag_value_array)
    ncfile[ncfile_varname].setncattr("flag_meanings", " ".join(flag_meanings))


def update_variable(
    ncfile: Dataset,
    ncfile_varname: str,
    data: Union[np.ndarray[Any, Any], list[Any]],
    qc_data_error: bool = True,
) -> None:
    """
    Adds data to variable, and updates valid_min and valid_max
     variable attrs if they exist.

    Args:
        ncfile (netCDF Dataset): Dataset object of netCDF file.
        ncfile_varname (str): Name of variable in netCDF file.
        data (array or list): Data to be added to netCDF variable.
        qc_data_error (bool): Raise error if trying to add values to QC flag
                               variables that are not in the flag_values attribute.
                               Otherwise, just a warning is printed. Default True.
    """
    if "valid_min" in ncfile.variables[ncfile_varname].ncattrs():
        ncfile.variables[ncfile_varname].valid_min = np.float64(np.nanmin(data)).astype(
            ncfile.variables[ncfile_varname].datatype
        )
        ncfile.variables[ncfile_varname].valid_max = np.float64(np.nanmax(data)).astype(
            ncfile.variables[ncfile_varname].datatype
        )
    if (
        "qc" in ncfile_varname.lower()
        and "flag_values" in ncfile.variables[ncfile_varname].ncattrs()
    ):
        if not np.isin(data, ncfile.variables[ncfile_varname].flag_values).all():
            valid_values = ncfile.variables[ncfile_varname].flag_values.tolist()
            msg = (
                "Invalid data being added to QC variable, "
                f"only {valid_values} are allowed."
            )
            if qc_data_error:
                raise ValueError(msg)
            else:
                print(f"[WARN]: {msg}")
    ncfile.variables[ncfile_varname][:] = data


def zero_pad_number(n: int) -> str:
    """
    Returns single digit number n as '0n'
    Returns multiple digit number n as 'n'
    Used for date or month strings

    Args:
        n (int): Number

    Returns:
        str: Number with zero padding if single digit.

    """
    if len(f"{n}") == 1:
        return f"0{n}"
    else:
        return f"{n}"
