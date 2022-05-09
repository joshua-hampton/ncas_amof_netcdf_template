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
create_netcdf.main(<ncas-instrument>)
```

where `<ncas-instrument>` is replaced with the name of an NCAS instrument, e.g. "ncas-ceilometer-3"
