"""
Functions for removal of empty product-specific variables.
As a variable cannot be removed from a netCDF file, a new file
has to be created, with the option of removing the old one.
"""

import os
from netCDF4 import Dataset
import requests
import numpy as np





def get_product_variables_metadata(product, skip_check = False):
    """
    Get variables and their metadata associated with a product.
    `product` should be in https://github.com/ncasuk/AMF_CVs/blob/main/AMF_CVs/AMF_product.json
    
    Args:
        product (str): Product describing the data from the instrument for the netCDF file.
        skip_check (bool): Skips checking if product in the product json file. Default False.
        
    Returns:
        list: All product-specific variables.
        dict: Dictionary of variables and their attributes.
        
    """
    if not skip_check:
        product_list = get_json_from_github("https://raw.githubusercontent.com/ncasuk/AMF_CVs/main/AMF_CVs/AMF_product.json")["product"]
    
        # Check for valid product
        if product not in product_list:
            msg = f"product {product} is not in https://github.com/ncasuk/AMF_CVs/blob/main/AMF_CVs/AMF_product.json"
            raise ValueError(msg)
     
    # Get the stuff
    var_dict = get_json_from_github(f"https://raw.githubusercontent.com/ncasuk/AMF_CVs/main/AMF_CVs/AMF_product_{product}_variable.json")[f"product_{product}_variable"]
    variables = var_dict.keys()
    
    return variables, var_dict



def get_json_from_github(url):
    """
    Returns desired json file from https://github.com/ncasuk/AMF_CVs/tree/main/AMF_CVs
    URL should be in form https://raw.githubusercontent.com/ncasuk/AMF_CVs/main/AMF_CVs/___.json,
    otherwise a JSONDecodeError will be returned by the r.json() call
      
    Args:
        url (str): URL of json file
        
    Returns:
        dict: JSON data from URL
        
    """
    r = requests.get(url)
    return r.json()



def main(infile, outfile = None, overwrite = True, verbose=0, **kwargs):
    """
    If a product-specific variable is empty, we want to remove it.
    However, removing a variable from a netcdf file is not possible, 
    so we have to create a new one, and just not copy over the 
    empty variable.
      
    Args:
        infile (str): File path and name of current netCDF file.
        outfile (str): Name of temporary netCDF file to create (or not so temporary, see overwrite). If None, then an file with `tmp` appended to start of infile filename will be created. Default None.
        overwrite (any): Optional. If truthy, outfile overwrites infile. If falsy, both outfile and infile remain. Default True.
        verbose (any): Optional. If truthy, prints variables that are being removed from infile. Default 0.
        kwargs: Additional keyword arguments (e.g. skip_check for get_product_variables_metadata function).
        
    """
    
    in_ncfile = Dataset(infile, "r")
    product = infile.split('/')[-1].split('_')[3]
    
    if outfile == None:
        infile_name = infile.split('/')[-1]
        infile_dir = '/'.join(infile.split('/')[:-1])
        outfile = f'{infile_dir}/tmp_{infile_name}'
    
    toexclude = []
    product_vars, _ = get_product_variables_metadata(product, **kwargs)

    for var in in_ncfile.variables.keys():
        if var in product_vars:
            if 'valid_min' in in_ncfile[var].ncattrs() and in_ncfile[var].valid_min == '<derived from file>':
                toexclude.append(var)
            elif np.all(in_ncfile[var][:].mask) == True:
                toexclude.append(var)
    
    if verbose:
        print(f'empty variables being removed: {toexclude}')
    
    dst = Dataset(outfile, "w", format='NETCDF4_CLASSIC')
    # copy global attributes all at once via dictionary
    dst.setncatts(in_ncfile.__dict__)
    # copy dimensions
    for name, dimension in in_ncfile.dimensions.items():
        dst.createDimension(name, (len(dimension)))
    # copy all file data except for the excluded
    for name, variable in in_ncfile.variables.items():
        if name not in toexclude:
            in_ncfile_name_attrs = in_ncfile[name].__dict__
            if '_FillValue' in in_ncfile_name_attrs:
                fill_value = in_ncfile_name_attrs.pop('_FillValue')
                dst.createVariable(name, variable.datatype, variable.dimensions, fill_value = fill_value)
            else:
                dst.createVariable(name, variable.datatype, variable.dimensions)
            # copy variable attributes all at once via dictionary
            dst[name].setncatts(in_ncfile_name_attrs)
            dst[name][:] = in_ncfile[name][:]
            
    dst.close()            
    in_ncfile.close()
    
    if overwrite:
        os.rename(outfile, infile)