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
from . import values
from .__init__ import __version__


def add_attributes(
    ncfile: Dataset,
    instrument_dict: dict[
        str, dict[str, Union[str, list[str], dict[str, dict[str, Union[str, float]]]]]
    ],
    product: str,
    created_time: str,
    location: str,
    loc: str,
    use_local_files: Optional[str] = None,
    tag: str = "latest",
) -> None:
    """
    Adds all global attributes for a given product to the netCDF file.

    Args:
        ncfile (obj): netCDF file object
        instrument_dict (dict): information about the instrument from
                                tsv2dict.isntrument_dict.
        product (str): name of data product.
        create_time (str): time of file creation.
        location (str): value for the 'platform' global attribute.
        loc (str): value for the 'deployment_mode' global attribute, should be one of
                   'land', 'sea', 'air', or 'trajectory'.
        tag (str): tagged release version of AMF_CVs, or "latest" to get most recent
                release. Ignored if use_local_files is not None. Default latest.
        use_local_files (str or None): path to local directory where tsv files are
                                    stored. If "None", read from online. Default None.
    """
    for key, value in instrument_dict["common"]["attributes"].items():
        if value["Fixed Value"] != "":
            ncfile.setncattr(key, value["Fixed Value"])
        elif key == "source":
            ncfile.setncattr(key, instrument_dict["info"]["Descriptor"])
        elif key == "institution":
            ncfile.setncattr(key, "National Centre for Atmospheric Science (NCAS)")
        elif key == "platform":
            ncfile.setncattr(key, location)
        elif key == "instrument_manufacturer":
            ncfile.setncattr(key, instrument_dict["info"]["Manufacturer"])
        elif key == "instrument_model":
            ncfile.setncattr(key, instrument_dict["info"]["Model No."])
        elif key == "instrument_serial_number":
            ncfile.setncattr(key, instrument_dict["info"]["Serial Number"])
        elif key == "amf_vocabularies_release":
            if use_local_files:
                attrsdict = tsv2dict.tsv2dict_attrs(
                    f"{use_local_files}/_common/global-attributes.tsv"
                )
                tagurl = attrsdict["amf_vocabularies_release"]["Example"]
            else:
                if tag == "latest":
                    tag = values.get_latest_CVs_version()
                tagurl = f"https://github.com/ncasuk/AMF_CVs/releases/tag/{tag}"
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

    for key, value in instrument_dict[product]["attributes"].items():
        if value["Fixed Value"] != "":
            ncfile.setncattr(key, value["Fixed Value"])
        else:
            ncfile.setncattr(
                key,
                f"CHANGE: {value['Description']}. {value['Compliance checking rules']}",
            )


def add_dimensions(
    ncfile: Dataset,
    instrument_dict: dict[
        str, dict[str, Union[str, list[str], dict[str, dict[str, Union[str, float]]]]]
    ],
    product: str,
    dimension_lengths: dict[str, int],
) -> None:
    """
    Adds all dimensions for a given product to the netCDF file.

    Args:
        ncfile (obj): netCDF file object
        instrument_dict (dict): information about the instrument from
                                tsv2dict.isntrument_dict.
        product (str): name of data product.
        dimension_lengths (dict): length of each dimension.
    """
    for key, length in dimension_lengths.items():
        if (
            key in instrument_dict["common"]["dimensions"].keys()
            or key in instrument_dict[product]["dimensions"].keys()
        ):
            ncfile.createDimension(key, length)


def add_variables(
    ncfile: Dataset,
    instrument_dict: dict[
        str, dict[str, Union[str, list[str], dict[str, dict[str, Union[str, float]]]]]
    ],
    product: str,
    verbose: int = 0,
) -> None:
    """
    Adds all variables and their attributes for a given product to the netCDF file.

    Args:
        ncfile (obj): netCDF file object
        instrument_dict (dict): information about the instrument from
                                tsv2dict.isntrument_dict.
        product (str): name of data product.
        verbose (int): level of additional info to print. At the moment,
                       there is only 1 additional level. Default 0.
    """
    for obj in [product, "common"]:
        for key, value in instrument_dict[obj]["variables"].items():
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
                    print(f"WARN: No dimensions for variable {key} in product {obj}")
                    print("Variable not added file")
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
                        if (
                            isinstance(mdatvalue, str)
                            and mdatvalue == ""
                            and verbose >= 1
                        ):
                            print(
                                f"WARN: No value for attribute {mdatkey} "
                                "for variable {key}, attribute not added"
                            )
                        else:
                            var.setncattr(mdatkey, mdatvalue)


def make_netcdf(
    instrument: str,
    product: str,
    time: str,
    instrument_dict: dict[
        str, dict[str, Union[str, list[str], dict[str, dict[str, Union[str, float]]]]]
    ],
    loc: str = "land",
    dimension_lengths: dict[str, int] = {},
    verbose: int = 0,
    options: str = "",
    product_version: str = "1.0",
    file_location: str = ".",
    use_local_files: Optional[str] = None,
    tag: str = "latest",
    return_open: bool = True,
    chunk_by_dimension: Optional[dict[str, int]] = None,
    compression: Union[str, dict[str, str], None] = None,
    complevel: Union[int, dict[str, int]] = 4,
    shuffle: Union[bool, dict[str, bool]] = True,
) -> Union[None, Dataset]:
    """
    Makes netCDF file for given instrument and arguments.

    Args:
        instrument (str): ncas instrument name.
        product (str): name of data product.
        time (str): time that the data represents, in YYYYmmdd-HHMMSS format or
                    as much of as required.
        instrument_dict (dict): information about the instrument
                                from tsv2dict.isntrument_dict.
        loc (str): location of instrument, one of 'land', 'sea', 'air' or 'trajectory'.
                   Default 'land'.
        dimension_lengths (dict): lengths of dimensions in file. If not given,
                                  python will prompt the user to enter lengths
                                  for each dimension. Default {}.
        verbose (int): level of additional info to print. At the moment, there is
                       only 1 additional level. Default 0.
        options (str): options to be included in file name. All options should be in
                       one string and separated by an underscore ('_'), with up to
                       three options permitted. Default ''.
        product_version (str): version of the data file. Default '1.0'.
        file_location (str): where to write the netCDF file. Default '.'.
        use_local_files (str or None): path to local directory where tsv files are
                                    stored. If "None", read from online. Default None.
        tag (str): tagged release version of AMF_CVs, or 'latest' to get most recent
                release. Ignored if use_local_files is not None. Default "latest".
        return_open (bool): If True, return the netCDF file as an open object. If
                             False, closes netCDF file. Default True (option will
                             be removed in 2.5.0).
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
    if not return_open:
        warnings.warn(
            "Closing netCDF file immediately after creation is being deprecated."
            " This option will be removed from version 2.5.0, use return_open=True"
            " (default from 2.4.0) to return open netCDF object.",
            DeprecationWarning,
            stacklevel=2,
        )

    chunk_by_dimension = chunk_by_dimension or {}

    # add chunks to variables with defined chunk dimensions
    all_options = ["common", product]
    for prod in all_options:
        for var in (var_dict := instrument_dict[prod]["variables"]):
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
        instrument_dict["info"]["Mobile/Fixed (loc)"].split("-")[0].strip().lower()
        == "fixed"
    ):
        platform = (
            instrument_dict["info"]["Mobile/Fixed (loc)"].split("-")[-1].strip().lower()
        )
    else:
        platform = instrument_dict["info"]["Mobile/Fixed (loc)"].strip().lower()

    if options != "":
        no_options = len(options.split("_"))
        if no_options > 3:
            msg = f"Too many options, maximum allowed 3, given {no_options}"
            raise ValueError(msg)
        options = f"_{options}"

    filename = (
        f"{instrument}_{f'{platform}_' if platform != '' else ''}"
        f"{time}_{product}{options}_v{product_version}.nc"
    )

    ncfile = Dataset(f"{file_location}/{filename}", "w", format="NETCDF4_CLASSIC")
    created_time = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")

    add_attributes(
        ncfile,
        instrument_dict,
        product,
        created_time,
        platform,
        loc,
        use_local_files=use_local_files,
        tag=tag,
    )
    add_dimensions(ncfile, instrument_dict, product, dimension_lengths)
    add_variables(ncfile, instrument_dict, product, verbose=verbose)

    if return_open:
        return ncfile
    else:
        ncfile.close()


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
    return_open: bool = True,
    chunk_by_dimension: Optional[dict[str, int]] = None,
    compression: Union[str, dict[str, str], None] = None,
    complevel: Union[int, dict[str, int]] = 4,
    shuffle: Union[bool, dict[str, bool]] = True,
) -> Union[Dataset, None]:
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
        return_open (bool): If True, return the netCDF file as an open object. If
                             False, closes netCDF file. Default True (option will be
                             removed in 2.5.0).
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
    if not return_open:
        warnings.warn(
            "Closing netCDF file immediately after creation is being deprecated."
            " This option will be removed from version 2.5.0, use return_open=True"
            " (default from 2.4.0) to return open netCDF object.",
            DeprecationWarning,
            stacklevel=2,
        )

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

    product_dict = tsv2dict.product_dict(
        product,
        platform=platform,
        deployment_loc=deployment_loc,
        use_local_files=use_local_files,
        tag=tag,
    )

    # make sure we have dimension lengths for all expected dimensions
    all_dimensions = []
    dimlengths = {}
    for key, val in product_dict.items():
        if "dimensions" in val.keys() and (key == product or key == "common"):
            for dim in list(val["dimensions"].keys()):
                if dim not in all_dimensions:
                    all_dimensions.append(dim)
                    if (
                        isinstance(val["dimensions"][dim]["Length"], int)
                        or "<" not in val["dimensions"][dim]["Length"]
                    ):
                        dimlengths[dim] = int(val["dimensions"][dim]["Length"])
    for key, value in dimension_lengths.items():
        if key not in dimlengths.keys():
            dimlengths[key] = value
    for dim in all_dimensions:
        if dim not in dimlengths.keys():
            length = input(f"Enter length for dimension {dim}: ")
            dimlengths[dim] = int(length)

    # make the files
    if return_open:
        nc = make_netcdf(
            instrument_name,
            product,
            date,
            product_dict,
            loc=deployment_loc,
            dimension_lengths=dimlengths,
            verbose=verbose,
            options=options,
            product_version=product_version,
            file_location=file_location,
            use_local_files=use_local_files,
            tag=tag,
            return_open=return_open,
            chunk_by_dimension=chunk_by_dimension,
            compression=compression,
            complevel=complevel,
            shuffle=shuffle,
        )
        return nc
    else:
        make_netcdf(
            instrument_name,
            product,
            date,
            product_dict,
            loc=deployment_loc,
            dimension_lengths=dimlengths,
            verbose=verbose,
            options=options,
            product_version=product_version,
            file_location=file_location,
            use_local_files=use_local_files,
            tag=tag,
            return_open=return_open,
            chunk_by_dimension=chunk_by_dimension,
            compression=compression,
            complevel=complevel,
            shuffle=shuffle,
        )


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
    return_open: bool = True,
    chunk_by_dimension: Optional[dict[str, int]] = None,
    compression: Union[str, dict[str, str], None] = None,
    complevel: Union[int, dict[str, int]] = 4,
    shuffle: Union[bool, dict[str, bool]] = True,
) -> Union[Dataset, list[Dataset], None]:
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
                                are made.
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
        return_open (bool): If True, return the netCDF file as an open object. If
                             False, closes netCDF file. Default True (option will be
                             removed in 2.5.0).
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
    if not return_open:
        warnings.warn(
            "Closing netCDF file immediately after creation is being deprecated."
            " This option will be removed from version 2.5.0, use return_open=True"
            " (default from 2.4.0) to return open netCDF object.",
            DeprecationWarning,
            stacklevel=2,
        )

    if date is None:
        date = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d")

    chunk_by_dimension = chunk_by_dimension or {}

    instrument_dict = tsv2dict.instrument_dict(
        instrument, loc=loc, use_local_files=use_local_files, tag=tag
    )

    # check if platform needs changing
    if platform is not None:
        if "mobile" not in instrument_dict["info"]["Mobile/Fixed (loc)"].lower():
            print(
                "[WARNING]: Changing platform for an "
                f"observatory instrument {instrument}."
            )
        instrument_dict["info"]["Mobile/Fixed (loc)"] = platform

    # get and check our list of products
    tsvdictkeys = instrument_dict.keys()
    poss_products = list(tsvdictkeys)
    poss_products.remove("info")
    poss_products.remove("common")
    if products is None:  # user doesn't specify products, make all
        products = poss_products
    else:  # check user specified products are applicable for instrument
        remove_products = []
        if isinstance(products, str):
            products = [products]
        for product in products:
            if product not in poss_products:
                print(
                    f"ERROR: {product} is not available for this "
                    "instrument, will be skipped."
                )
                remove_products.append(product)
        for remove_product in remove_products:
            products.remove(remove_product)
    # so by now we should have our list of products, quit if we have no products
    if not isinstance(products, list) or len(products) == 0:
        msg = f"No valid products specified, valid products are {poss_products}"
        raise ValueError(msg)

    # make sure we have dimension lengths for all expected dimensions
    all_dimensions = []
    dimlengths = {}
    for key, val in instrument_dict.items():
        if "dimensions" in val.keys() and (key in products or key == "common"):
            for dim in list(val["dimensions"].keys()):
                if dim not in all_dimensions:
                    all_dimensions.append(dim)
                    if (
                        isinstance(val["dimensions"][dim]["Length"], int)
                        or "<" not in val["dimensions"][dim]["Length"]
                    ):
                        dimlengths[dim] = int(val["dimensions"][dim]["Length"])
    for key, value in dimension_lengths.items():
        if key not in dimlengths.keys():
            dimlengths[key] = value
    for dim in all_dimensions:
        if dim not in dimlengths.keys():
            length = input(f"Enter length for dimension {dim}: ")
            dimlengths[dim] = int(length)

    # make the files
    if return_open:
        ncfiles = []
        for product in products:
            ncfiles.append(
                make_netcdf(
                    instrument,
                    product,
                    date,
                    instrument_dict,
                    loc=loc,
                    dimension_lengths=dimlengths,
                    verbose=verbose,
                    options=options,
                    product_version=product_version,
                    file_location=file_location,
                    use_local_files=use_local_files,
                    tag=tag,
                    return_open=return_open,
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
    else:
        for product in products:
            make_netcdf(
                instrument,
                product,
                date,
                instrument_dict,
                loc=loc,
                dimension_lengths=dimlengths,
                verbose=verbose,
                options=options,
                product_version=product_version,
                file_location=file_location,
                use_local_files=use_local_files,
                tag=tag,
                return_open=return_open,
                chunk_by_dimension=chunk_by_dimension,
                compression=compression,
                complevel=complevel,
                shuffle=shuffle,
            )


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
