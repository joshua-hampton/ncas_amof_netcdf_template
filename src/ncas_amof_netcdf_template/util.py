"""
Reasonably helpful functions that can be often used.

"""

import csv
import datetime as dt
import numpy as np


def check_int(value):
    """
    Returns True if value is an integer, otherwise returns False.
    
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


def check_float(value):
    """
    Returns True if value is a float, otherwise returns False.

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



def get_metadata(metafile):
    """
    Returns a dict from a csv with metadata.
    Can also include latitude and longitude variables if
    they are single values (e.g. point deployment).
    
    Args:
        metafile (file): csv file with metadata, one attribute per line

    Returns:
        dict: metadata from csv as dictionary
    """
    with open(metafile, 'rt') as meta:
        raw_metadata = {} #empty dict
        metaread = csv.reader(meta)
        for row in metaread:
            if len(row) >= 2:
                raw_metadata[row[0]] = ','.join(row[1:]).strip()
    return raw_metadata



def add_metadata_to_netcdf(ncfile, metadata_file=None):
    """
    Reads metadata from csv file using get_metadata, adds values to 
    global attributes in netCDF file.
    Can also include latitude and longitude variables if they are 
    single values (e.g. point deployment), using update_variable function.
    
    Args:
        ncfile (netCDF Dataset): Dataset object of netCDF file.
        metadata_file (file): csv file with metadata, one attribute per line
    """
    if metadata_file != None:
        raw_metadata = get_metadata(metadata_file)
        for attr, value in raw_metadata.items():
            # if value is int or float, use that type rather than str
            if check_int(value):
                value = int(value)
            elif check_float(value):
                value = float(value)

            if attr in ncfile.ncattrs():
                ncfile.setncattr(attr, value)
            elif attr == 'latitude' or attr == 'longitude':
                update_variable(ncfile, attr, value)



def get_times(dt_times):
    """
    Returns all time units for AMOF netCDF files from series of datetime objects.

    Args:
        dt_times (list-like object): object with datetime objects for times

    Returns:
        lists: unix_times, day-of-year, years, months, days, hours, minutes, seconds
        floats: unix time of first and last times (time_coverage_start and time_coverage_end)
        str: date in YYYYmmdd format of first time, (file_date)
    """
    unix_times = [i.replace(tzinfo=dt.timezone.utc).timestamp() for i in dt_times]
    doy = [i.timetuple().tm_yday for i in dt_times]
    years = [i.year for i in dt_times]
    months = [i.month for i in dt_times]
    days = [i.day for i in dt_times]
    hours = [i.hour for i in dt_times]
    minutes = [i.minute for i in dt_times]
    seconds = [np.float32(i.second + (i.microsecond/(10**(len(str(i.microsecond)))))) for i in dt_times]    
    time_coverage_start_dt = unix_times[0]
    time_coverage_end_dt = unix_times[-1]
    file_date = f'{dt_times[0].year}{zero_pad_number(dt_times[0].month)}{zero_pad_number(dt_times[0].day)}'    
    return unix_times, doy, years, months, days, hours, minutes, seconds, time_coverage_start_dt, time_coverage_end_dt, file_date



def update_variable(ncfile, ncfile_varname, data):
    """
    Adds data to variable, and updates valid_min and valid_max variable attrs if they exist.
    
    Args:
        ncfile (netCDF Dataset): Dataset object of netCDF file.
        ncfile_varname (str): Name of variable in netCDF file.
        data (array or list): Data to be added to netCDF variable.
    """
    if 'valid_min' in ncfile.variables[ncfile_varname].ncattrs():
        ncfile.variables[ncfile_varname].valid_min = np.float64(np.nanmin(data)).astype(ncfile.variables[ncfile_varname].datatype)
        ncfile.variables[ncfile_varname].valid_max = np.float64(np.nanmax(data)).astype(ncfile.variables[ncfile_varname].datatype)
    ncfile.variables[ncfile_varname][:] = data



def zero_pad_number(n):
    """
    Returns single digit number n as '0n'
    Returns multiple digit number n as 'n'
    Used for date or month strings
    
    Args:
        n (int): Number
        
    Returns:
        str: Number with zero padding if single digit.
        
    """
    if len(f'{n}') == 1:
        return f'0{n}'
    else:
        return f'{n}'
