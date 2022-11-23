Suggestions and Further Help
============================

Code layout
-----------
`ncas-ceilometer-3-software <https://github.com/ncasuk/ncas-ceilometer-3-software>`_ is an example of this module in use for creating NCAS-GENERAL netCDF files. There are four main components to this repo:

#. ``read_ceilometer.py`` - this script contains functions to read the raw data files from the instrument and returns all of the variables and data in a Python-friendly format.
#. ``process_ceilometer.py`` - this uses the functions in ``read_ceilometer.py`` to read the raw data, and uses the functions from this module to actually create the netCDF file.
#. ``metadata.csv`` - CSV file which has relevant metadata for this instrument, used as described `here <usage.html#metadata>`_.
#. ``scripts`` - folder that contains Bash scripts that can be called in a crontab/scheduler to automatically create netCDF files on a regular basis.


Problems?
---------
The best way to get help is through `issues on GitHub <https://github.com/joshua-hampton/ncas_amof_netcdf_template/issues>`_. Here you'll be able to see if anyone else has had the same problem, and any fixes or solutions that may have been found, or raise an issue to highlight a new problem.

If you find a problem and also work out a solution to the issue, feel free to fork the GitHub repo and `create a pull request <https://github.com/joshua-hampton/ncas_amof_netcdf_template/pulls>`_ with your solution. This will then be reviewed before being accepted into a future release.


Donations
---------
Yeah, I bet I can't get away with this...

