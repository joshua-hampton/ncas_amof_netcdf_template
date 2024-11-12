"""
Get various URLs from AMF_CVs GitHub repo for vocab releases.

"""

import requests
from typing import Optional


def get_latest_CVs_version() -> str:
    """
    Get latest release version of AMF_CVs

    Returns:
        string of latest tagged version release
    """
    return requests.get("https://github.com/ncasuk/AMF_CVs/releases/latest").url.split(
        "/"
    )[-1]


def get_latest_instrument_CVs_version() -> str:
    """
    Get latest release version of ncas-data-instrument-vocabs

    Returns:
        string of latest tagged version release
    """
    return requests.get(
        "https://github.com/ncasuk/ncas-data-instrument-vocabs/releases/latest"
    ).url.split("/")[-1]


def get_common_attributes_url(
    use_local_files: Optional[str] = None, tag: str = "latest"
) -> str:
    """
    Return URL to TSV file of common global attributes.

    Args:
        use_local_files (str or None): path to local directory where tsv files are
                                    stored. If "None", read from online. Default None.
        tag (str): tagged release of definitions, or 'latest' to get most recent
                release. Ignored if use_local_files is not None. Default "latest".

    Returns:
        URL string
    """
    if use_local_files:
        file_loc = use_local_files
    else:
        if tag == "latest":
            tag = get_latest_CVs_version()
        file_loc = (
            f"https://raw.githubusercontent.com/ncasuk/AMF_CVs/{tag}"
            "/product-definitions/tsv"
        )
    return f"{file_loc}/_common/global-attributes.tsv"


def get_common_variables_url(
    loc: str = "land", use_local_files: Optional[str] = None, tag: str = "latest"
) -> str:
    """
    Return URL to TSV file of common variables.

    Args:
        loc (str): deployment mode of instrument - one of
                   'land', 'sea', 'air', or 'trajectory'
        use_local_files (str or None): path to local directory where tsv files are
                                    stored. If "None", read from online. Default None.
        tag (str): tagged release of definitions, or 'latest' to get most recent
                release. Ignored if use_local_files is not None. Default "latest".

    Returns:
        URL string
    """
    if loc not in ["land", "sea", "air", "trajectory"]:
        raise ValueError(
            f"Invalid location {loc} - should be one of "
            "'land', 'sea', 'air', 'trajectory'."
        )
    if use_local_files:
        file_loc = use_local_files
    else:
        if tag == "latest":
            tag = get_latest_CVs_version()
        file_loc = (
            f"https://raw.githubusercontent.com/ncasuk/AMF_CVs/{tag}"
            "/product-definitions/tsv"
        )
    return f"{file_loc}/_common/variables-{loc}.tsv"


def get_common_dimensions_url(
    loc: str = "land", use_local_files: Optional[str] = None, tag: str = "latest"
) -> str:
    """
    Return URL to TSV file of common dimensions.

    Args:
        loc (str): deployment mode of instrument -
                   one of 'land', 'sea', 'air', or 'trajectory'
        use_local_files (str or None): path to local directory where tsv files are
                                    stored. If "None", read from online. Default None.
        tag (str): tagged release of definitions, or 'latest' to get most recent
                release. Ignored if use_local_files is not None. Default "latest".

    Returns:
        URL string
    """
    if loc not in ["land", "sea", "air", "trajectory"]:
        raise ValueError(
            f"Invalid location {loc} - should be one of "
            "'land', 'sea', 'air', 'trajectory'."
        )
    if use_local_files:
        file_loc = use_local_files
    else:
        if tag == "latest":
            tag = get_latest_CVs_version()
        file_loc = (
            f"https://raw.githubusercontent.com/ncasuk/AMF_CVs/{tag}"
            "/product-definitions/tsv"
        )
    return f"{file_loc}/_common/dimensions-{loc}.tsv"


def get_instruments_url(
    use_local_files: Optional[str] = None, tag: str = "latest"
) -> str:
    """
    Return URL to TSV file of AMOF instruments.

    Args:
        use_local_files (str or None): path to local directory where tsv files are
                                    stored. If "None", read from online. Default None.
        tag (str): tagged release of definitions, or 'latest' to get most recent
                release. Ignored if use_local_files is not None. Default "latest".

    Returns:
        URL string
    """
    if use_local_files:
        file_loc = use_local_files
    else:
        if tag == "latest":
            tag = get_latest_instrument_CVs_version()
        file_loc = (
            f"https://raw.githubusercontent.com/ncasuk/ncas-data-instrument-vocabs/{tag}"
            "/product-definitions/tsv"
        )
    return f"{file_loc}/_instrument_vocabs/ncas-instrument-name-and-descriptors.tsv"


def get_community_instruments_url(
    use_local_files: Optional[str] = None, tag: str = "latest"
) -> str:
    """
    Return URL to TSV file of community instruments.

    Args:
        use_local_files (str or None): path to local directory where tsv files are
                                    stored. If "None", read from online. Default None.
        tag (str): tagged release of definitions, or 'latest' to get most recent
                release. Ignored if use_local_files is not None. Default "latest".

    Returns:
        URL string
    """
    if use_local_files:
        file_loc = use_local_files
    else:
        if tag == "latest":
            tag = get_latest_instrument_CVs_version()
        file_loc = (
            f"https://raw.githubusercontent.com/ncasuk/ncas-data-instrument-vocabs/{tag}"
            "/product-definitions/tsv"
        )
    return (
        f"{file_loc}/_instrument_vocabs/community-instrument-name-and-descriptors.tsv"
    )


def get_all_data_products_url(
    use_local_files: Optional[str] = None, tag: str = "latest"
) -> str:
    """
    Return URL to TSV file of data products.

    Args:
        use_local_files (str or None): path to local directory where tsv files are
                                    stored. If "None", read from online. Default None.
        tag (str): tagged release of definitions, or 'latest' to get most recent
                release. Ignored if use_local_files is not None. Default "latest".

    Returns:
        URL string
    """
    if use_local_files:
        file_loc = use_local_files
    else:
        if tag == "latest":
            tag = get_latest_CVs_version()
        file_loc = (
            f"https://raw.githubusercontent.com/ncasuk/AMF_CVs/{tag}"
            "/product-definitions/tsv"
        )
    return f"{file_loc}/_vocabularies/data-products.tsv"
