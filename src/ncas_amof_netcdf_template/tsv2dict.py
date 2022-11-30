"""
Take tsv files and return data as dictionaries 
useful for creating netCDF files.

"""

import pandas as pd
import re
import requests

from . import values


def tsv2dict_vars(tsv_file):
    """
    For a given tsv file from https://github.com/ncasuk/AMF_CVs/tree/main/product-definitions/tsv
    for data variables, return dictionary of variables and their attributes.

    Args:
        tsv_file (str): URL to location of tsv file

    Returns:
        dictionary of variables and attributes
    """
    df_vars = pd.read_csv(tsv_file, sep='\t')
    df_vars=df_vars.fillna('')
    
    all_vars_dict = {}
    current_var_dict = {}
    first_loop = True
    current_var = ''
    
    for current_line in df_vars.iloc:
        if current_line['Variable'] != '':
            if not first_loop:
                all_vars_dict[current_var] = current_var_dict
                current_var_dict = {}
            else:
                first_loop = False
            current_var = current_line['Variable']
            current_var_dict = {}
            #continue
        if current_line['Attribute'] != '':
            if current_line['Value'] == '' and 'example value' in current_line.keys() and current_line['example value'] != '':
                current_var_dict[current_line['Attribute']] = f"EXAMPLE: {current_line['example value']}"
            else:
                current_var_dict[current_line['Attribute']] = current_line['Value']
    all_vars_dict[current_var] = current_var_dict
    
    return all_vars_dict


def tsv2dict_dims(tsv_file):
    """
    For a given tsv file from https://github.com/ncasuk/AMF_CVs/tree/main/product-definitions/tsv
    for data dimensions, return dictionary of dimensions and additional info.

    Args:
        tsv_file (str): URL to location of tsv file

    Returns:
        dictionary of dimensions and info
    """
    df_dims = pd.read_csv(tsv_file, sep='\t')
    df_dims = df_dims.fillna('')
    
    all_dims_dict = {}
    
    for dim in df_dims.iloc:
        dim_dict = dim.to_dict()
        dim_name = dim_dict.pop('Name')
        all_dims_dict[dim_name] = dim_dict
        
    return all_dims_dict


def tsv2dict_attrs(tsv_file):
    """
    For a given tsv file from https://github.com/ncasuk/AMF_CVs/tree/main/product-definitions/tsv
    for data global attributes, return dictionary of attributes and associated values and info.

    Args:
        tsv_file (str): URL to location of tsv file

    Returns:
        dictionary of global attributes and associated values and info
    """
    df_attrs = pd.read_csv(tsv_file, sep='\t')
    df_attrs = df_attrs.fillna('')
    
    all_attrs_dict = {}
    
    for dim in df_attrs.iloc:
        dim_dict = dim.to_dict()
        dim_name = dim_dict.pop('Name')
        all_attrs_dict[dim_name] = dim_dict
        
    return all_attrs_dict


def tsv2dict_instruments(tsv_file):
    """
    For a given tsv file from https://github.com/ncasuk/AMF_CVs/tree/main/product-definitions/tsv
    for ncas- or community- instruments, return dictionary of instruments and associated information.

    Args:
        tsv_file (str): URL to location of tsv file

    Returns:
        dictionary of instruments and associated information
    """
    df_instruments = pd.read_csv(tsv_file, sep='\t')
    df_instruments = df_instruments.fillna('')
    
    all_instruments = {}
    
    for current_instrument in df_instruments.iloc:
        inst_dict = current_instrument.to_dict()
        inst_name = inst_dict.pop('New Instrument Name')        
        data_products = re.split(',| |\|', inst_dict['Data Product(s)'])
        data_products = list(filter(None, data_products))
        inst_dict['Data Product(s)'] = data_products        
        all_instruments[inst_name] = inst_dict
        
    return all_instruments


def create_variables_tsv_url(product, tag = values.TAG):
    """
    Returns URL for tsv file of variables specific to  a given product and tag release or branch.

    Args:
        product (str): data product
        tag (str): tag release or branch name in GitHub for version of data. Default is set in values.py.

    Return: 
        URL
    """
    return f'https://raw.githubusercontent.com/ncasuk/AMF_CVs/{tag}/product-definitions/tsv/{product}/variables-specific.tsv'


def create_dimensions_tsv_url(product, tag = values.TAG):
    """
    Returns URL for tsv file of dimensions specific to a given product and tag release or branch.

    Args:
        product (str): data product
        tag (str): tag release or branch name in GitHub for version of data. Default is set in values.py.

    Return: 
        URL
    """

    return f'https://raw.githubusercontent.com/ncasuk/AMF_CVs/{tag}/product-definitions/tsv/{product}/dimensions-specific.tsv'


def create_attributes_tsv_url(product, tag = values.TAG):
    """
    Returns URL for tsv file of global attributes specific to a given product and tag release or branch.

    Args:
        product (str): data product
        tag (str): tag release or branch name in GitHub for version of data. Default is set in values.py.

    Return: 
        URL
    """

    return f'https://raw.githubusercontent.com/ncasuk/AMF_CVs/{tag}/product-definitions/tsv/{product}/global-attributes-specific.tsv'


def instrument_dict(desired_instrument, loc='land'):
    """
    Collect all variables, dimensions and attributes required for all data products
    associated with an instrument and deployment mode.

    Args:
        desired_instrument (str): name of instrument
        loc (str): deployment mode, one of 'land', 'sea', 'air', or 'trajectory'. Default 'land'.

    Returns:
        dictionary of all attributes, dimensions and variables associated with the named instrument.
    """
    if loc == 'land':
        common_dimensions_url = values.COMMON_DIMENSIONS_LAND_URL
        common_variables_url = values.COMMON_VARIABLES_LAND_URL
    elif loc == 'sea':
        common_dimensions_url = values.COMMON_DIMENSIONS_SEA_URL
        common_variables_url = values.COMMON_VARIABLES_SEA_URL
    elif loc == 'air':
        common_dimensions_url = values.COMMON_DIMENSIONS_AIR_URL
        common_variables_url = values.COMMON_VARIABLES_AIR_URL
    elif loc == 'trajectory':
        common_dimensions_url = values.COMMON_DIMENSIONS_TRAJECTORY_URL
        common_variables_url = values.COMMON_VARIABLES_TRAJECTORY_URL
    else:
        msg = f'Unknown loc "{loc}" - should be one of "land", "sea", "air", "trajectory"'
        raise ValueError(msg)
    
    instrument_dict = {}
    main_instruments = tsv2dict_instruments(values.INSTRUMENTS_URL)
    if desired_instrument in main_instruments.keys():
        instrument_dict['info'] = main_instruments[desired_instrument]
    else:
        instrument_dict['info'] = tsv2dict_instruments(values.COMMUNITY_INSTRUMENTS_URL)[desired_instrument]

    # Add common stuff
    instrument_dict['common'] = {}
    instrument_dict['common']['attributes'] = {}
    instrument_dict['common']['dimensions'] = {}
    instrument_dict['common']['variables'] = {}

    instrument_dict['common']['attributes'] = tsv2dict_attrs(values.COMMON_ATTRIBUTES_URL)
    instrument_dict['common']['dimensions'] = tsv2dict_dims(common_dimensions_url)
    instrument_dict['common']['variables'] = tsv2dict_vars(common_variables_url)

    # Add stuff for each product of instrument it specifics exist
    for product in instrument_dict['info']['Data Product(s)']:
        instrument_dict[product] = {}
        instrument_dict[product]['attributes'] = {}
        instrument_dict[product]['dimensions'] = {}
        instrument_dict[product]['variables'] = {}
        
        attr_url = create_attributes_tsv_url(product)
        dim_url = create_dimensions_tsv_url(product)
        var_url = create_variables_tsv_url(product)
    
        request = requests.get(attr_url)
        if request.status_code == 200:
            instrument_dict[product]['attributes'] = tsv2dict_attrs(attr_url)
    
        request = requests.get(dim_url)
        if request.status_code == 200:
            instrument_dict[product]['dimensions'] = tsv2dict_dims(dim_url)
    
        request = requests.get(var_url)
        if request.status_code == 200:
            instrument_dict[product]['variables'] = tsv2dict_vars(var_url)

    return instrument_dict

    
if __name__ == "__main__":
    import sys
    desired_instrument = sys.argv[1]
    instrument = instrument_dict(desired_instrument)
    '''
    This bit just makes the print look pretty, a standard print would also work
    '''
    import pprint
    pp = pprint.PrettyPrinter(indent = 2, width = 200)
    pp.pprint(instrument)
