ncas-amof-netcdf-template
=========================

Makes 'just-add-data' AMOF-compliant netCDF4 file.

> **NOTE**: Still work in progress


Usage
-----

`python create_netcdf.py <ncas-instrument>`

or from within python

```python
import create_netcdf
main(instrument, date = None, dimension_lengths = {}, loc = 'land')
```
where:
- `instrument` - name of NCAS instrument, e.g. "ncas-ceilometer-3"
- `date` - date for data, YYYYmmdd format, default to today's date
- `dimension_lengths` - dictionary of lengths of dimensions, e.g. {'time':96, 'altitude':45}. If length for required dimensions are not given, then python will ask for user input, default empty.
- `loc` - one of 'land', 'air', 'sea', or 'trajectory', default is 'land'
