ncas-amof-netcdf-template
=========================
[![Documentation Status](https://readthedocs.org/projects/ncas-amof-netcdf-template/badge/?version=stable)](https://ncas-amof-netcdf-template.readthedocs.io/en/stable)
[![PyPI](https://img.shields.io/pypi/v/ncas-amof-netcdf-template)](https://pypi.org/project/ncas-amof-netcdf-template/)
[![Conda (channel only)](https://img.shields.io/conda/vn/conda-forge/ncas-amof-netcdf-template)](https://anaconda.org/conda-forge/ncas-amof-netcdf-template)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/ncas-amof-netcdf-template)


Makes 'just-add-data' AMOF-compliant netCDF4 file.

A full description on how to install and use this module can be found [through the documentation](https://ncas-amof-netcdf-template.readthedocs.io/en/stable).

Requirements
------------
* Python 3.7 or above
* Python modules:
  * [netCDF4](http://unidata.github.io/netcdf4-python/)
  * [NumPy](https://numpy.org/) 
  * [Requests](https://requests.readthedocs.io/en/latest/)
  * [pandas](https://pandas.pydata.org/)

Installation
------------
Releases of `ncas-amof-netcdf-template` can be installed using conda,
```
conda install -c conda-forge ncas-amof-netcdf-template
```
or by using pip,
```
pip install ncas-amof-netcdf-template
```
or releases can be [downloaded from GitHub](https://github.com/joshua-hampton/ncas_amof_netcdf_template/releases) and installed using
```
pip install .
```

Usage
-----

A fuller description of how to use this module can be found in the [documentation](https://ncas-amof-netcdf-template.readthedocs.io/en/stable/usage.html).

```python
import ncas_amof_netcdf_template as nant
nant.create_netcdf.main(instrument, date = None, dimension_lengths = {}, loc = 'land', products = None)
```
where:
- `instrument` - name of NCAS instrument, e.g. "ncas-ceilometer-3"
- `date` - date for data, YYYYmmdd format, default to today's date. Optional.
- `dimension_lengths` - dictionary of lengths of dimensions, e.g. {'time':96, 'altitude':45}. If length for required dimensions are not given, then python will ask for user input, default empty. Optional.
- `loc` - one of 'land', 'air', 'sea', or 'trajectory', default is 'land'. Optional.
- `products` - applicable products of desired NCAS instrument to make netCDF for. Setting products as `None` (default) makes netCDF file for all available products. Optional.
- `verbose` - additional level of information and warnings to print. Only 1 additional layer of warnings are currently available.

All products associated with an instrument can be printed by
```python
import ncas_amof_netcdf_template as nant
nant.create_netcdf.list_products(instrument)
```
where `instrument` is replaced with the name of the NCAS instrument.


