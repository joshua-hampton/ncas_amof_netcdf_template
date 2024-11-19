import pytest
import requests
import tempfile
import os
import pandas as pd
from ncas_amof_netcdf_template import tsv2dict


@pytest.mark.parametrize(
    "product", ["mean-winds", "aerosol-optical-depth", "o2n2-concentration-ratio"]
)
def test_links_exist(product):
    url = tsv2dict.create_variables_tsv_url(product)
    request = requests.get(url)
    assert request.status_code == 200


def test_tsv2dict_vars():
    # Create a temporary TSV file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".tsv") as tmp:
        tmp_path = tmp.name
        tmp.write(b"Variable\tAttribute\tValue\texample value\n")
        tmp.write(b"var1\tattr1\tvalue1\t\n")
        tmp.write(b"\tattr2\t\texample1\n")
        tmp.write(b"var2\tattr1\tvalue2\t\n")
        tmp.write(b"\tattr2\t\texample2\n")

    # Call the tsv2dict_vars function
    result = tsv2dict.tsv2dict_vars(tmp_path)

    # Check the result
    assert result == {
        "var1": {"attr1": "value1", "attr2": "EXAMPLE: example1"},
        "var2": {"attr1": "value2", "attr2": "EXAMPLE: example2"},
    }

    # Delete the temporary file
    os.remove(tmp_path)


def test_tsv2dict_vars_empty_file():
    # Create a temporary TSV file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".tsv") as tmp:
        tmp_path = tmp.name
        tmp.write(b"Variable\tAttribute\tValue\texample value\n")

    # Call the tsv2dict_attrs function
    result = tsv2dict.tsv2dict_vars(tmp_path)

    # Check the result
    assert result == {"": {}}

    # Delete the temporary file
    os.remove(tmp_path)


def test_tsv2dict_dims():
    # Create a temporary TSV file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".tsv") as tmp:
        tmp_path = tmp.name
        tmp.write(b"Name\tAttribute1\tAttribute2\n")
        tmp.write(b"dim1\tvalue1\tvalue2\n")
        tmp.write(b"dim2\tvalue3\tvalue4\n")

    # Call the tsv2dict_dims function
    result = tsv2dict.tsv2dict_dims(tmp_path)

    # Check the result
    assert result == {
        "dim1": {"Attribute1": "value1", "Attribute2": "value2"},
        "dim2": {"Attribute1": "value3", "Attribute2": "value4"},
    }

    # Delete the temporary file
    os.remove(tmp_path)


def test_tsv2dict_dims_empty_file():
    # Create a temporary TSV file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".tsv") as tmp:
        tmp_path = tmp.name
        tmp.write(b"Name\tAttribute1\tAttribute2\n")

    # Call the tsv2dict_attrs function
    result = tsv2dict.tsv2dict_dims(tmp_path)

    # Check the result
    assert result == {}

    # Delete the temporary file
    os.remove(tmp_path)


def test_tsv2dict_attrs():
    # Create a temporary TSV file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".tsv") as tmp:
        tmp_path = tmp.name
        tmp.write(b"Name\tAttribute1\tAttribute2\n")
        tmp.write(b"attr1\tvalue1\tvalue2\n")
        tmp.write(b"attr2\tvalue3\tvalue4\n")

    # Call the tsv2dict_attrs function
    result = tsv2dict.tsv2dict_attrs(tmp_path)

    # Check the result
    assert result == {
        "attr1": {"Attribute1": "value1", "Attribute2": "value2"},
        "attr2": {"Attribute1": "value3", "Attribute2": "value4"},
    }

    # Delete the temporary file
    os.remove(tmp_path)


def test_tsv2dict_attrs_empty_file():
    # Create a temporary TSV file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".tsv") as tmp:
        tmp_path = tmp.name
        tmp.write(b"Name\tAttribute1\tAttribute2\n")

    # Call the tsv2dict_attrs function
    result = tsv2dict.tsv2dict_attrs(tmp_path)

    # Check the result
    assert result == {}

    # Delete the temporary file
    os.remove(tmp_path)


def test_tsv2dict_instruments():
    # Create a temporary TSV file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".tsv") as tmp:
        tmp_path = tmp.name
        tmp.write(b"New Instrument Name\tData Product(s)\n")
        tmp.write(b"instrument1\tproduct1, product2\n")
        tmp.write(b"instrument2\tproduct3|product4\n")
        tmp.write(b"instrument3\tproduct5 product6\n")

    # Call the tsv2dict_instruments function
    result = tsv2dict.tsv2dict_instruments(tmp_path)

    # Check the result
    assert result == {
        "instrument1": {
            "Data Product(s)": ["product1", "product2"],
            "instrument_name": "instrument1",
        },
        "instrument2": {
            "Data Product(s)": ["product3", "product4"],
            "instrument_name": "instrument2",
        },
        "instrument3": {
            "Data Product(s)": ["product5", "product6"],
            "instrument_name": "instrument3",
        },
    }

    # Delete the temporary file
    os.remove(tmp_path)


def test_tsv2dict_instruments_empty_file():
    # Create a temporary TSV file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".tsv") as tmp:
        tmp_path = tmp.name
        tmp.write(b"New Instrument Name\tData Product(s)\n")

    # Call the tsv2dict_instruments function
    result = tsv2dict.tsv2dict_instruments(tmp_path)

    # Check the result
    assert result == {}

    # Delete the temporary file
    os.remove(tmp_path)


def test_create_variables_tsv_url_with_local_files():
    # Call the create_variables_tsv_url function with local files
    result = tsv2dict.create_variables_tsv_url(
        "product1", use_local_files="/local/path"
    )

    # Check the result
    assert result == "/local/path/product1/variables-specific.tsv"


def test_create_variables_tsv_url():
    # Call the create_variables_tsv_url function with a tag
    result = tsv2dict.create_variables_tsv_url("product1", tag="tag1")
    # Check the result
    assert (
        result
        == "https://raw.githubusercontent.com/ncasuk/AMF_CVs/tag1/product-definitions/tsv/product1/variables-specific.tsv"
    )

    # Call the create_variables_tsv_url function with "latest" tag
    result = tsv2dict.create_variables_tsv_url("product1")
    # Check result does not have "latest" where tag should be
    assert (
        result
        != "https://raw.githubusercontent.com/ncasuk/AMF_CVs/latest/product-definitions/tsv/product1/variables-specific.tsv"
    )


def test_create_dimensions_tsv_url_with_local_files():
    # Call the create_dimensions_tsv_url function with local files
    result = tsv2dict.create_dimensions_tsv_url(
        "product1", use_local_files="/local/path"
    )

    # Check the result
    assert result == "/local/path/product1/dimensions-specific.tsv"


def test_create_dimensions_tsv_url():
    # Call the create_dimensions_tsv_url function with a tag
    result = tsv2dict.create_dimensions_tsv_url("product1", tag="tag1")
    # Check the result
    assert (
        result
        == "https://raw.githubusercontent.com/ncasuk/AMF_CVs/tag1/product-definitions/tsv/product1/dimensions-specific.tsv"
    )

    # Call the create_dimensions_tsv_url function with the latest tag
    result = tsv2dict.create_dimensions_tsv_url("product1")
    # Check the result does not have "latest" where tag should be
    assert (
        result
        != "https://raw.githubusercontent.com/ncasuk/AMF_CVs/latest/product-definitions/tsv/product1/dimensions-specific.tsv"
    )


def test_create_attributes_tsv_url_with_local_files():
    # Call the create_attributes_tsv_url function with local files
    result = tsv2dict.create_attributes_tsv_url(
        "product1", use_local_files="/local/path"
    )

    # Check the result
    assert result == "/local/path/product1/global-attributes-specific.tsv"


def test_create_attributes_tsv_url():
    # Call the create_attributes_tsv_url function with a tag
    result = tsv2dict.create_attributes_tsv_url("product1", tag="tag1")
    # Check the result
    assert (
        result
        == "https://raw.githubusercontent.com/ncasuk/AMF_CVs/tag1/product-definitions/tsv/product1/global-attributes-specific.tsv"
    )

    # Call the create_attributes_tsv_url function with the latest tag
    result = tsv2dict.create_attributes_tsv_url("product1")
    # Check the result does not have "latest" where tag should be
    assert (
        result
        != "https://raw.githubusercontent.com/ncasuk/AMF_CVs/latest/product-definitions/tsv/product1/global-attributes-specific.tsv"
    )


def test_instrument_dict():
    # Mock the tsv2dict_instruments and tsv2dict_attrs functions to return specific dictionaries
    tsv2dict.tsv2dict_instruments = lambda url: {
        "instrument1": {"Data Product(s)": ["product1"]}
    }
    tsv2dict.tsv2dict_attrs = lambda url: {"attr1": "value1"}
    tsv2dict.tsv2dict_dims = lambda url: {"dim1": "value1"}
    tsv2dict.tsv2dict_vars = lambda url: {"var1": {"attr1": "value1"}}

    # Call the instrument_dict function with a tag
    result = tsv2dict.instrument_dict("instrument1")

    # Check the result
    assert result == {
        "info": {"Data Product(s)": ["product1"]},
        "common": {
            "attributes": {"attr1": "value1"},
            "dimensions": {"dim1": "value1"},
            "variables": {"var1": {"attr1": "value1"}},
        },
        "product1": {
            "attributes": {},
            "dimensions": {},
            "variables": {},
        },
    }


def test_product_dict_with_local_files():
    # Call the product_dict function with local files
    result = tsv2dict.product_dict(
        "product1",
        platform="loc1",
        deployment_loc="land",
        use_local_files="/local/path",
        tag="tag1",
    )

    # Check the result
    assert "common" in result
    assert "product1" in result
    assert "info" in result
    assert result["info"]["Mobile/Fixed (loc)"] == "loc1"

    # Make sure we get the same if still using deprecated "instrument_loc" argument instead of "platform"
    result = tsv2dict.product_dict(
        "product1",
        instrument_loc="loc1",
        deployment_loc="land",
        use_local_files="/local/path",
        tag="tag1",
    )

    # Check the result
    assert "common" in result
    assert "product1" in result
    assert "info" in result
    assert result["info"]["Mobile/Fixed (loc)"] == "loc1"


def test_product_dict():
    # Mock the get_common_dimensions_url, get_common_variables_url, get_common_attributes_url,
    # create_attributes_tsv_url, create_dimensions_tsv_url, and create_variables_tsv_url functions
    tsv2dict.values.get_common_dimensions_url = (
        lambda use_local_files, tag, loc: "common_dimensions_url"
    )
    tsv2dict.values.get_common_variables_url = (
        lambda use_local_files, tag, loc: "common_variables_url"
    )
    tsv2dict.values.get_common_attributes_url = (
        lambda use_local_files, tag: "common_attributes_url"
    )
    tsv2dict.create_attributes_tsv_url = (
        lambda desired_product, use_local_files, tag: "attributes_url"
    )
    tsv2dict.create_dimensions_tsv_url = (
        lambda desired_product, use_local_files, tag: "dimensions_url"
    )
    tsv2dict.create_variables_tsv_url = (
        lambda desired_product, use_local_files, tag: "variables_url"
    )

    # Call the product_dict function with the latest tag
    result = tsv2dict.product_dict(
        "product1",
        platform="loc1",
        deployment_loc="land",
        use_local_files="/local/path",
    )

    # Check the result
    assert "common" in result
    assert "product1" in result
    assert "info" in result
    assert result["info"]["Mobile/Fixed (loc)"] == "loc1"


def test_list_all_products():
    # Mock the get_all_data_products_url function to return a URL
    tsv2dict.values.get_all_data_products_url = (
        lambda use_local_files, tag: "https://example.com/data_products.tsv"
    )

    # Mock the pd.read_csv function to return a DataFrame
    pd.read_csv = lambda url, sep: pd.DataFrame(
        {"Data Product": ["product1", "product2", "product3"]}
    )

    # Call the list_all_products function with a tag
    result = tsv2dict.list_all_products(None, "tag1")

    # Check the result
    assert result == ["product1", "product2", "product3"]
