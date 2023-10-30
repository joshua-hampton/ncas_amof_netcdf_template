How to use
==========

Unless otherwise stated, all examples will use the ``ncas-ceilometer-3`` instrument as an example.

Create netCDF file
------------------
In its very simplest form:

.. code-block:: python

  import ncas_amof_netcdf_template as nant
  ncs = nant.create_netcdf.main('ncas-ceilometer-3', return_open=True)

This will create a netCDF file with today's date for all data products availalbe for the given instrument. If files for multiple products are made, the returned object will be a list containing all objects; if only a single file then just that netCDF file object is returned.

.. attention::
   If the ``return_open`` argument is omitted or set to False, then the ``create_netcdf.main`` function will close the netCDF file(s), rather than returning open files. This is the only behaviour before version 2.3 and is the default in 2.3, but ``return_open=True`` will be the default in 2.4, and from 2.5 the False option will be removed.

A netCDF file can also be created for a specific data product, rather than by a specific instrument.

.. code-block:: python

  nc = nant.create_netcdf.make_product_netcdf('surface-met', 'my-home-weather-station', return_open=True)

The file created in this example uses the ``surface-met`` data product definition, and requires the instrument name ``my-home-weather-station`` for the file name.


Dimensions
^^^^^^^^^^
Dimension sizes need to be defined when creating a netCDF file. Dimension lengths can be provided to the ``create_netcdf.main`` function as a dictionary:

.. code-block:: python

  ncs = nant.create_netcdf.main('ncas-ceilometer-3', dimension_lengths = {'time':96, 'altitude':45, 'layer_index':4}, return_open=True)


If dimensions aren't given, Python asks for the dimension lengths to be given:

.. code-block:: python

  ncs = nant.create_netcdf.main('ncas-ceilometer-3', return_open=True)
  Enter length for dimension time: 96
  Enter length for dimension altitude: 45
  Enter length for dimension layer_index: 4


Date
^^^^
The `file-naming convention <https://sites.google.com/ncas.ac.uk/ncasobservations/home/data-project/ncas-data-standards/ncas-amof/file-naming>`_ for the NCAS-GENERAL standard includes the date, and sometimes time, which the data within the file represents. By default, today's date will be used in the file name. This behaviour can be overridden by giving the date to the ``create_netcdf.main`` function:

.. code-block:: python

  ncs = nant.create_netcdf.main('ncas-ceilometer-3', return_open=True, date='20220214')


Data Products
^^^^^^^^^^^^^
List available data products for an instrument:

.. code-block:: python

  nant.create_netcdf.list_products('ncas-ceilometer-3')

Alternatively, all possible data products can be listed if no instrument name is given.

A data product can be defined in the call to create the netCDF file:

.. code-block:: python

  nc = nant.create_netcdf.main('ncas-ceilometer-3', return_open = True, products = 'aerosol-backscatter')

Or multiple products can be defined by using a list:

.. code-block:: python

  ncs = nant.create_netcdf.main('ncas-ceilometer-3', return_open = True, products = ['cloud-base','cloud-coverage'])


Deployment Modes
^^^^^^^^^^^^^^^^
NCAS instruments can be deployed in one of four deployment modes - land, sea, air, or trajectory. Each of these modes requires different dimensions and variables, and the deployment mode is recorded as a global attribute in the netCDF file. The default deployment mode is ``'land'``; however, an alternative deployment mode can be selected using the ``loc`` keyword:

.. code-block:: python

  ncs = nant.create_netcdf.main('ncas-ceilometer-3', return_open = True, loc = 'sea')


Output Location
^^^^^^^^^^^^^^^
The netCDF file will be written to the current working directory by default. To specify an alternative location, the ``'file_location'`` keyword can be used:

.. code-block:: python

  ncs = nant.create_netcdf.main('ncas-ceilometer-3', return_open = True, file_location = '/path/to/save/location')


Other Options
^^^^^^^^^^^^^
All available options for this function can be found on `this API page <create_netcdf.html#ncas_amof_netcdf_template.create_netcdf.main>`_.

Add Data
--------
After the netCDF file is created, the file then needs to be opened in append mode, and data can then be added to the file:

.. code-block:: python

  import ncas_amof_netcdf_template as nant
  from netCDF4 import Dataset

  # Read raw data into python
  # ...
  # backscatter_data = ...

  nc = nant.create_netcdf.main('ncas-ceilometer-3', return_open=True, date='20221117', product = 'aerosol-backscatter')

  nant.util.update_variable(nc, 'attenuated_aerosol_backscatter_coefficient', backscatter_data)


where ``'attenuated_aerosol_backscatter_coefficient'`` is the name of the variable in the netCDF file, and ``'backscatter_data'`` is an array containing the data. This will also update the ``valid_min`` and ``valid_max`` attributes for each variable where applicable.

Time
----
netCDF files that follow the NCAS-GENERAL metadata standard require a number of variables that correspond to time, or a portion of it, including (but not limited to) UNIX time, year, month and day.
This module `includes a function <util.html#ncas_amof_netcdf_template.util.get_times>`_ that will take a list of `datetime <https://docs.python.org/3/library/datetime.html>`_ objects and return the times in all the required formats.

.. code-block:: python

  import ncas_amof_netcdf_template as nant
  import datetime as dt

  # generate some times for this example
  t1 = dt.datetime.strptime('20221117T120000','%Y%m%dT%H%M%S')
  t2 = dt.datetime.strptime('20221117T120500','%Y%m%dT%H%M%S')
  times = [t1,t2]

  unix_times, day_of_year, years, months, days, hours, minutes, seconds, \
    time_coverage_start_unix, time_coverage_end_unix, file_date = nant.util.get_times(times)

This returns 8 lists with the time formatted as needed for variables in the netCDF file, as well as the first and last UNIX time stamp which can be used for the `time coverage start and end <#time-coverage-start-and-end>`_ metadata fields, and the date/time with the correct precision which, if required, could be used for the date in the ``create_netcdf.main`` function (e.g. in the example above it would return ``'20221117-12'``).

Metadata
--------
While all required metadata fields are added to the global attributes of the netCDF file, and in some cases the defined values are directly inserted, it is necessary to add further metadata values to the netCDF file, for example ``creator_name``. Fields that need metadata adding to them are initially given placeholder text which starts with the word "CHANGE" - simple interrogation of the created netCDF file will reveal which attributes need specifying.

Metadata that needs adding to the file can be organised into a CSV file, with one attribute-value pair on each line, for example a file called ``metadata.csv`` might look like

.. code-block:: none

  creator_name,Sam Jones
  creator_email,sam.jones@ncas.ac.uk

The contents of this CSV file can then be added to the netCDF file

.. code-block:: python

  nant.util.add_metadata_to_netcdf(nc, 'metadata.csv')


Latitude, Longitude, and Geospatial Bounds
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Although latitude and longitude are variables in the netCDF file, single value latitude and longitude values, with units `degrees North` and `degrees East` respectively can be included in the ``metadata.csv`` file, for example

.. code-block:: none

  latitude,53.801277
  longitude,-1.548567

The ``geospatial_bounds`` global attribute can also be defined directly in the metadata CSV file, or calculated from the latitude and longitude values:

.. code-block:: python

  nant.util.add_metadata_to_netcdf(nc, 'metadata.csv')
  geobounds = f"{ncfile.variables['latitude'][0]}N, {ncfile.variables['longitude'][0]}E"
  nc.setncattr('geospatial_bounds', geobounds)


Time Coverage Start and End
^^^^^^^^^^^^^^^^^^^^^^^^^^^
As mentioned `above <#time>`_, the ``time_coverage_start`` and ``time_coverage_end`` global attribute values can be obtained using the `get_times function <util.html#ncas_amof_netcdf_template.util.get_times>`_. The returns from this function include the first and last times as UNIX time stamps, which can be converted into the correct format for the global attribute values:

.. code-block:: python

  dt.datetime.fromtimestamp(time_coverage_start_unix, dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")


Remove Empty Variables
----------------------
The NCAS-GENERAL metadata standard can be seen as two parts: the first being "common" attributes, dimensions and variables that are required in all files, the second is "product-specific" information, for example the ``aerosol-backscatter`` product has variables ``attenuated_aerosol_backscatter_coefficient`` and ``range_squared_corrected_backscatter_power`` which are not in the ``cloud-base`` product. However, there may be cases where the instrument does not measure one or more of these product-specific variables. These empty product-specific variables should not be included in the final netCDF file.

.. code-block:: python

   nant.remove_empty_variables.main('./ncas-ceilometer-3_iao_20221117_aerosol-backscatter_v1.0.nc')

The netCDF file needs to be closed before this can be done, using ``nc.close()``.


Full Example
------------
An example of a full work flow using ``ncas_amof_netcdf_template`` to create the netCDF file, where is is assumed the actual reading of the raw data is handled by a function called ``read_data_from_raw_files``, and metadata is stored in a file called ``metadata.csv``.

.. code-block:: python

  import ncas_amof_netcdf_template as nant
  import datetime as dt
  from netCDF4 import Dataset

  # Read the raw data with user-written function, with times returning data in datetime format
  # In this example, `time` and `altitude` are the only dimensions
  backscatter_data, times, altitudes, other variables = read_data_from_raw_files()

  # Get all the time formats
  unix_times, day_of_year, years, months, days, hours, minutes, seconds, \
    time_coverage_start_unix, time_coverage_end_unix, file_date = nant.util.get_times(times)

  # Create netCDF file and read it back into the script in append mode
  nc = nant.create_netcdf.main('ncas-ceilometer-3', return_open = True, date = file_date,
                              dimension_lengths = {'time':len(times), 'altitude':len(altitudes)},
                              loc = 'land', products = 'aerosol-backscatter',
                              file_location = ncfile_location)

  # Add variable data to netCDF file
  nant.util.update_variable(nc, 'altitude', altitudes)
  nant.util.update_variable(nc, 'attenuated_aerosol_backscatter_coefficient',
                            backscatter_data)
  nant.util.update_variable(nc, 'time', unix_times)
  nant.util.update_variable(nc, 'day_of_year', day_of_year)
  nant.util.update_variable(nc, 'year', years)
  # and so on for each time format

  # Add metadata from file
  nant.util.add_metadata_to_netcdf(nc, 'metadata.csv')

  # Add time_coverage_start and time_coverage_end metadata using data from get_times
  nc.setncattr('time_coverage_start',
               dt.datetime.fromtimestamp(time_coverage_start_unix, dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S"))
  nc.setncattr('time_coverage_end',
               dt.datetime.fromtimestamp(time_coverage_end_unix, dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S"))

  # Look to see if latitude and longitude values have been added, and
  # geospatial_bounds NOT added, through the metadata file
  lat_masked = nc.variables['latitude'][0].mask
  lon_masked = nc.variables['longitude'][0].mask
  geospatial_attr_changed = "CHANGE" in nc.getncattr('geospatial_bounds')
  if geospatial_attr_changed and not lat_masked and not lon_masked:
      geobounds = f"{nc.variables['latitude'][0]}N, {nc.variables['longitude'][0]}E"
      nc.setncattr('geospatial_bounds', geobounds)

  # Close file
  nc.close()

  # Check for empty variables and remove if necessary
  nant.remove_empty_variables.main(f'{ncfile_location}/ncas-ceilometer-3_iao_{file_date}_aerosol-backscatter_v1.0.nc')
