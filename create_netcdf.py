import tsv2dict
from netCDF4 import Dataset
import datetime as dt
import copy

import values



def add_attributes(ncfile, instrument_dict, product, created_time, location, loc):
    for key,value in instrument_dict['common']['attributes'].items():
        if value['Fixed Value'] != '':
            ncfile.setncattr(key, value['Fixed Value'])
        elif key == 'source':
            ncfile.setncattr(key, instrument_dict['info']['Descriptor'])
        elif key == 'institution':
            ncfile.setncattr(key, 'National Centre for Atmospheric Science (NCAS)')
        elif key == 'platform':
            ncfile.setncattr(key, location)
        elif key == 'instrument_manufacturer':
            ncfile.setncattr(key, instrument_dict['info']['Manufacturer'])
        elif key == 'instrument_model':
            ncfile.setncattr(key, instrument_dict['info']['Model No.'])
        elif key == 'instrument_serial_number':
            ncfile.setncattr(key, instrument_dict['info']['Serial Number'])
        elif key == 'amf_vocabularies_release':
            ncfile.setncattr(key, f'https://github.com/ncasuk/AMF_CVs/releases/tag/{values.TAG}')
        elif key == 'history':
            ncfile.setncattr(key, f'{created_time} - File created')
        elif key == 'last_revised_date':
            ncfile.setncattr(key, created_time)
        elif key == 'deployment_mode':
            ncfile.setncattr(key, loc)
        else:
            ncfile.setncattr(key, f"CHANGE: {value['Description']}. {value['Compliance checking rules']}")
    
    for key,value in instrument_dict[product]['attributes'].items():
        if value['Fixed Value'] != '':
            ncfile.setncattr(key, value['Fixed Value'])
        else:
            ncfile.setncattr(key, f"CHANGE: {value['Description']}. {value['Compliance checking rules']}")
            
            
            
def add_dimensions(ncfile, instrument_dict, product, dimension_lengths):
    for key, length in dimension_lengths.items():
        if key in instrument_dict['common']['dimensions'].keys() or key in instrument_dict[product]['dimensions'].keys():
            ncfile.createDimension(key, length)
        
        
def add_variables(ncfile, instrument_dict, product):
    for obj in [product, 'common']:
        for key, value in instrument_dict[obj]['variables'].items():
            # therefore, value is instrument_dict[obj]['variables'][key]
            # want to pop certain things here, but not for ever, so make tmp_value
            tmp_value = copy.copy(value)
            
            # error, there are some variables with dimensions 
            # missing, error in spreadsheet
            # if we encounter one, we're going to print out an error 
            # and forget about that variable
            if 'dimension' not in tmp_value.keys():
                print(f'ERROR: Missing dimensions for variable {key} in product {obj}')
                print(f'Variable not added file')
            else:
                var_dims = tmp_value['dimension']
                # there was an error somewhere meaning 2 dimensions had a '.' instead of ',' between them
                var_dims = var_dims.replace('.',',')
                var_dims = tuple(x.strip() for x in var_dims.split(','))
            
                datatype = tmp_value.pop('type')
                
                if '_FillValue' in tmp_value:
                    fill_value = float(tmp_value.pop('_FillValue'))
                else:
                    fill_value = ''
                
                if fill_value != '':
                    var = ncfile.createVariable(key, datatype, var_dims, fill_value = fill_value)
                else:
                    var = ncfile.createVariable(key, datatype, var_dims)
                
                for mdatkey, mdatvalue in tmp_value.items():
                    var.setncattr(mdatkey, mdatvalue)
    

            

def make_netcdf(instrument, product, time, instrument_dict, loc = 'land', dimension_lengths = {}, **kwargs):
    """
    dimension_lengths = {dimension_name1: length, dimension_name2: length...}
    loc - one of land, sea, air, trajectory
    kwargs: options (default '')
            product_version (default 1.0)
            file_location (default '.')
    """
    location = instrument_dict['info']['Mobile/Fixed (loc)'].split('-')[-1].strip().lower()
    if 'product_version' in kwargs:
        product_version = kwargs['product_version']
    else:
        product_version = 1.0
    if 'options' in kwargs:
        no_options = len(kwargs['options'].split('_'))
        if no_options > 3:
            msg = f'Too many options, maximum allowed 3, given {no_options}'
            raise ValueError(msg)
        options = f"_{kwargs['options']}"
    else:
        options = ''
    if 'file_location' in kwargs:
        file_location = kwargs['file_location']
    else:
        file_location = '.'
        
    filename = f"{instrument}_{location}_{time}_{product}{options}_v{product_version}.nc"
    
    ncfile = Dataset(f'{file_location}/{filename}', 'w', format='NETCDF4_CLASSIC')
    created_time = dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%S')
    
    add_attributes(ncfile, instrument_dict, product, created_time, location, loc)
    add_dimensions(ncfile, instrument_dict, product, dimension_lengths)
    add_variables(ncfile, instrument_dict, product)
    
    ncfile.close()
    

def list_products(instrument):
    """
    Lists available products for an instrument
    
    Args:
        instrument (str): ncas instrument name
        
    Returns:
        list of products available for the given instrument
    """
    instrument_dict = tsv2dict.instrument_dict(instrument)
    tsvdictkeys = instrument_dict.keys()
    products = list(tsvdictkeys)
    products.remove('info')
    products.remove('common')
    return products

    
    
def main(instrument, date = None, dimension_lengths = {}, loc = 'land', products = None):
    """
    Create 'just-add-data' AMOF-compliant netCDF file 
    
    Args:
        instrument (str): ncas instrument name
        date (str): date for file, format YYYYmmdd. If not given, finds today's date
        dimension_lengths (dict): dictionary of dimension:length. If length not given 
                                  for needed dimension, user will be asked to type 
                                  in dimension length
        loc (str): one of 'land', 'sea', 'air', 'trajectory'
        products (str): list of products to make netCDF file for this instrument. If None, then all applicable products are made.
    """
    if date == None:
        date = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d")
    
    instrument_dict = tsv2dict.instrument_dict(instrument, loc = loc)
    
    # get and check our list of products
    tsvdictkeys = instrument_dict.keys()
    poss_products = list(tsvdictkeys)
    poss_products.remove('info')
    poss_products.remove('common')
    if products == None:  # user doesn't specify products, make all
        products = poss_products
    else:  # check user specified products are applicable for instrument
        remove_products = []
        if isinstance(product, str):
            product = [product]
        for product in products:
            if product not in poss_products:
                print(f'{product} is not available for this instrument, will be skipped.')
                remove_products.append(product)
        for remove_product in remove_products:
            products.remove(remove_product)
    # so by now we should have our list of products, quit if we have no products
    if not isinstance(products, list) or len(products) == 0:
        msg = f'No valid products specified, valid products are {poss_products}'
        raise ValueError(msg)
    
    # make sure we have dimension lengths for all expected dimensions
    all_dimensions = []
    dimlengths = {}
    for key, val in instrument_dict.items():
        if 'dimensions' in val.keys() and (key in products or key == 'common'):
            for dim in list(val['dimensions'].keys()):
                if dim not in all_dimensions:
                    all_dimensions.append(dim)
                    if '<' not in val['dimensions'][dim]['Length']:
                        dimlengths[dim] = int(val['dimensions'][dim]['Length'])
    for key, value in dimension_lengths.items():
        if key not in dimlengths.keys():
            dimlengths[key] = value
    for dim in all_dimensions:
        if dim not in dimlengths.keys():
            length = input(f"Enter length for dimension {dim}: ")
            dimlengths[dim] = int(length)
    
    # make the files
    for product in products:
        make_netcdf(instrument, product, date, instrument_dict, loc = loc, dimension_lengths = dimlengths)
    
    
    
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description = 'Create AMOF-compliant netCDF file with no data.')
    parser.add_argument('instrument', type=str, help = 'Name of NCAS instrument.')
    parser.add_argument('-d','--date', type=str, help = 'Date for data in file, YYYYmmdd format. If not given, default to today.', default=None, dest='date')
    parser.add_argument('-l','--dim-lengths', nargs='*', help = 'Length for each dimension, e.g. -l time 96 altitude 45. If not given, or required dimension missing, python will ask for user input.', dest='dim_lengths')
    parser.add_argument('-m','--deployment-mode', type=str, choices=['land','sea','air','trajectory'], help = 'Deployment mode of instrument, one of "land", "sea", "air, "trajectory". Default is "land".', default='land', dest='deployment')
    parser.add_argument('--list-products', action='store_true', dest='list_products', help = 'If given, available products for instrument are printed, then script exits.')
    parser.add_argument('-p','--products', nargs='*', default=None, help = 'Products for instrument to make netCDF file. If not given, netCDF files for all applicable products are made.', dest="products")
    args = parser.parse_args()
    
    
    if args.list_products:
        print(list_products(args.instrument))
    else:
        dim_lengths = {}
        if args.dim_lengths != None:
            if len(args.dim_lengths) % 2 != 0:
                msg = f'-l/--dim-lengths option should be `dimension length` pairs'
                raise ValueError(msg)
            for i in range(0,len(args.dim_lengths),2):
                dim_lengths[args.dim_lengths[i]] = int(args.dim_lengths[i+1])
            
        main(args.instrument, date=args.date, dimension_lengths=dim_lengths, loc=args.deployment, products=args.products)
