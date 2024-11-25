"""
Take tsv files a return a class with all the data needed for creating the netCDF files.
"""

import requests
import pandas as pd
import re
from typing import Optional, Union

from .util import check_int


class FileInfo:
    """
    Class that will gather and hold all the data to create netCDF file with

    Args:
        instrument_name (str): name of the instrument
        data_product (str): name of data product to use
        deployment_mode (str): value of the 'deployment_mode' global attribute, and
                               different variables may be required depending on
                               value. One of "land", "sea", "air", or "trajectory".
                               Default is "land".
        tag (str): tagged release version of AMF_CVs, or "latest" to get most
                   recent version. Default is "latest".
        use_local_files (str or None): path to local directory where tsv files are
                                       stored. If "None", read from online. If not
                                       "None", "tag" must be specified. Default
                                       None.
    """

    def __init__(
        self,
        instrument_name: str,
        data_product: str,
        deployment_mode: str = "land",
        tag: str = "latest",
        use_local_files: Optional[str] = None,
    ) -> None:
        """
        Initialise the class.

        Args:
            instrument_name (str): name of the instrument
            data_product (str): name of data product to use
            deployment_mode (str): value of the 'deployment_mode' global attribute, and
                                   different variables may be required depending on
                                   value. One of "land", "sea", "air", or "trajectory".
            tag (str): tagged release version of AMF_CVs, or "latest" to get most
                       recent version. Default is "latest".
            use_local_files (str or None): path to local directory where tsv files are
                                           stored. If "None", read from online. If not
                                           "None", "tag" must be specified. Default
                                           None.
        """
        if deployment_mode not in ["land", "sea", "air", "trajectory"]:
            msg = f"Invalid deployment mode {deployment_mode}, must be one of 'land', 'sea', 'air', 'trajectory'."
            raise ValueError(msg)

        if use_local_files is not None and tag == "latest":
            msg = "Incompatible options - if 'use_local_files' is given, 'tag' version must be specified."
            raise ValueError(msg)

        self.instrument_name = instrument_name
        self.data_product = data_product
        self.deployment_mode = deployment_mode
        self.use_local_files = use_local_files
        self.tag = tag
        if self.use_local_files is not None:
            self.ncas_gen_version = tag
        else:
            if self.tag == "latest":
                self.ncas_gen_version = self._get_github_latest_version(
                    "https://github.com/ncasuk/AMF_CVs"
                )
            elif self._check_github_cvs_version_exists(release_tag=tag):
                self.ncas_gen_version = tag
            else:
                msg = f"Cannot find release version {tag} in https://github.com/ncasuk/AMF_CVs"
                raise ValueError(msg)
        self.attributes = {}
        self.dimensions = {}
        self.variables = {}
        self.instrument_data = {}

    def __repr__(self) -> str:
        class_name = type(self).__name__
        return f"{class_name}(instrument_name='{self.instrument_name}', data_product='{self.data_product}', deployment_mode='{self.deployment_mode}', tag='{self.tag}', use_local_files='{self.use_local_files}') - ncas_gen_version = '{self.ncas_gen_version}"

    def __str__(self) -> str:
        return f"Class with information for '{self.instrument_name}' instrument and '{self.data_product}' data product"

    def get_common_info(self) -> None:
        """
        Get all the common variables, dimensions and attributes, and add to class
        properties
        """
        self._tsv2dict_attrs(self._attributes_tsv_url(self.deployment_mode))

    def get_deployment_info(self) -> None:
        """
        Get all the variables, dimensions and attributes related to the deployment
        mode, and add to class properties
        """
        self._tsv2dict_dims(self._dimensions_tsv_url(self.deployment_mode))
        self._tsv2dict_vars(self._variables_tsv_url(self.deployment_mode))

    def get_product_info(self) -> None:
        """
        Get all the variables, dimensions and attributes related to the data product,
        and add to class properties
        """
        self._tsv2dict_attrs(self._attributes_tsv_url(self.data_product))
        self._tsv2dict_dims(self._dimensions_tsv_url(self.data_product))
        self._tsv2dict_vars(self._variables_tsv_url(self.data_product))

    def get_instrument_info(self) -> None:
        """
        Get all the attribute data related to a defined instrument in the
        ncas-data-instrument-vocabs repo, and add to class property.
        """
        if self.instrument_name.startswith("ncas-"):
            self._tsv2dict_instruments(self._get_ncas_instrument_tsv_url())
        else:
            self._tsv2dict_instruments(self._get_community_instrument_tsv_url())

    def _tsv2dict_vars(self, tsv_file: str) -> None:
        """
        For a given tsv file from the AMF_CVs GitHub repo, add dictionary of
        variables and their attributes to variables property.

        Args:
            tsv_file (str): URL to location of tsv file
        """
        if self._check_website_exists(tsv_file):
            df_vars = pd.read_csv(tsv_file, sep="\t")
            df_vars = df_vars.fillna("")

            current_var_dict = {}
            first_loop = True
            current_var = ""

            for current_line in df_vars.iloc:
                if current_line["Variable"] != "":
                    if not first_loop:
                        self.variables[current_var] = current_var_dict
                    else:
                        first_loop = False
                    current_var = current_line["Variable"]
                    current_var_dict = {}
                if current_line["Attribute"] != "":
                    if (
                        current_line["Value"] == ""
                        and "example value" in current_line.keys()
                        and current_line["example value"] != ""
                    ):
                        current_var_dict[current_line["Attribute"]] = (
                            f"EXAMPLE: {current_line['example value']}"
                        )
                    else:
                        current_var_dict[current_line["Attribute"]] = current_line[
                            "Value"
                        ]

            self.variables[current_var] = current_var_dict

    def _tsv2dict_dims(self, tsv_file: str) -> None:
        """
        For a given tsv file from the AMF_CVs GitHub repo, add dictionary of dimensions
        and additional info to dimensions property.

        Args:
            tsv_file (str): URL to location of tsv file
        """
        if self._check_website_exists(tsv_file):
            df_dims = pd.read_csv(tsv_file, sep="\t")
            df_dims = df_dims.fillna("")

            for dim in df_dims.iloc:
                dim_dict = dim.to_dict()
                dim_name = dim_dict.pop("Name")
                if check_int(dim_dict["Length"]):
                    dim_dict["Length"] = int(dim_dict["Length"])
                self.dimensions[dim_name] = dim_dict

    def _tsv2dict_attrs(self, tsv_file: str) -> None:
        """
        For a given tsv file from the AMF_CVs GitHub repo, add dictionary of attributes
        and values to attribute property.

        Args:
            tsv_file (str): URL to location of tsv file
        """
        if self._check_website_exists(tsv_file):
            df_attrs = pd.read_csv(tsv_file, sep="\t")
            df_attrs = df_attrs.fillna("")

            for attr in df_attrs.iloc:
                attr_dict = attr.to_dict()
                attr_name = attr_dict.pop("Name")
                self.attributes[attr_name] = attr_dict

    def _tsv2dict_instruments(self, tsv_file: str) -> None:
        """
        For a given tsv file from the ncas-data-instrument-vocabs repo, add dictionary
        of instrument data to atttributes property.

        Args:
            tsv_file (str): URL to location of tsv file
        """
        if self._check_website_exists(tsv_file):
            df_instruments = pd.read_csv(tsv_file, sep="\t")
            df_instrument = df_instruments.where(
                df_instruments["New Instrument Name"] == self.instrument_name
            ).dropna(subset=["New Instrument Name"])
            if len(df_instrument) == 0:
                print(
                    f"[WARNING] No details found for instrument {self.instrument_name}..."
                )
            else:
                for inst in df_instrument.iloc:
                    instrument_dict = inst.to_dict()
                    data_products = re.split(
                        r",| |\|", instrument_dict["Data Product(s)"]
                    )
                    data_products = list(filter(None, data_products))
                    instrument_dict["Data Product(s)"] = data_products
                    for i in [
                        "Manufacturer",
                        "Model No.",
                        "Serial Number",
                        "Data Product(s)",
                        "Mobile/Fixed (loc)",
                        "Descriptor",
                    ]:
                        self.instrument_data[i] = instrument_dict[i]

    def _check_instrument_has_product(self) -> bool:
        """
        Check instrument has defined data product associated with it

        Returns:
            bool: does the instrument have the given data product associated with it
        """
        if "Data Product(s)" not in self.instrument_data.keys():
            self.get_instrument_info()
        return self.data_product in self.instrument_data["Data Product(s)"]

    def _get_github_latest_version(self, url: str) -> str:
        """
        Get the tag of the latest release version

        Args:
            url (str): GitHub URL to find latest release version of: https://github.com/<owner-name>/<repo-name>

        Returns:
            str: tag name of latest version release
        """
        return requests.get(f"{url}/releases/latest").url.split("/")[-1]

    def _check_website_exists(self, url: str) -> bool:
        """
        Check website exists and is up

        Args:
            url (str): URL to check

        Returns:
            bool: website is reachable
        """
        status = requests.get(url).status_code
        return status == 200

    def _check_github_cvs_version_exists(
        self, release_tag: Optional[str] = None
    ) -> bool:
        """
        Check the requested tagged version of AMF_CVs exists on GitHub
        """
        if release_tag is None:
            release_tag = self.ncas_gen_version
        url = f"https://github.com/ncasuk/AMF_CVs/releases/{release_tag}"
        return self._check_website_exists(url)

    def _dimensions_tsv_url(self, obj: str) -> str:
        """
        Get the URL for the tsv files for dimensions

        Args:
            obj (str): Data product or deployment mode

        Returns:
            str: URL location of dimension tsv file
        """
        if self.use_local_files is not None:
            main_loc = self.use_local_files
        else:
            main_loc = "https://raw.githubusercontent.com/ncasuk/AMF_CVs"
        file_loc = f"{main_loc}/{self.ncas_gen_version}/product-definitions/tsv"
        path, option = (
            (obj, "specific")
            if obj not in ["land", "sea", "air", "trajectory"]
            else ("_common", obj)
        )
        return f"{file_loc}/{path}/dimensions-{option}.tsv"

    def _variables_tsv_url(self, obj: str) -> str:
        """
        Get the URL for the tsv files for variables

        Args:
            obj (str): Data product or deployment mode

        Returns:
            str: URL location of variable tsv file
        """
        if self.use_local_files is not None:
            main_loc = self.use_local_files
        else:
            main_loc = "https://raw.githubusercontent.com/ncasuk/AMF_CVs"
        file_loc = f"{main_loc}/{self.ncas_gen_version}/product-definitions/tsv"
        path, option = (
            (obj, "specific")
            if obj not in ["land", "sea", "air", "trajectory"]
            else ("_common", obj)
        )
        return f"{file_loc}/{path}/variables-{option}.tsv"

    def _attributes_tsv_url(self, obj: str) -> str:
        """
        Get the URL for the tsv files for attributes

        Args:
            obj (str): Data product or deployment mode

        Returns:
            str: URL location of attribute tsv file
        """
        if self.use_local_files is not None:
            main_loc = self.use_local_files
        else:
            main_loc = "https://raw.githubusercontent.com/ncasuk/AMF_CVs"
        file_loc = f"{main_loc}/{self.ncas_gen_version}/product-definitions/tsv"
        path, option = (
            (obj, "-specific")
            if obj not in ["land", "sea", "air", "trajectory"]
            else ("_common", "")
        )
        return f"{file_loc}/{path}/global-attributes{option}.tsv"

    def _get_ncas_instrument_tsv_url(self) -> str:
        """
        Get the URL for the tsv file of NCAS instruments
        """
        if self.use_local_files is not None:
            main_loc = f"{self.use_local_files}/{self.tag}"
        else:
            vocab_version = self._get_github_latest_version(
                "https://github.com/ncasuk/ncas-data-instrument-vocabs"
            )
            file_loc = (
                "https://raw.githubusercontent.com/ncasuk/ncas-data-instrument-vocabs"
            )
            main_loc = f"{file_loc}/{vocab_version}"
        return f"{main_loc}/product-definitions/tsv/_instrument_vocabs/ncas-instrument-name-and-descriptors.tsv"

    def _get_community_instrument_tsv_url(self) -> str:
        """
        Get the URL for the tsv file of NCAS instruments
        """
        if self.use_local_files is not None:
            main_loc = f"{self.use_local_files}/{self.tag}"
        else:
            vocab_version = self._get_github_latest_version(
                "https://github.com/ncasuk/ncas-data-instrument-vocabs"
            )
            file_loc = (
                "https://raw.githubusercontent.com/ncasuk/ncas-data-instrument-vocabs"
            )
            main_loc = f"{file_loc}/{vocab_version}"
        return f"{main_loc}/product-definitions/tsv/_instrument_vocabs/community-instrument-name-and-descriptors.tsv"


def convert_instrument_dict_to_file_info(
    instrument_dict: dict[
        str, dict[str, Union[str, list[str], dict[str, dict[str, Union[str, float]]]]]
    ],
    instrument_name: str,
    data_product: str,
    deployment_mode: str,
    tag: str,
) -> FileInfo:
    """
    Convert instrument_dict from tsv2dict.instrument_dict to a FileInfo class variable

    Args:
        instrument_dict (dict): Dictionary made by tsv2dict.instrument_dict
        instrument_name (str): Name of the instrument
        data_product (str): Data product of data for netCDF file
        deployment_mode (str): Deployment mode of instrument. One of "land", "sea",
                               "air", "trajectory"
        tag (str): Tag release of AMF_CVs being used

    Returns:
        FileInfo object with all instrument data from the dictionary
    """
    instrument_file_info = FileInfo(instrument_name, data_product, deployment_mode, tag)
    for prod in ["common", data_product]:
        if "attributes" in instrument_dict[prod].keys():
            for attr_name, attr_dict in instrument_dict[prod]["attributes"].items():
                instrument_file_info.attributes[attr_name] = attr_dict
        if "dimensions" in instrument_dict[prod].keys():
            for dim_name, dim_dict in instrument_dict[prod]["dimensions"].items():
                instrument_file_info.dimensions[dim_name] = dim_dict
        if "variables" in instrument_dict[prod].keys():
            for var_name, var_dict in instrument_dict[prod]["variables"].items():
                instrument_file_info.variables[var_name] = var_dict
    if "info" in instrument_dict.keys():
        for key, value in instrument_dict["info"].items():
            if (
                key == "Mobile/Fixed (loc)"
                and value.split("-")[0].strip().lower() == "fixed"
            ):
                value = value.split("-")[1].strip()
            instrument_file_info.instrument_data[key] = value

    return instrument_file_info
