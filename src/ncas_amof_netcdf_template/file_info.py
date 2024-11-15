"""
Take tsv files a return a class with all the data needed for creating the netCDF files.
"""

import requests
import pandas as pd
import re


class FileInfo:
    """
    Class that will gather and hold all the data to create netCDF file with
    """
    def __init__(
        self,
        instrument_name: str,
        data_product: str,
        deployment_mode: str = "land",
        tag: str = "latest",
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
        """
        if deployment_mode not in ["land", "sea", "air", "trajectory"]:
            msg = f"Invalid deployment mode {deployment_mode}, must be one of 'land', 'sea', 'air', 'trajectory'."
            raise ValueError(msg)

        self.instrument_name = instrument_name
        self.data_product = data_product
        self.deployment_mode = deployment_mode
        self.tag = tag
        if self.tag == "latest":
            self.ncas_gen_version = self._get_github_latest_version("https://github.com/ncasuk/AMF_CVs")
        elif self._check_github_cvs_version_exists():
            self.ncas_gen_version = tag
        else:
            msg = f"Cannot find release version {tag} in https://github.com/ncasuk/AMF_CVs"
            raise ValueError(msg)
        self.attributes = {}
        self.dimensions = {}
        self.variables = {}


    def __repr__(self) -> str:
        class_name = type(self).__name__
        return f"{class_name}(instrument_name='{self.instrument_name}', data_product='{self.data_product}', deployment_mode='{self.deployment_mode}', tag='{self.tag}') - ncas_gen_version = '{self.ncas_gen_version}"


    def __str__(self) -> str:
        return f"Class with information for {self.instrument_name} instrument and {self.data_product} product"



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
                        current_var_dict[current_line["Attribute"]] = current_line["Value"]

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
            df_instrument = df_instruments.where(df_instruments["New Instrument Name"] == self.instrument_name).dropna(subset=["New Instrument Name"])
            if len(df_instrument) == 0:
                print(f"[WARNING] No details found for instrument {self.instrument_name}...")
            else:
                for inst in df_instrument.iloc:
                    instrument_dict = inst.to_dict()
                    data_products = re.split(r",| |\|", instrument_dict["Data Product(s)"])
                    data_products = list(filter(None, data_products))
                    instrument_dict["Data Product(s)"] = data_products

                    for i in ["Manufacturer", "Model No.", "Serial Number", "Data Product(s)", "Mobile/Fixed (loc)", "Descriptor"]:
                        self.attributes[i] = {"Fixed Value": instrument_dict[i]}


    def _check_instrument_has_product(self, product: str) -> bool:
        """
        Check instrument has defined data product associated with it

        Args:
            product (str): data product to check

        Returns:
            bool: does the instrument have the given data product associated with it
        """
        if "Data Product(s)" not in self.attributes.keys():
            if self.instrument_name.startswith("ncas"):
                inst_tsv = self._get_ncas_instrument_tsv_url()
            else:
                inst_tsv = self._get_community_instrument_tsv_url()
            self._tsv2dict_instruments(inst_tsv)
        return product in self.attributes["Data Product(s)"]


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


    def _check_github_cvs_version_exists(self) -> bool:
        """
        Check the requested tagged version of AMF_CVs exists on GitHub
        """
        url = f"https://github.com/ncasuk/AMF_CVs/releases/{self.ncas_gen_version}"
        return self._check_website_exists(url)
        

    def _dimensions_tsv_url(self, obj: str) -> str:
        """
        Get the URL for the tsv files for dimensions

        Args:
            obj (str): Data product or deployment mode

        Returns:
            str: URL location of dimension tsv file
        """
        file_loc = f"https://raw.githubusercontent.com/ncasuk/AMF_CVs/{self.ncas_gen_version}/product-definitions/tsv"
        path, option = (obj, "specific") if obj not in ["land", "sea", "air", "trajectory"] else ("_common", obj)
        return f"{file_loc}/{path}/dimensions-{option}.tsv"


    def _variables_tsv_url(self, obj: str) -> str:
        """
        Get the URL for the tsv files for variables

        Args:
            obj (str): Data product or deployment mode

        Returns:
            str: URL location of variable tsv file
        """
        file_loc = f"https://raw.githubusercontent.com/ncasuk/AMF_CVs/{self.ncas_gen_version}/product-definitions/tsv"
        path, option = (obj, "specific") if obj not in ["land", "sea", "air", "trajectory"] else ("_common", obj)
        return f"{file_loc}/{path}/variables-{option}.tsv"


    def _attributes_tsv_url(self, obj: str) -> str:
        """
        Get the URL for the tsv files for attributes

        Args:
            obj (str): Data product or deployment mode

        Returns:
            str: URL location of attribute tsv file
        """
        file_loc = f"https://raw.githubusercontent.com/ncasuk/AMF_CVs/{self.ncas_gen_version}/product-definitions/tsv"
        path, option = (obj, "-specific") if obj not in ["land", "sea", "air", "trajectory"] else ("_common", "")
        return f"{file_loc}/{path}/global-attributes{option}.tsv"

    
    def _get_ncas_instrument_tsv_url(self) -> str:
        """
        Get the URL for the tsv file of NCAS instruments
        """
        vocab_version = self._get_github_latest_version("https://github.com/ncasuk/ncas-data-instrument-vocabs")
        file_loc = f"https://raw.githubusercontent.com/ncasuk/ncas-data-instrument-vocabs"
        return f"{file_loc}/{vocab_version}/product-definitions/tsv/_instrument_vocabs/ncas-instrument-name-and-descriptors.tsv"

    
    def _get_community_instrument_tsv_url(self) -> str:
        """
        Get the URL for the tsv file of NCAS instruments
        """
        vocab_version = self._get_github_latest_version("https://github.com/ncasuk/ncas-data-instrument-vocabs")
        file_loc = f"https://raw.githubusercontent.com/ncasuk/ncas-data-instrument-vocabs"
        return f"{file_loc}/{vocab_version}/product-definitions/tsv/_instrument_vocabs/community-instrument-name-and-descriptors.tsv"

        


