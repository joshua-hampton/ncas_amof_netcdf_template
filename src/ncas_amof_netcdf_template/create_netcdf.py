"""
Create netCDF files for NCAS AMOF instruments that adhere to the NCAS-AMF-2.0.0
standard.

"""

from netCDF4 import Dataset
import datetime as dt
import copy
import numpy as np
import getpass
import socket
import warnings
from typing import Optional, Union

from . import tsv2dict
from .__init__ import __version__
from .file_info import FileInfo, convert_instrument_dict_to_file_info


def add_attributes(
    ncfile: Dataset,
    instrument_dict: Optional[
        dict[
            str,
            dict[str, Union[str, list[str], dict[str, dict[str, Union[str, float]]]]],
        ]
    ] = None,
    product: Optional[str] = None,
    created_time: Optional[str] = None,
    location: Optional[str] = None,
    loc: str = "land",
    use_local_files: Optional[str] = None,
    tag: str = "latest",
    instrument_file_info: Optional[FileInfo] = None,
) -> None:
    """
    Adds all global attributes for a given product to the netCDF file.

    Args:
        ncfile (obj): netCDF file object
        instrument_dict (dict): -DEPRECATED- information about the instrument from
                                tsv2dict.isntrument_dict. Use instrument_file_info
                                instead. Will be removed in version 2.7.0.
        product (str): -DEPRECATED- name of data product. Value will be obtained from
                       instrument_file_info. Option will be removed in version 2.7.0.
        created_time (str or None): time of file creation. If 'None', now will be used.
        location (str or None): -DEPRECATED- value for the 'platform' global attribute.
                                Value will be obtained from instrument_file_info. Option
                                will be removed in version 2.7.0.
        loc (str): -DEPRECATED- value for the 'deployment_mode' global attribute,
                   should be one of 'land', 'sea', 'air', or 'trajectory'. Value will
                   be obtained from instrument_file_info. Option will be removed in
                   version 2.7.0.
        instrument_file_info (FileInfo): information about instrument for making netCDF
                                         file, from
                                         ncas_amof_netcdf_template.file_info.FileInfo.
        tag (str): -DEPRECATED- tagged release version of AMF_CVs, or "latest" to get
                   most recent release. Ignored if use_local_files is not None. Value
                   will be obtained from instrument_file_info. Option will be removed
                   in version 2.7.0.
        use_local_files (str or None): path to local directory where tsv files are
                                    stored. If "None", read from online. Default None.
    """
    if instrument_dict is not None:
        if instrument_file_info is None:
            warnings.warn(
                "Using dictionary for instrument info is being deprecated, use the"
                " ncas_amof_netcdf_template.file_info.FileInfo class instead. Use of the"
                " instrument_dict option will be removed from version 2.7.0",
                DeprecationWarning,
                stacklevel=2,
            )
            if product is None:
                msg = (
                    "If instrument_dict is still being used, 'product' must be given."
                    " Preferred option is to switch to using instrument_file_info"
                    " instead."
                )
                raise ValueError(msg)
            instrument_file_info = convert_instrument_dict_to_file_info(
                instrument_dict,
                instrument_dict["info"]["instrument_name"],
                product,
                loc,
                tag,
            )
        else:
            warnings.warn(
                "instrument_dict and instrument_file_info both given, using"
                " instrument_file_info. Use of instrument_dict is being deprecated,"
                " and will be removed from version 2.7.0.",
                DeprecationWarning,
                stacklevel=2,
            )

    if instrument_file_info is None:
        msg = "No instrument file info given"
        raise ValueError(msg)

    if product is not None or location is not None or tag != "latest" or loc != "land":
        warnings.warn(
            "Defining any of 'product', 'location', 'loc' or 'tag' arguments is being"
            " deprecated, as this information will be pulled from"
            " instrument_file_info argument. These options will be removed from"
            " version 2.7.0.",
            DeprecationWarning,
            stacklevel=2,
        )
        if product is not None and product != instrument_file_info.data_product:
            msg = (
                f"Value of deprecated argument 'product' {product} does not match"
                " value of product in instrument_file_info"
                f" {instrument_file_info.data_product}"
                " (possibly converted from instrument_dict)."
            )
            raise ValueError(msg)
        elif (
            location is not None
            and location != instrument_file_info.instrument_data["Mobile/Fixed (loc)"]
        ):
            msg = (
                f"Value of deprecated argument 'location' {location} does not match"
                " value of location in instrument_file_info"
                f" {instrument_file_info.instrument_data['Mobile/Fixed (loc)']}."
                " (possibly converted from instrument_dict)."
            )
            raise ValueError(msg)
        elif tag != "latest" and tag != instrument_file_info.tag:
            msg = (
                f"Value of deprecated argument 'tag' {tag} does not macth value of"
                f" tag in instrument_file_info {instrument_file_info.tag}."
                " (possibly converted from instrument_dict)."
            )
            raise ValueError(msg)
        elif loc != "land" and loc != instrument_file_info.deployment_mode:
            msg = (
                f"Value of deprecated argument 'loc' {loc} does not match value of"
                f" loc in instrument_file_info {instrument_file_info.deployment_mode}"
                " (possibly converted from instrument_dict)."
            )
            raise ValueError(msg)

    if created_time is None:
        created_time = dt.datetime.now(tz=dt.timezone.utc).strftime("%Y%m%dT%H%M%S")

    for key, value in instrument_file_info.attributes.items():
        if value["Fixed Value"] != "":
            ncfile.setncattr(key, value["Fixed Value"])
        elif key == "source":
            if "Descriptor" in instrument_file_info.instrument_data.keys():
                ncfile.setncattr(
                    key, instrument_file_info.instrument_data["Descriptor"]
                )
            else:
                ncfile.setncattr(key, "n/a")
        elif key == "institution":
            ncfile.setncattr(key, "National Centre for Atmospheric Science (NCAS)")
        elif key == "platform":
            if "Mobile/Fixed (loc)" in instrument_file_info.instrument_data.keys():
                ncfile.setncattr(
                    key, instrument_file_info.instrument_data["Mobile/Fixed (loc)"]
                )
            else:
                ncfile.setncattr(key, "n/a")
        elif key == "instrument_manufacturer":
            if "Manufacturer" in instrument_file_info.instrument_data.keys():
                ncfile.setncattr(
                    key, instrument_file_info.instrument_data["Manufacturer"]
                )
            else:
                ncfile.setncattr(key, "n/a")
        elif key == "instrument_model":
            if "Model No." in instrument_file_info.instrument_data.keys():
                ncfile.setncattr(key, instrument_file_info.instrument_data["Model No."])
            else:
                ncfile.setncattr(key, "n/a")
        elif key == "instrument_serial_number":
            if "Serial Number" in instrument_file_info.instrument_data.keys():
                ncfile.setncattr(
                    key, instrument_file_info.instrument_data["Serial Number"]
                )
            else:
                ncfile.setncattr(key, "n/a")
        elif key == "amf_vocabularies_release":
            if use_local_files:
                attrsdict = tsv2dict.tsv2dict_attrs(
                    f"{use_local_files}/_common/global-attributes.tsv"
                )
                tagurl = attrsdict["amf_vocabularies_release"]["Example"]
            else:
                tagurl = f"https://github.com/ncasuk/AMF_CVs/releases/tag/{instrument_file_info.ncas_gen_version}"
            ncfile.setncattr(key, tagurl)
        elif key == "history":
            user = getpass.getuser()
            machine = socket.gethostname()
            history_text = (
                f"{created_time} - File created by {user} on {machine} "
                f"using the ncas_amof_netcdf_template v{__version__} python package"
            )
            ncfile.setncattr(key, history_text)
        elif key == "last_revised_date":
            ncfile.setncattr(key, created_time)
        elif key == "deployment_mode":
            ncfile.setncattr(key, loc)
        else:
            ncfile.setncattr(
                key,
                f"CHANGE: {value['Description']}. {value['Compliance checking rules']}",
            )


def add_dimensions(
    ncfile: Dataset,
    instrument_dict: Optional[
        dict[
            str,
            dict[str, Union[str, list[str], dict[str, dict[str, Union[str, float]]]]],
        ]
    ] = None,
    product: Optional[str] = None,
    dimension_lengths: Optional[dict[str, int]] = None,
    instrument_file_info: Optional[FileInfo] = None,
) -> None:
    """
    Adds all dimensions for a given product to the netCDF file.

    Args:
        ncfile (obj): netCDF file object
        instrument_dict (dict): -DEPRECATED- information about the instrument from
                                tsv2dict.isntrument_dict. Use instrument_file_info
                                instead. Will be removed in version 2.7.0.
        product (str): -DEPRECATED- name of data product. Value will now be obtained
                       from instrument_file_info. Option will be removed from version
                       2.7.0.
        dimension_lengths (dict): -DEPRECATED- length of each dimension. Values will
                                  now be obtained from instrument_file_info. Option
                                  will be removed from version 2.7.0.
        instrument_file_info (FileInfo): information about instrument for making netCDF
                                         file, from
                                         ncas_amof_netcdf_template.file_info.FileInfo.
    """
    if instrument_dict is not None:
        if instrument_file_info is None:
            warnings.warn(
                "Using dictionary for instrument info is being deprecated, use the"
                " ncas_amof_netcdf_template.file_info.FileInfo class instead. Use of the"
                " instrument_dict option will be removed from version 2.7.0",
                DeprecationWarning,
                stacklevel=2,
            )
            if product is None or dimension_lengths is None:
                msg = (
                    "If instrument_dict is still being used, 'product' and"
                    " 'dimension_lengths' must be given. Preferred option is to switch"
                    " to using instrument_file_info instead."
                )
                raise ValueError(msg)
        else:
            warnings.warn(
                "instrument_dict and instrument_file_info both given, using"
                " instrument_file_info. Use of instrument_dict is being deprecated,"
                " and will be removed from version 2.7.0.",
                DeprecationWarning,
                stacklevel=2,
            )

    if product is not None or dimension_lengths is not None:
        warnings.warn(
            "Options 'product' and 'dimension_lengths' are being deprecated, data will"
            " be retrieved from 'instrument_file_info' instead. These options will be"
            " removed in version 2.7.0.",
            DeprecationWarning,
            stacklevel=2,
        )
        if instrument_file_info is not None:
            if product is not None and product != instrument_file_info.data_product:
                msg = (
                    f"Value of deprecated argument 'product' {product} does not match"
                    " value of product in instrument_file_info"
                    f" {instrument_file_info.data_product}."
                )
                raise ValueError(msg)
            elif dimension_lengths is not None:
                for key, length in dimension_lengths.items():
                    if length != (
                        ifo_dim_len := instrument_file_info.dimensions[key]["Length"]
                    ):
                        msg = (
                            f"Value of dimension {key} ({length}) given in deprecated"
                            " argument 'dimension_lengths' does not match the value in"
                            f" instrument_file_info ({ifo_dim_len})."
                        )
                        raise ValueError(msg)

    if instrument_file_info is not None:
        for dim_name in instrument_file_info.dimensions.keys():
            ncfile.createDimension(
                dim_name, instrument_file_info.dimensions[dim_name]["Length"]
            )

    elif dimension_lengths is not None:
        for key, length in dimension_lengths.items():
            if (
                key in instrument_dict["common"]["dimensions"].keys()
                or key in instrument_dict[product]["dimensions"].keys()
            ):
                ncfile.createDimension(key, length)


def add_variables(
    ncfile: Dataset,
    instrument_dict: Optional[
        dict[
            str,
            dict[str, Union[str, list[str], dict[str, dict[str, Union[str, float]]]]],
        ]
    ] = None,
    product: Optional[str] = None,
    instrument_file_info: Optional[FileInfo] = None,
    verbose: int = 0,
) -> None:
    """
    Adds all variables and their attributes for a given product to the netCDF file.

    Args:
        ncfile (obj): netCDF file object
        instrument_dict (dict): -DEPRECATED- information about the instrument from
                                tsv2dict.isntrument_dict. Use instrument_file_info
                                instead. Will be removed in version 2.7.0.
        product (str): -DEPRECATED- name of data product. Value will be obtained from
                       instrument_file_info. Option will be removed in version 2.7.0.
        instrument_file_info (FileInfo): information about instrument for making netCDF
                                         file, from
                                         ncas_amof_netcdf_template.file_info.FileInfo.
        verbose (int): level of additional info to print. At the moment,
                       there is only 1 additional level. Default 0.
    """
    if instrument_dict is not None:
        if instrument_file_info is None:
            warnings.warn(
                "Using dictionary for instrument info is being deprecated, use the"
                " ncas_amof_netcdf_template.file_info.FileInfo class instead. Use of the"
                " instrument_dict option will be removed from version 2.7.0",
                DeprecationWarning,
                stacklevel=2,
            )
            if product is None:
                msg = (
                    "If instrument_dict is still being used, 'product' must be given."
                    " Preferred option is to switch to using instrument_file_info"
                    " instead."
                )
                raise ValueError(msg)
            instrument_file_info = convert_instrument_dict_to_file_info(
                instrument_dict,
                instrument_dict["info"]["instrument_name"],
                product,
                deployment_mode="land",
                tag="latest",
            )
        else:
            warnings.warn(
                "instrument_dict and instrument_file_info both given, using"
                " instrument_file_info. Use of instrument_dict is being deprecated,"
                " and will be removed from version 2.7.0.",
                DeprecationWarning,
                stacklevel=2,
            )

    if instrument_file_info is None:
        msg = "No instrument file info given"
        raise ValueError(msg)

    if product is not None:
        warnings.warn(
            "Option 'product' is being deprecated, data will be retrieved from"
            " instrument_file_info option. Option will be removed from version 2.7.0.",
            DeprecationWarning,
            stacklevel=2,
        )
        if product != instrument_file_info.data_product:
            msg = (
                f"Value of deprecated argument 'product' {product} does not match"
                " value of product in instrument_file_info"
                f" {instrument_file_info.data_product}"
                " (possibly converted from instrument_dict)."
            )
            raise ValueError(msg)

    for key, value in instrument_file_info.variables.items():
        # make sure variable doesn't already exist, warn if it does
        if key in ncfile.variables.keys():
            print(f"WARN: variable {key} defined multiple times.")
        else:
            # therefore, value is instrument_dict[obj]['variables'][key]
            # want to pop certain things here, but not for ever, so make tmp_value
            tmp_value = copy.copy(value)

            # error, there are some variables with dimensions
            # missing, error in spreadsheet
            # if we encounter one, we're going to print out an error
            # and forget about that variable
            if "dimension" not in tmp_value.keys():
                print(f"WARN: No dimensions for variable {key}")
                var_dims = ()
            else:
                var_dims = tmp_value.pop("dimension")
                # there was an error somewhere meaning 2 dimensions
                # had a '.' instead of ',' between them
                var_dims = var_dims.replace(".", ",")
                var_dims = tuple(x.strip() for x in var_dims.split(","))

            datatype = tmp_value.pop("type")

            if "_FillValue" in tmp_value:
                fill_value = float(tmp_value.pop("_FillValue"))
            else:
                fill_value = None

            if "chunksizes" in tmp_value:
                chunksizes = tmp_value.pop("chunksizes")
            else:
                chunksizes = None

            if "compression" in tmp_value:
                compression = tmp_value.pop("compression")
            else:
                compression = None

            if "complevel" in tmp_value:
                complevel = tmp_value.pop("complevel")
            else:
                complevel = 4

            if "shuffle" in tmp_value:
                shuffle = tmp_value.pop("shuffle")
            else:
                shuffle = True

            var = ncfile.createVariable(
                key,
                datatype,
                var_dims,
                fill_value=fill_value,
                chunksizes=chunksizes,
                compression=compression,
                complevel=complevel,
                shuffle=shuffle,
            )

            for mdatkey, mdatvalue in tmp_value.items():
                # flag meanings in the tsv files are separated by '|',
                # should be space separated
                if "|" in mdatvalue and "flag_meaning" in mdatkey:
                    mdatvalue = " ".join([i.strip() for i in mdatvalue.split("|")])
                # flag values are bytes, can't add byte array
                # into NETCDF4_CLASSIC so have to muddle a bit
                if "flag_value" in mdatkey and "qc" in key and var.dtype == np.int8:
                    # turn string "0b,1b..." into list of ints [0,1...]
                    mdatvalue = mdatvalue.strip(",")
                    newmdatvalue = [int(i.strip("b")) for i in mdatvalue.split(",")]
                    # turn list into array with int8 type
                    mdatvalue = np.array(newmdatvalue, dtype=np.int8)
                # print warning for example values,
                # and don't add example values for standard_name
                if (
                    mdatkey == "standard_name"
                    and ("EXAMPLE" in mdatvalue or mdatvalue == "")
                    and verbose >= 1
                ):
                    print(
                        f"WARN: No standard name for variable {key}, "
                        "standard_name attribute not added"
                    )
                elif "EXAMPLE" in mdatvalue and verbose >= 1:
                    print(
                        "WARN: example value for attribute "
                        f"{mdatkey} for variable {key}"
                    )
                # don't add EXAMPLE standard name
                if not (
                    mdatkey == "standard_name"
                    and ("EXAMPLE" in mdatvalue or mdatvalue == "")
                ):
                    # don't add empty attributes
                    if isinstance(mdatvalue, str) and mdatvalue == "" and verbose >= 1:
                        print(
                            f"WARN: No value for attribute {mdatkey} "
                            "for variable {key}, attribute not added"
                        )
                    else:
                        var.setncattr(mdatkey, mdatvalue)


def make_netcdf(
    instrument: Optional[str] = None,
    product: Optional[str] = None,
    time: str = dt.datetime.now(tz=dt.timezone.utc).strftime("%Y%m%d"),
    instrument_dict: Optional[
        dict[
            str,
            dict[str, Union[str, list[str], dict[str, dict[str, Union[str, float]]]]],
        ]
    ] = None,
    loc: str = "land",
    dimension_lengths: dict[str, int] = {},
    verbose: int = 0,
    options: str = "",
    product_version: str = "1.0",
    file_location: str = ".",
    use_local_files: Optional[str] = None,
    tag: str = "latest",
    chunk_by_dimension: Optional[dict[str, int]] = None,
    compression: Union[str, dict[str, str], None] = None,
    complevel: Union[int, dict[str, int]] = 4,
    shuffle: Union[bool, dict[str, bool]] = True,
    instrument_file_info: Optional[FileInfo] = None,
) -> Dataset:
    """
    Makes netCDF file for given instrument and arguments.

    Args:
        instrument (str or None): -DEPRECATED- ncas instrument name. Value will be
                                  retrived from instrument_file_info. Option will be
                                  removed in version 2.7.0. Default None.
        product (str or None): -DEPRECATED- name of data product. Value will be
                               retrieved from instrument_file_info. Option will be
                               removed in version 2.7.0. Default None.
        time (str): time that the data represents, in YYYYmmdd-HHMMSS format or
                    as much of as required. Default is now in YYYYmmdd format.
        instrument_dict (dict or None): -DEPRECATED- information about the instrument
                                        from tsv2dict.instrument_dict. Use
                                        instrument_file_info argument instead. Will be
                                        removed in version 2.7.0.
        instrument_file_info (FileInfo or None): information about the instrument,
                                                 from file_info.FileInfo.
        loc (str): -DEPRECATED- location of instrument, one of 'land', 'sea', 'air' or
                   'trajectory'. Value will be retrieved from instrument_file_info.
                   Option will be removed in version 2.7.0. Default 'land'.
        dimension_lengths (dict): -DEPRECATED- lengths of dimensions in file. If not
                                  given, python will prompt the user to enter lengths
                                  for each dimension. Values will be retrieved from
                                  instrument_file_info. Option will be removed in
                                  version 2.7.0. Default {}.
        verbose (int): level of additional info to print. At the moment, there is
                       only 1 additional level. Default 0.
        options (str): options to be included in file name. All options should be in
                       one string and separated by an underscore ('_'), with up to
                       three options permitted. Default ''.
        product_version (str): version of the data file. Default '1.0'.
        file_location (str): where to write the netCDF file. Default '.'.
        use_local_files (str or None): path to local directory where tsv files are
                                    stored. If "None", read from online. Default None.
        tag (str): -DEPRECATED- tagged release version of AMF_CVs, or 'latest' to get
                   most recent release. Ignored if use_local_files is not None. Value
                   will be retrieved from instrument_file_info. Option will be removed
                   in verison 2.7.0. Default "latest".
        chunk_by_dimension (dict): chunk sizes to use in each dimension.
                                   Default None (no chunking).
        compression (str or dict): compression algorithm to be used to store data. If
                                   string, then compression option passed to all
                                   variables. If dictionary, should be variable:compression
                                   pairs, and compression option passed to just the specified
                                   variables. Should be one of the options available in
                                   the netCDF4 python module. Default is None (no compression).
        complevel (int or dict): level of compression to be used, between 0 (no compression)
                                 and 9 (most compression). Either integer value or dictionary
                                 with variable:integer pairs. Default is 4. Ignored if no
                                 compression used.
        shuffle (bool or dict): whether to use the HDF5 shuffle filter before compressing with
                                zlib, significantly improving compression. Default is True.
                                Ignored if compression is not zlib.

    Returns:
        netCDF file object or nothing.
    """
    if instrument_dict is not None:
        if instrument_file_info is None:
            warnings.warn(
                "Using dictionary for instrument info is being deprecated, use the"
                " ncas_amof_netcdf_template.file_info.FileInfo class instead. Use of the"
                " instrument_dict option will be removed from version 2.7.0",
                DeprecationWarning,
                stacklevel=2,
            )
            if product is None:
                msg = (
                    "If instrument_dict is still being used, 'product' must be given."
                    " Preferred option is to switch to using instrument_file_info"
                    " instead."
                )
                raise ValueError(msg)
            instrument_file_info = convert_instrument_dict_to_file_info(
                instrument_dict,
                instrument_dict["info"]["instrument_name"],
                product,
                loc,
                tag,
            )
        else:
            warnings.warn(
                "instrument_dict and instrument_file_info both given, using"
                " instrument_file_info. Use of instrument_dict is being deprecated,"
                " and will be removed from version 2.7.0.",
                DeprecationWarning,
                stacklevel=2,
            )

    if instrument_file_info is None:
        msg = "No instrument file info given"
        raise ValueError(msg)

    if (
        instrument is not None
        or product is not None
        or loc != "land"
        or dimension_lengths != {}
        or tag != "latest"
    ):
        warnings.warn(
            "Options 'instrument', 'product', 'loc', 'dimension_lengths', and 'tag'"
            " are being deprecated, data will be retrieved from instrument_file_info"
            " option. Option will be removed from version 2.7.0.",
            DeprecationWarning,
            stacklevel=2,
        )
        if (
            instrument is not None
            and instrument != instrument_file_info.instrument_name
        ):
            msg = (
                f"Value of deprecated argument 'instrument' {instrument} does not"
                " match value of instrument name in instrument_file_info"
                f" {instrument_file_info.instrument_name}"
                " (possibly converted from instrument_dict)."
            )
            raise ValueError(msg)
        elif product is not None and product != instrument_file_info.data_product:
            msg = (
                f"Value of deprecated argument 'product' {product} does not match"
                " value of product in instrument_file_info"
                f" {instrument_file_info.data_product}"
                " (possibly converted from instrument_dict)."
            )
            raise ValueError(msg)
        elif tag != "latest" and tag != instrument_file_info.tag:
            msg = (
                f"Value of deprecated argument 'tag' {tag} does not macth value of"
                f" tag in instrument_file_info {instrument_file_info.tag}."
                " (possibly converted from instrument_dict)."
            )
            raise ValueError(msg)
        elif loc != "land" and loc != instrument_file_info.deployment_mode:
            msg = (
                f"Value of deprecated argument 'loc' {loc} does not match value of"
                f" loc in instrument_file_info {instrument_file_info.deployment_mode}"
                " (possibly converted from instrument_dict)."
            )
            raise ValueError(msg)
        elif dimension_lengths is not None:
            for key, length in dimension_lengths.items():
                if length != (
                    ifo_dim_len := instrument_file_info.dimensions[key]["Length"]
                ):
                    msg = (
                        f"Value of dimension {key} ({length}) given in deprecated"
                        " argument 'dimension_lengths' does not match the value in"
                        f" instrument_file_info ({ifo_dim_len})."
                    )
                    raise ValueError(msg)

    chunk_by_dimension = chunk_by_dimension or {}

    # add chunks to variables with defined chunk dimensions
    for var in (var_dict := instrument_file_info.variables):
        if "dimension" in var_dict[var].keys():
            var_dims = var_dict[var]["dimension"]
            var_dims = var_dims.replace(".", ",")
            var_dims = [x.strip() for x in var_dims.split(",")]
            if all(var_dim in chunk_by_dimension.keys() for var_dim in var_dims):
                chunksizes = tuple(
                    [int(chunk_by_dimension[var_dim]) for var_dim in var_dims]
                )
                var_dict[var]["chunksizes"] = chunksizes
        if isinstance(compression, str):
            var_dict[var]["compression"] = compression
        elif isinstance(compression, dict) and var in compression.keys():
            var_dict[var]["compression"] = compression[var]
        else:
            var_dict[var]["compression"] = None

        if isinstance(complevel, int):
            var_dict[var]["complevel"] = complevel
        elif isinstance(complevel, dict) and var in complevel.keys():
            var_dict[var]["complevel"] = complevel[var]
        else:
            var_dict[var]["complevel"] = 4

        if isinstance(shuffle, bool):
            var_dict[var]["shuffle"] = shuffle
        elif isinstance(shuffle, dict) and var in shuffle.keys():
            var_dict[var]["shuffle"] = shuffle[var]
        else:
            var_dict[var]["shuffle"] = True

    if (
        instrument_file_info.instrument_data["Mobile/Fixed (loc)"]
        .split("-")[0]
        .strip()
        .lower()
        == "fixed"
    ):
        platform = (
            instrument_file_info.instrument_data["Mobile/Fixed (loc)"]
            .split("-")[-1]
            .strip()
            .lower()
        )
    else:
        platform = (
            instrument_file_info.instrument_data["Mobile/Fixed (loc)"].strip().lower()
        )
    instrument_file_info.instrument_data["Mobile/Fixed (loc)"] = platform

    if options != "":
        no_options = len(options.split("_"))
        if no_options > 3:
            msg = f"Too many options, maximum allowed 3, given {no_options}"
            raise ValueError(msg)
        options = f"_{options}"

    filename = (
        f"{instrument_file_info.instrument_name}_{f'{platform}_' if platform != '' else ''}"
        f"{time}_{instrument_file_info.data_product}{options}_v{product_version}.nc"
    )

    ncfile = Dataset(f"{file_location}/{filename}", "w", format="NETCDF4_CLASSIC")
    created_time = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")

    add_attributes(
        ncfile,
        instrument_file_info=instrument_file_info,
        use_local_files=use_local_files,
        created_time=created_time,
    )
    add_dimensions(ncfile, instrument_file_info=instrument_file_info)
    add_variables(ncfile, instrument_file_info=instrument_file_info, verbose=verbose)

    return ncfile


def list_products(
    instrument: str = "all",
    use_local_files: Optional[str] = None,
    tag: str = "latest",
) -> list[str]:
    """
    Lists available products, either for a specific instrument or all data products.

    Args:
        instrument (str): ncas instrument name, or "all" for all data products.
                          Default "all".
        use_local_files (str or None): path to local directory where tsv files are
                                    stored. If "None", read from online. Default None.
        tag (str): tagged release of definitions, or 'latest' to get most recent
                release. Ignored if use_local_files is not None. Default "latest".

    Returns:
        list of products available for the given instrument
    """
    if instrument != "all":
        instrument_dict = tsv2dict.instrument_dict(
            instrument, use_local_files=use_local_files, tag=tag
        )
        tsvdictkeys = instrument_dict.keys()
        products = list(tsvdictkeys)
        products.remove("info")
        products.remove("common")
    else:
        products = tsv2dict.list_all_products(use_local_files=use_local_files, tag=tag)
    return products


def make_product_netcdf(
    product: str,
    instrument_name: str,
    date: Optional[str] = None,
    dimension_lengths: dict[str, int] = {},
    platform: str = "",
    instrument_loc: str = "",
    deployment_loc: str = "land",
    verbose: int = 0,
    options: str = "",
    product_version: str = "1.0",
    file_location: str = ".",
    use_local_files: Optional[str] = None,
    tag: str = "latest",
    chunk_by_dimension: Optional[dict[str, int]] = None,
    compression: Union[str, dict[str, str], None] = None,
    complevel: Union[int, dict[str, int]] = 4,
    shuffle: Union[bool, dict[str, bool]] = True,
) -> Dataset:
    """
    Create an AMOF-like netCDF file for a given data product. This means files can be
    made to the NCAS-GENERAL standard for instruments that aren't part of the AMOF
    instrument suite.

    Args:
        product (str): name of data product
        instrument_name (str): instrument name for use in file name
        date (str): date for file, format YYYYmmdd. If not given, finds today's date
        dimension_lengths (dict): dictionary of dimension:length. If length not given
                                  for needed dimension, user will be asked to type
                                  in dimension length
        platform (str): observatory or location of the instrument. Default "".
        instrument_loc (str): [DEPRECATED - use "platform" instead] observatory or
                              location of the instrument. Default "".
        deployment_loc (str): one of 'land', 'sea', 'air', 'trajectory'.
                              Default "land".
        verbose (int): level of info to print out. Note that at the moment there is
                        only one additional layer, this may increase in future.
        options (str): options to be included in file name. All options should be in
                       one string and separated by an underscore ("_"), with up to
                       three options permitted. Default "".
        product_version (str): version of the data file. Default "1.0".
        file_location (str): where to write the netCDF file. Default ".".
        use_local_files (str or None): path to local directory where tsv files are
                                    stored. If "None", read from online. Default None.
        tag (str): tagged release of definitions, or 'latest' to get most recent
                release. Ignored if use_local_files is not None. Default "latest".
        chunk_by_dimension (dict): chunk sizes to use in each dimension
                                   Default None (no chunking).
        compression (str or dict): compression algorithm to be used to store data. If
                                   string, then compression option passed to all
                                   variables. If dictionary, should be variable:compression
                                   pairs, and compression option passed to just the specified
                                   variables. Should be one of the options available in
                                   the netCDF4 python module. Default is None (no compression).
        complevel (int or dict): level of compression to be used, between 0 (no compression)
                                 and 9 (most compression). Either integer value or dictionary
                                 with variable:integer pairs. Default is 4. Ignored if no
                                 compression used.
        shuffle (bool or dict): whether to use the HDF5 shuffle filter before compressing with
                                zlib, significantly improving compression. Default is True.
                                Ignored if compression is not zlib.

    Returns:
        netCDF file object or nothing.
    """
    chunk_by_dimension = chunk_by_dimension or {}

    if platform != "" and instrument_loc != "":
        warnings.warn(
            "Both platform and instrument_loc are given, using platform."
            " instrument_loc will be removed from version 2.6.0.",
            DeprecationWarning,
            stacklevel=2,
        )

    if instrument_loc != "":
        warnings.warn(
            "instrument_loc is deprecated, use platform instead."
            " This option will be removed from version 2.6.0.",
            DeprecationWarning,
            stacklevel=2,
        )
        platform = instrument_loc

    if date is None:
        date = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d")

    product_file_info = FileInfo(
        instrument_name,
        product,
        deployment_mode=deployment_loc,
        tag=tag,
        use_local_files=use_local_files,
    )
    product_file_info.get_common_info()
    product_file_info.get_deployment_info()
    product_file_info.get_product_info()

    product_file_info.instrument_data["Mobile/Fixed (loc)"] = platform

    # make sure we have dimension lengths for all expected dimensions
    for key, val in product_file_info.dimensions.items():
        if not isinstance(val["Length"], int):
            if key in dimension_lengths.keys():
                val["Length"] = int(dimension_lengths[key])
            else:
                length = input(f"Enter length for dimension {key}: ")
                val["Length"] = int(length)

    # make the files
    nc = make_netcdf(
        time=date,
        instrument_file_info=product_file_info,
        verbose=verbose,
        options=options,
        product_version=product_version,
        file_location=file_location,
        chunk_by_dimension=chunk_by_dimension,
        compression=compression,
        complevel=complevel,
        shuffle=shuffle,
    )
    return nc


def main(
    instrument: str,
    date: Optional[str] = None,
    dimension_lengths: dict[str, int] = {},
    platform: Optional[str] = None,
    loc: str = "land",
    products: Union[str, list[str], None] = None,
    verbose: int = 0,
    options: str = "",
    product_version: str = "1.0",
    file_location: str = ".",
    use_local_files: Optional[str] = None,
    tag: str = "latest",
    chunk_by_dimension: Optional[dict[str, int]] = None,
    compression: Union[str, dict[str, str], None] = None,
    complevel: Union[int, dict[str, int]] = 4,
    shuffle: Union[bool, dict[str, bool]] = True,
) -> Union[Dataset, list[Dataset]]:
    """
    Create 'just-add-data' AMOF-compliant netCDF file

    Args:
        instrument (str): ncas instrument name
        date (str): date for file, format YYYYmmdd. If not given, finds today's date
        dimension_lengths (dict): dictionary of dimension:length. If length not given
                                  for needed dimension, user will be asked to type
                                  in dimension length
        platform (str): observatory or location of the instrument. If not given or is
                        None, will use default platform for instrument from instrument
                        vocabularies. Default None.
        loc (str): one of 'land', 'sea', 'air', 'trajectory'
        products (str or list): string of one product or list of multiple products to
                                make netCDF file for this instrument. If None, then
                                all available products for the defined instrument
                                are made. -DEPRECATION WARNING- option to specify
                                either a list of 'None' is being deprecated and will
                                be removed in version 2.7.0. Use single data product.
        verbose (int): level of info to print out. Note that at the moment there is
                        only one additional layer, this may increase in future.
        options (str): options to be included in file name. All options should be in
                       one string and separated by an underscore ('_'), with up to
                       three options permitted. Default ''.
        product_version (str): version of the data file. Default '1.0'.
        file_location (str): where to write the netCDF file. Default '.'.
        use_local_files (str or None): path to local directory where tsv files are
                                    stored. If "None", read from online. Default None.
        tag (str): tagged release of definitions, or 'latest' to get most recent
                release. Ignored if use_local_files is not None. Default "latest".
        chunk_by_dimension (dict): chunk sizes to use in each dimension
                                   Default None (no chunking).
        compression (str or dict): compression algorithm to be used to store data. If
                                   string, then compression option passed to all
                                   variables. If dictionary, should be variable:compression
                                   pairs, and compression option passed to just the specified
                                   variables. Should be one of the options available in
        complevel (int or dict): level of compression to be used, between 0 (no compression)
                                 and 9 (most compression). Either integer value or dictionary
                                 with variable:integer pairs. Default is 4. Ignored if no
                                 compression used.
        shuffle (bool or dict): whether to use the HDF5 shuffle filter before compressing with
                                zlib, significantly improving compression. Default is True.
                                Ignored if compression is not zlib.
                                   the netCDF4 python module. Default is None (no compression).

    Returns:
        netCDF file object or nothing
    """
    if date is None:
        date = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d")

    chunk_by_dimension = chunk_by_dimension or {}

    if isinstance(products, str):
        products = [products]
    elif products is None:
        products = list_products(instrument=instrument, tag=tag)
        warnings.warn(
            "Passing 'None' as argument for 'products' is being deprecated. Use single"
            " data product for this argument. Available data products for instrument"
            f"{instrument} are {products}. The option to use 'None' will be removed"
            " from version 2.7.0.",
            DeprecationWarning,
            stacklevel=2,
        )
    elif isinstance(products, list):
        warnings.warn(
            "Giving multiple data products to the 'products' argument is"
            " being deprecated. Use single data product as a string for this argument."
            " The option to give a list will be removed from version 2.7.0.",
            DeprecationWarning,
            stacklevel=2,
        )

    ncfiles = []

    if len(products) == 0:
        msg = "No products specified"
        raise ValueError(msg)

    for product in products:
        instrument_file_info = FileInfo(
            instrument,
            product,
            deployment_mode=loc,
            tag=tag,
            use_local_files=use_local_files,
        )
        instrument_file_info.get_product_info()
        instrument_file_info.get_deployment_info()
        instrument_file_info.get_instrument_info()
        instrument_file_info.get_common_info()

        # check if platform needs changing
        if platform is not None:
            if (
                "mobile"
                not in instrument_file_info.instrument_data[
                    "Mobile/Fixed (loc)"
                ].lower()
            ):
                print(
                    "[WARNING]: Changing platform for an "
                    f"observatory instrument {instrument}."
                )
            instrument_file_info.instrument_data["Mobile/Fixed (loc)"] = platform

        # make sure we have dimension lengths for all expected dimensions
        for key, val in instrument_file_info.dimensions.items():
            if not isinstance(val["Length"], int):
                if key in dimension_lengths.keys():
                    val["Length"] = int(dimension_lengths[key])
                else:
                    length = input(f"Enter length for dimension {key}: ")
                    val["Length"] = int(length)

        # make the files
        ncfiles.append(
            make_netcdf(
                time=date,
                instrument_file_info=instrument_file_info,
                verbose=verbose,
                options=options,
                product_version=product_version,
                file_location=file_location,
                chunk_by_dimension=chunk_by_dimension,
                compression=compression,
                complevel=complevel,
                shuffle=shuffle,
            )
        )
    if len(ncfiles) == 1:
        return ncfiles[0]
    else:
        return ncfiles


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Create AMOF-compliant netCDF file with no data."
    )
    parser.add_argument("instrument", type=str, help="Name of NCAS instrument.")
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Level of additional info to print.",
    )
    parser.add_argument(
        "-d",
        "--date",
        type=str,
        help="Date for data in file, YYYYmmdd format. If not given, default to today.",
        default=None,
        dest="date",
    )
    parser.add_argument(
        "-l",
        "--dim-lengths",
        nargs="*",
        help=(
            "Length for each dimension, e.g. -l time 96 altitude 45. If not given, "
            "or required dimension missing, python will ask for user input."
        ),
        dest="dim_lengths",
    )
    parser.add_argument(
        "-m",
        "--deployment-mode",
        type=str,
        choices=["land", "sea", "air", "trajectory"],
        help=(
            "Deployment mode of instrument, one of 'land', 'sea', 'air', "
            "'trajectory'. Default is 'land'."
        ),
        default="land",
        dest="deployment",
    )
    parser.add_argument(
        "--list-products",
        action="store_true",
        dest="list_products",
        help=(
            "If given, available products for instrument are printed, "
            "then script exits."
        ),
    )
    parser.add_argument(
        "-p",
        "--products",
        nargs="*",
        default=None,
        help=(
            "Products for instrument to make netCDF file. If not given, netCDF files "
            "for all applicable products are made."
        ),
        dest="products",
    )
    parser.add_argument(
        "-k",
        "--kwargs",
        nargs="*",
        help=(
            "Addtitional keyword arguments supplied to create_netcdf.make_netcdf "
            "through create_netcdf.main. Should be given as `argument value`, "
            "implemented kwargs are file_location, options, product_version. If "
            "argument option is given, each option for the netcdf file name should "
            "be separated by an underscore, e.g. `option opt1_opt2_opt3`"
        ),
        dest="kwargs",
    )
    args = parser.parse_args()

    if args.list_products:
        print(list_products(args.instrument))
    else:
        dim_lengths = {}
        if args.dim_lengths is not None:
            if len(args.dim_lengths) % 2 != 0:
                msg = "-l/--dim-lengths option should be `dimension length` pairs"
                raise ValueError(msg)
            for i in range(0, len(args.dim_lengths), 2):
                dim_lengths[args.dim_lengths[i]] = int(args.dim_lengths[i + 1])

        kwargs = {}
        if args.kwargs is not None:
            current_val = None
            for val in args.kwargs:
                if val in ["file_location", "options", "product_version"]:
                    kwargs[val] = ""
                    current_val = val
                elif current_val is not None:
                    kwargs[current_val] = f"{kwargs[current_val]}{val}"
                else:
                    msg = "Not sure what to do with given input, exiting..."
                    print(args.kwargs)
                    raise ValueError(msg)

        main(
            args.instrument,
            date=args.date,
            dimension_lengths=dim_lengths,
            loc=args.deployment,
            products=args.products,
            verbose=args.verbose,
            **kwargs,
        )
