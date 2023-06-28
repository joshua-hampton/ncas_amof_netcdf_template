ncas-amof-netcdf-template
=========================
[![PyPI](https://img.shields.io/pypi/v/ncas-amof-netcdf-template)](https://pypi.org/project/ncas-amof-netcdf-template/)
[![Conda (channel only)](https://img.shields.io/conda/vn/conda-forge/ncas-amof-netcdf-template)](https://anaconda.org/conda-forge/ncas-amof-netcdf-template)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/ncas-amof-netcdf-template)

[![Documentation Status](https://readthedocs.org/projects/ncas-amof-netcdf-template/badge/?version=stable)](https://ncas-amof-netcdf-template.readthedocs.io/en/stable)
[![GitHub Workflow Status](https://github.com/joshua-hampton/ncas_amof_netcdf_template/actions/workflows/run_tests.yml/badge.svg)](https://github.com/joshua-hampton/ncas_amof_netcdf_template/actions/workflows/run_tests.yml)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/joshua-hampton/ncas_amof_netcdf_template/main.svg)](https://results.pre-commit.ci/latest/github/joshua-hampton/ncas_amof_netcdf_template/main)

[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v1.json)](https://github.com/charliermarsh/ruff)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Makes 'just-add-data' AMOF-compliant netCDF4 file for either a given NCAS instrument or one of the defined data products.

A full description on how to install and use this module can be found [through the documentation](https://ncas-amof-netcdf-template.readthedocs.io/en/stable).

Requirements
------------
* Python 3.8 or above
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


Contributing
------------
Contributions are welcome from everyone, provided they enhance and improve the capabilities of this package, and code can be distributed under the conditions of the [licence](#licence). When contributing, users should create a new branch under their forked repository.

Note that `pre-commit-ci` will run on all pull requests to this repository, however autofix is disabled. It is recommended that users ensure their contributions pass these checks before submitting pull requests, however users can type `pre-commit.ci autofix` into a comment after a failed pre-commit-ci run to automatically fix issues. See [pre-commit](https://pre-commit.com/) for more details.


Licence
-------
This package is available under the [MIT licence](LICENSE).
