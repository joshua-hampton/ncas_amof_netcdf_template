ncas-amof-netcdf-template
=========================

<h2>IMPORTANT: PLEASE READ!</h2>
This branch is a development version, and while it should be installable with pip and work as intended there are no guarantees.

For a stable version, please switch to the `main` branch or download the [latest release version](https://github.com/joshua-hampton/ncas_amof_netcdf_template/releases/latest).



<h3>Carry on...</h3>

Makes 'just-add-data' AMOF-compliant netCDF4 file.

> **NOTE 1**: Check out the [wiki], it's much bettter than what's written here.

> **NOTE 2**: Works, but still work in progress, bugs may well be present. Please report an issue with any problems discovered.


Usage
-----

<h3>Python</h3>

```python
import create_netcdf
create_netcdf.main(instrument, date = None, dimension_lengths = {}, loc = 'land', products = None)
```
where:
- `instrument` - name of NCAS instrument, e.g. "ncas-ceilometer-3"
- `date` - date for data, YYYYmmdd format, default to today's date. Optional.
- `dimension_lengths` - dictionary of lengths of dimensions, e.g. {'time':96, 'altitude':45}. If length for required dimensions are not given, then python will ask for user input, default empty. Optional.
- `loc` - one of 'land', 'air', 'sea', or 'trajectory', default is 'land'. Optional.
- `products` - applicable products of desired NCAS instrument to make netCDF for. Setting products as `None` (default) makes netCDF file for all available products. Optional.

All products associated with an instrument can be printed by
```python
import create_netcdf
create_netcdf.list_products(instrument)
```
where `instrument` is replaced with the name of the NCAS instrument.

<h3>Command Line</h3>

```bash
python create_netcdf.py ncas-instrument
```
will make a netCDF file for every applicable product for `ncas-instrument`, where `ncas-instrument` is replaced with the name of an NCAS instrument. Products can be listed with the by executing 
```bash 
python create_netcdf.py ncas-instrument --list-products
```
and individual products can be specified using the `-p` flag. For all available options, `python create_netcdf.py --help`

[wiki]: https://github.com/joshua-hampton/ncas_amof_netcdf_template/wiki
