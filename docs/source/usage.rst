How to use
==========

Unless otherwise stated, all examples will use the ``ncas-ceilometer-3`` instrument as an example.

Create netCDF file
------------------
In its very simplest form:
::

  import ncas_amof_netcdf_template as nant
  nant.create_netcdf.main('ncas-ceilometer-3')

This will create a netCDF file with today's date for all data products availalbe for the given instrument.

Date
^^^^
The `file-naming convention <https://sites.google.com/ncas.ac.uk/ncasobservations/home/data-project/ncas-data-standards/ncas-amof/file-naming>`_ for the NCAS-GENERAL standard includes the date, and sometimes time, which the data within the file represents. By default, today's date will be used in the file name. This behaviour can be overridden by giving the date to the ``create_netcdf.main`` function:
::

  nant.create_netcdf.main('ncas-ceilometer-3', date='20220214')


Data Products
^^^^^^^^^^^^^
List available data products for an instrument:
::
   
  nant.create_netcdf.list_products('ncas-ceilometer-3')


A data product can be defined in the call to create the netCDF file:
::

  nant.create_netcdf.main('ncas-ceilometer-3', products = 'aerosol-backscatter')

Or multiple products can be defined by using a list:
::

  nant.create_netcdf.main('ncas-ceilometer-3', products = ['cloud-base','cloud-coverage'])


Deployment Modes
^^^^^^^^^^^^^^^^
NCAS instruments can be deployed in one of four deployment modes - land, sea, air, or trajectory. Each of these modes requires different dimensions and variables, and the deployment mode is recorded as a global attribute in the netCDF file. The default deployment mode is ``'land'``; however, an alternative deployment mode can be selected using the ``loc`` keyword:
::

  nant.create_netcdf.main('ncas-ceilometer-3', loc = 'sea')


Output Location
^^^^^^^^^^^^^^^
The netCDF file will be written to the current working directory by default. To specify an alternative location, the ``'file_location'`` keyword can be used:
::

  nant.create_netcdf.main('ncas-ceilometer-3', file_location = '/path/to/save/location')


Other Options
^^^^^^^^^^^^^
All available options for this function can be found on `this API page <create_netcdf.html#ncas_amof_netcdf_template.create_netcdf.main>`_.

Add Data
--------
After the netCDF file is created, the file then needs to be opened in append mode, and data can then be added to the file:
::

  import ncas_amof_netcdf_template as nant
  from netCDF4 import Dataset

  # Read raw data into python
  # ...
  # backscatter_data = ...

  nant.create_netcdf.main('ncas-ceilometer-3', date='20221117', product = 'aerosol-backscatter')
  nc = Dataset('./ncas-ceilometer-3_iao_20221117_aerosol-backscatter_v1.0.nc', 'a')

  nant.util.update_variable(nc, 'attenuated_aerosol_backscatter_coefficient', backscatter_data)

  
where ``'attenuated_aerosol_backscatter_coefficient'`` is the name of the variable in the netCDF file, and ``'backscatter_data'`` is an array containing the data. This will also update the ``valid_min`` and ``valid_max`` attributes for each variable where applicable.


Metadata
--------


Remove Empty Variables
----------------------
Why would I want/needs to do this?
::

   nant.remove_empty_variables.main('ncas-aws-10_iao_20220427_surface-met_v1.0.nc')
	

Additional 
----------

Changing tag version
^^^^^^^^^^^^^^^^^^^^
