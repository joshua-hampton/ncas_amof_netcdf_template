"""
Take tsv files and return data as dictionaries
useful for creating netCDF files.

"""

import pandas as pd
import re
import requests
import os

from . import values


def tsv2dict_vars(tsv_file):
    """
    For a given tsv file from
    https://github.com/ncasuk/AMF_CVs/tree/main/product-definitions/tsv
    for data variables, return dictionary of variables and their attributes.

    Args:
        tsv_file (str): URL to location of tsv file

    Returns:
        dictionary of variables and attributes
    """
    df_vars = pd.read_csv(tsv_file, sep="\t")
    df_vars = df_vars.fillna("")

    all_vars_dict = {}
    current_var_dict = {}
    first_loop = True
    current_var = ""

    for current_line in df_vars.iloc:
        if current_line["Variable"] != "":
            if not first_loop:
                all_vars_dict[current_var] = current_var_dict
                current_var_dict = {}
            else:
                first_loop = False
            current_var = current_line["Variable"]
            current_var_dict = {}
            # continue
        if current_line["Attribute"] != "":
            if (
                current_line["Value"] == ""
                and "example value" in current_line.keys()
                and current_line["example value"] != ""
            ):
                current_var_dict[
                    current_line["Attribute"]
                ] = f"EXAMPLE: {current_line['example value']}"
            else:
                current_var_dict[current_line["Attribute"]] = current_line["Value"]
    all_vars_dict[current_var] = current_var_dict

    return all_vars_dict


def tsv2dict_dims(tsv_file):
    """
    For a given tsv file from
    https://github.com/ncasuk/AMF_CVs/tree/main/product-definitions/tsv
    for data dimensions, return dictionary of dimensions and additional info.

    Args:
        tsv_file (str): URL to location of tsv file

    Returns:
        dictionary of dimensions and info
    """
    df_dims = pd.read_csv(tsv_file, sep="\t")
    df_dims = df_dims.fillna("")

    all_dims_dict = {}

    for dim in df_dims.iloc:
        dim_dict = dim.to_dict()
        dim_name = dim_dict.pop("Name")
        all_dims_dict[dim_name] = dim_dict

    return all_dims_dict


def tsv2dict_attrs(tsv_file):
    """
    For a given tsv file from
    https://github.com/ncasuk/AMF_CVs/tree/main/product-definitions/tsv for data
    global attributes, return dictionary of attributes and associated values and info.

    Args:
        tsv_file (str): URL to location of tsv file

    Returns:
        dictionary of global attributes and associated values and info
    """
    df_attrs = pd.read_csv(tsv_file, sep="\t")
    df_attrs = df_attrs.fillna("")

    all_attrs_dict = {}

    for dim in df_attrs.iloc:
        dim_dict = dim.to_dict()
        dim_name = dim_dict.pop("Name")
        all_attrs_dict[dim_name] = dim_dict

    return all_attrs_dict


def tsv2dict_instruments(tsv_file):
    """
    For a given tsv file from
    https://github.com/ncasuk/AMF_CVs/tree/main/product-definitions/tsv for ncas- or
    community-instruments, return dictionary of instruments and associated information.

    Args:
        tsv_file (str): URL to location of tsv file

    Returns:
        dictionary of instruments and associated information
    """
    df_instruments = pd.read_csv(tsv_file, sep="\t")
    df_instruments = df_instruments.fillna("")

    all_instruments = {}

    for current_instrument in df_instruments.iloc:
        inst_dict = current_instrument.to_dict()
        inst_name = inst_dict.pop("New Instrument Name")
        data_products = re.split(",| |\|", inst_dict["Data Product(s)"])
        data_products = list(filter(None, data_products))
        inst_dict["Data Product(s)"] = data_products
        all_instruments[inst_name] = inst_dict

    return all_instruments


def create_variables_tsv_url(product, use_local_files=None, tag="latest"):
    """
    Returns URL for tsv file of variables specific to  a given product and tag
    release or branch.

    Args:
        product (str): data product
        use_local_files (str or None): path to local directory where tsv files are
                                    stored. If "None", read from online. Default None.
        tag (str): tagged release of definitions, or 'latest' to get most recent
                release. Ignored if use_local_files is not None. Default "latest".

    Return:
        URL
    """
    if use_local_files:
        file_loc = use_local_files
    else:
        if tag == "latest":
            tag = values.get_latest_CVs_version()
        file_loc = (
            f"https://raw.githubusercontent.com/ncasuk/AMF_CVs/{tag}"
            "/product-definitions/tsv"
        )
    return f"{file_loc}/{product}/variables-specific.tsv"


def create_dimensions_tsv_url(product, use_local_files=None, tag="latest"):
    """
    Returns URL for tsv file of dimensions specific to a given product and tag
    release or branch.

    Args:
        product (str): data product
        use_local_files (str or None): path to local directory where tsv files are
                                    stored. If "None", read from online. Default None.
        tag (str): tagged release of definitions, or 'latest' to get most recent
                release. Ignored if use_local_files is not None. Default "latest".

    Return:
        URL
    """
    if use_local_files:
        file_loc = use_local_files
    else:
        if tag == "latest":
            tag = values.get_latest_CVs_version()
        file_loc = (
            f"https://raw.githubusercontent.com/ncasuk/AMF_CVs/{tag}"
            "/product-definitions/tsv"
        )
    return f"{file_loc}/{product}/dimensions-specific.tsv"


def create_attributes_tsv_url(product, use_local_files=None, tag="latest"):
    """
    Returns URL for tsv file of global attributes specific to a given product and tag
    release or branch.

    Args:
        product (str): data product
        use_local_files (str or None): path to local directory where tsv files are
                                    stored. If "None", read from online. Default None.
        tag (str): tagged release of definitions, or 'latest' to get most recent
                release. Ignored if use_local_files is not None. Default "latest".

    Return:
        URL
    """
    if use_local_files:
        file_loc = use_local_files
    else:
        if tag == "latest":
            tag = values.get_latest_CVs_version()
        file_loc = (
            f"https://raw.githubusercontent.com/ncasuk/AMF_CVs/{tag}"
            "/product-definitions/tsv"
        )
    return f"{file_loc}/{product}/global-attributes-specific.tsv"


def instrument_dict(desired_instrument, loc="land", use_local_files=None, tag="latest"):
    """
    Collect all variables, dimensions and attributes required for all data products
    associated with an instrument and deployment mode.

    Args:
        desired_instrument (str): name of instrument
        loc (str): deployment mode, one of 'land', 'sea', 'air',
                   or 'trajectory'. Default 'land'.
        use_local_files (str or None): path to local directory where tsv files are
                                    stored. If "None", read from online. Default None.
        tag (str): tagged release of definitions, or 'latest' to get most recent
                release. Ignored if use_local_files is not None. Default "latest".

    Returns:
        dictionary of all attributes, dimensions and variables
        associated with the named instrument.
    """
    common_dimensions_url = values.get_common_dimensions_url(
        use_local_files=use_local_files, tag=tag, loc=loc
    )
    common_variables_url = values.get_common_variables_url(
        use_local_files=use_local_files, tag=tag, loc=loc
    )

    instrument_dict = {}
    main_instruments = tsv2dict_instruments(
        values.get_instruments_url(use_local_files=use_local_files, tag=tag)
    )
    if desired_instrument in main_instruments.keys():
        instrument_dict["info"] = main_instruments[desired_instrument]
    else:
        instrument_dict["info"] = tsv2dict_instruments(
            values.get_community_instruments_url(
                use_local_files=use_local_files, tag=tag
            )
        )[desired_instrument]

    # Add common stuff
    instrument_dict["common"] = {}
    instrument_dict["common"]["attributes"] = {}
    instrument_dict["common"]["dimensions"] = {}
    instrument_dict["common"]["variables"] = {}

    instrument_dict["common"]["attributes"] = tsv2dict_attrs(
        values.get_common_attributes_url(use_local_files=use_local_files, tag=tag)
    )
    instrument_dict["common"]["dimensions"] = tsv2dict_dims(common_dimensions_url)
    instrument_dict["common"]["variables"] = tsv2dict_vars(common_variables_url)

    # Add stuff for each product of instrument it specifics exist
    for product in instrument_dict["info"]["Data Product(s)"]:
        instrument_dict[product] = {}
        instrument_dict[product]["attributes"] = {}
        instrument_dict[product]["dimensions"] = {}
        instrument_dict[product]["variables"] = {}

        attr_url = create_attributes_tsv_url(
            product, use_local_files=use_local_files, tag=tag
        )
        dim_url = create_dimensions_tsv_url(
            product, use_local_files=use_local_files, tag=tag
        )
        var_url = create_variables_tsv_url(
            product, use_local_files=use_local_files, tag=tag
        )

        if (use_local_files and os.path.isfile(attr_url)) or (
            not use_local_files and requests.get(attr_url).status_code == 200
        ):
            instrument_dict[product]["attributes"] = tsv2dict_attrs(attr_url)

        if (use_local_files and os.path.isfile(dim_url)) or (
            not use_local_files and requests.get(dim_url).status_code == 200
        ):
            instrument_dict[product]["dimensions"] = tsv2dict_dims(dim_url)

        if (use_local_files and os.path.isfile(var_url)) or (
            not use_local_files and requests.get(var_url).status_code == 200
        ):
            instrument_dict[product]["variables"] = tsv2dict_vars(var_url)

    return instrument_dict


def product_dict(
    desired_product,
    instrument_loc="",
    deployment_loc="land",
    use_local_files=None,
    tag="latest",
):
    """
    Collect all variables, dimensions and attributes required for a data products
    and deployment mode.

    Args:
        desired_product (str): name of data product
        instrument_loc (str): location or observatory of instrument
        deployment_loc (str): deployment mode, one of 'land', 'sea', 'air',
                              or 'trajectory'. Default 'land'.
        use_local_files (str or None): path to local directory where tsv files are
                                    stored. If "None", read from online. Default None.
        tag (str): tagged release of definitions, or 'latest' to get most recent
                release. Ignored if use_local_files is not None. Default "latest".

    Returns:
        dictionary of all attributes, dimensions and variables
        associated with the named data product.
    """
    common_dimensions_url = values.get_common_dimensions_url(
        use_local_files=use_local_files, tag=tag, loc=deployment_loc
    )
    common_variables_url = values.get_common_variables_url(
        use_local_files=use_local_files, tag=tag, loc=deployment_loc
    )

    product_dict = {}

    # Add common stuff
    product_dict["common"] = {}
    product_dict["common"]["attributes"] = {}
    product_dict["common"]["dimensions"] = {}
    product_dict["common"]["variables"] = {}

    product_dict["common"]["attributes"] = tsv2dict_attrs(
        values.get_common_attributes_url(use_local_files=use_local_files, tag=tag)
    )
    product_dict["common"]["dimensions"] = tsv2dict_dims(common_dimensions_url)
    product_dict["common"]["variables"] = tsv2dict_vars(common_variables_url)

    # Add stuff for each product of instrument it specifics exist
    product_dict[desired_product] = {}
    product_dict[desired_product]["attributes"] = {}
    product_dict[desired_product]["dimensions"] = {}
    product_dict[desired_product]["variables"] = {}

    attr_url = create_attributes_tsv_url(
        desired_product, use_local_files=use_local_files, tag=tag
    )
    dim_url = create_dimensions_tsv_url(
        desired_product, use_local_files=use_local_files, tag=tag
    )
    var_url = create_variables_tsv_url(
        desired_product, use_local_files=use_local_files, tag=tag
    )

    request = requests.get(attr_url)
    if request.status_code == 200 or use_local_files:
        product_dict[desired_product]["attributes"] = tsv2dict_attrs(attr_url)

    request = requests.get(dim_url)
    if request.status_code == 200 or use_local_files:
        product_dict[desired_product]["dimensions"] = tsv2dict_dims(dim_url)

    request = requests.get(var_url)
    if request.status_code == 200 or use_local_files:
        product_dict[desired_product]["variables"] = tsv2dict_vars(var_url)

    # Add basic info bits
    product_dict["info"] = {}
    product_dict["info"]["Mobile/Fixed (loc)"] = instrument_loc
    product_dict["info"]["Manufacturer"] = (
        "CHANGE: Manufacturer of instrument and key sub components."
        " String: min 2 characters."
    )
    product_dict["info"]["Model No."] = (
        "CHANGE: Model number of instrument and key sub components."
        " String: min 3 characters"
    )
    product_dict["info"]["Serial Number"] = (
        "CHANGE: Serial number of instrument and key sub components."
        " String: min 3 characters."
    )
    product_dict["info"]["Descriptor"] = "CHANGE: Descripton of instrument."

    return product_dict


def list_all_products(use_local_files=None, tag="latest"):
    """
    Return list of all available data products.

    Args:
        use_local_files (str or None): path to local directory where tsv files are
                                    stored. If "None", read from online. Default None.
        tag (str): tagged release of definitions, or 'latest' to get most recent
                release. Ignored if use_local_files is not None. Default "latest".
    """
    data_products_url = values.get_all_data_products_url(
        use_local_files=use_local_files, tag=tag
    )
    df_data_products = pd.read_csv(data_products_url, sep="\t")
    return list(df_data_products["Data Product"])


if __name__ == "__main__":
    import sys

    desired_instrument = sys.argv[1]
    instrument = instrument_dict(desired_instrument)
    """
    This bit just makes the print look pretty, a standard print would also work
    """
    import pprint

    pp = pprint.PrettyPrinter(indent=2, width=200)
    pp.pprint(instrument)
