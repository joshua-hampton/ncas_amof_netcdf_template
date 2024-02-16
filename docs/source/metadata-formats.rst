Metadata File Formats
=====================

Metadata can be provided in one (or more if so desired) of four different formats - CSV, JSON, YAML and XML. This page describes the required layout of each of these formats.

CSV
---

Metadata in CSV files must be formatted with one attribute per line, starting with the name of the attribute, followed by its value (which can have commas in it), optionally followed by ``type=`` and/or ``append=``, for example:

.. code-block::
  
   attribute_name1,attribute_value1
   attribute_name2,153,type=integer,append=True
   attribute_name3,attribute_value3, value3 continued, type=string

This will write to three attributes into the netCDF file:

- ``attribute_name1`` will be written with the value ``attribute_value1``.
- ``attribute_name2`` will be written with the value ``153`` as an integer appended to the end of the current value for ``attribute_name2``.
- ``attribute_name3`` will be written with the value ``attribute_value3, value3 continued`` as a string.

JSON
----

The following example will produce the same end result as above:

.. code-block:: json

   {
       "attribute_name1": "attribute_value1",
       "attribute_name2": {
           "value": 153,
           "type": "int",
           "append": true
       },
       "attribute_name3": {
           "value": "attribute_value3, value3 continued",
           "type": "string"
       }
   }

In the JSON format, if the value given to the attribute name is a single value (as in ``attribute_name1``), then that will be the attributes value, with the default options for ``type`` and ``append`` applied. If the value given is a dictionary (as in ``attribute_name2`` and ``attribute_name3``, then it must have a key ``value`` for the value of the attribute, and can optionally have ``type`` and ``append`` given.

YAML
----

The same information as shown in the previous examples can be given in a YAML file:

.. code-block:: yaml

   attribute_name1: attribute_value1
   attribute_name2:
     value: 153
     type: int
     append: true
   attribute_name3:
     value: attribute_value3, value3 continued
     type: string


XML
---

These metadata can also be given in an XML file:

.. code-block:: xml

   <?xml version="1.0" encoding="UTF-8"?>
   <attributes>
       <attribute_name1>
           <value>attribute_value1</value>
       </attribute_name1>
       <attribute_name2>
           <value>153</value>
           <type>integer</type>
           <append>true</append>
       </attribute_name2>
       <attribute_name3>
           <value>attribute_value3, value3 continued</value>
           <type>string</value>
       </attribute_name3>
   </attributes>


