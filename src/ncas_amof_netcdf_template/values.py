"""
Get various URLs from AMF_CVs GitHub repo for vocab releases.

"""

import requests


def get_latest_CVs_version():
    """
    Get latest release version of AMF_CVs
    
    Returns:
        string of latest tagged version release
    """
    return requests.get('https://github.com/ncasuk/AMF_CVs/releases/latest').url.split('/')[-1]


def get_common_attributes_url(tag = 'latest'):
    """
    Return URL to TSV file of common global attributes.

    Args:
        tag (str): tagged release of definitions, or 'latest' to get most recent release

    Returns:
        URL string 
    """
    if tag == 'latest':
        tag = get_latest_CVs_version()
    return f'https://raw.githubusercontent.com/ncasuk/AMF_CVs/{tag}/product-definitions/tsv/_common/global-attributes.tsv'


def get_common_variables_url(loc = 'land', tag = 'latest'):
    """
    Return URL to TSV file of common variables.

    Args:
        loc (str): deployment mode of instrument - one of 'land', 'sea', 'air', or 'trajectory'
        tag (str): tagged release of definitions, or 'latest' to get most recent release

    Returns:
        URL string 
    """
    if tag == 'latest':
        tag = get_latest_CVs_version()
    if loc not in ['land','sea','air','trajectory']:
        raise ValueError(f"Invalid location {loc} - should be one of 'land', 'sea', 'air', 'trajectory'.")
    return f'https://raw.githubusercontent.com/ncasuk/AMF_CVs/{tag}/product-definitions/tsv/_common/variables-{loc}.tsv'



def get_common_dimensions_url(loc = 'land', tag = 'latest'):
    """
    Return URL to TSV file of common dimensions.

    Args:
        loc (str): deployment mode of instrument - one of 'land', 'sea', 'air', or 'trajectory'
        tag (str): tagged release of definitions, or 'latest' to get most recent release

    Returns:
        URL string 
    """
    if tag == 'latest':
        tag = get_latest_CVs_version()
    if loc not in ['land','sea','air','trajectory']:
        raise ValueError(f"Invalid location {loc} - should be one of 'land', 'sea', 'air', 'trajectory'.")
    return f'https://raw.githubusercontent.com/ncasuk/AMF_CVs/{tag}/product-definitions/tsv/_common/dimensions-{loc}.tsv'


def get_instruments_url(tag = 'latest'):
    """
    Return URL to TSV file of AMOF instruments.

    Args:
        tag (str): tagged release of definitions, or 'latest' to get most recent release

    Returns:
        URL string 
    """
    if tag == 'latest':
        tag = get_latest_CVs_version()
    return f'https://raw.githubusercontent.com/ncasuk/AMF_CVs/{tag}/product-definitions/tsv/_vocabularies/ncas-instrument-name-and-descriptors.tsv'


def get_community_instruments_url(tag = 'latest'):
    """
    Return URL to TSV file of community instruments.

    Args:
        tag (str): tagged release of definitions, or 'latest' to get most recent release

    Returns:
        URL string 
    """
    if tag == 'latest':
        tag = get_latest_CVs_version()
    return f'https://raw.githubusercontent.com/ncasuk/AMF_CVs/{tag}/product-definitions/tsv/_vocabularies/community-instrument-name-and-descriptors.tsv'
