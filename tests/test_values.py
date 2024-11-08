import pytest
import requests_mock
from ncas_amof_netcdf_template import values


def test_get_latest_CVs_version():
    with requests_mock.Mocker() as m:
        m.get(
            "https://github.com/ncasuk/AMF_CVs/releases/latest",
            status_code=302,
            headers={
                "Location": "https://github.com/ncasuk/AMF_CVs/releases/tag/v1.2.3"
            },
        )
        m.get(
            "https://github.com/ncasuk/AMF_CVs/releases/tag/v1.2.3", text="dummy text"
        )
        result = values.get_latest_CVs_version()
        assert result == "v1.2.3"


def test_get_latest_CVs_version_with_no_version():
    with requests_mock.Mocker() as m:
        m.get(
            "https://github.com/ncasuk/AMF_CVs/releases/latest",
            status_code=302,
            headers={"Location": "https://github.com/ncasuk/AMF_CVs/releases/latest/"},
        )
        m.get("https://github.com/ncasuk/AMF_CVs/releases/latest/", text="dummy text")
        result = values.get_latest_CVs_version()
        assert result == ""


def test_get_latest_instrument_CVs_version():
    with requests_mock.Mocker() as m:
        m.get(
            "https://github.com/ncasuk/ncas-data-instrument-vocabs/releases/latest",
            status_code=302,
            headers={
                "Location": "https://github.com/ncasuk/ncas-data-instrument-vocabs/releases/tag/v1.2.3"
            },
        )
        m.get(
            "https://github.com/ncasuk/ncas-data-instrument-vocabs/releases/tag/v1.2.3",
            text="dummy text",
        )
        result = values.get_latest_instrument_CVs_version()
        assert result == "v1.2.3"


def test_get_latest_instrument_CVs_version_with_no_version():
    with requests_mock.Mocker() as m:
        m.get(
            "https://github.com/ncasuk/ncas-data-instrument-vocabs/releases/latest",
            status_code=302,
            headers={
                "Location": "https://github.com/ncasuk/ncas-data-instrument-vocabs/releases/latest/"
            },
        )
        m.get(
            "https://github.com/ncasuk/ncas-data-instrument-vocabs/releases/latest/",
            text="dummy text",
        )
        result = values.get_latest_instrument_CVs_version()
        assert result == ""


def test_get_common_attributes_url_with_local_files():
    result = values.get_common_attributes_url(use_local_files="/local/path")
    assert result == "/local/path/_common/global-attributes.tsv"


def test_get_common_attributes_url_with_latest_tag():
    with requests_mock.Mocker() as m:
        m.get(
            "https://github.com/ncasuk/AMF_CVs/releases/latest",
            status_code=302,
            headers={
                "Location": "https://github.com/ncasuk/AMF_CVs/releases/tag/v1.2.3"
            },
        )
        m.get(
            "https://github.com/ncasuk/AMF_CVs/releases/tag/v1.2.3", text="dummy text"
        )
        result = values.get_common_attributes_url()
        assert (
            result
            == "https://raw.githubusercontent.com/ncasuk/AMF_CVs/v1.2.3/product-definitions/tsv/_common/global-attributes.tsv"
        )


def test_get_common_attributes_url_with_specific_tag():
    result = values.get_common_attributes_url(tag="v1.2.3")
    assert (
        result
        == "https://raw.githubusercontent.com/ncasuk/AMF_CVs/v1.2.3/product-definitions/tsv/_common/global-attributes.tsv"
    )


def test_get_common_variables_url_with_local_files():
    for loc in ["land", "sea", "air", "trajectory"]:
        result = values.get_common_variables_url(loc=loc, use_local_files="/local/path")
        assert result == f"/local/path/_common/variables-{loc}.tsv"


def test_get_common_variables_url_with_invalid_location():
    with pytest.raises(ValueError):
        values.get_common_variables_url(loc="invalid")


def test_get_common_variables_url_with_latest_tag():
    with requests_mock.Mocker() as m:
        m.get(
            "https://github.com/ncasuk/AMF_CVs/releases/latest",
            status_code=302,
            headers={
                "Location": "https://github.com/ncasuk/AMF_CVs/releases/tag/v1.2.3"
            },
        )
        m.get(
            "https://github.com/ncasuk/AMF_CVs/releases/tag/v1.2.3", text="dummy text"
        )
        for loc in ["land", "sea", "air", "trajectory"]:
            result = values.get_common_variables_url(loc=loc)
            assert (
                result
                == f"https://raw.githubusercontent.com/ncasuk/AMF_CVs/v1.2.3/product-definitions/tsv/_common/variables-{loc}.tsv"
            )


def test_get_common_variables_url_with_specific_tag():
    for loc in ["land", "sea", "air", "trajectory"]:
        result = values.get_common_variables_url(loc=loc, tag="v1.2.3")
        assert (
            result
            == f"https://raw.githubusercontent.com/ncasuk/AMF_CVs/v1.2.3/product-definitions/tsv/_common/variables-{loc}.tsv"
        )


def test_get_common_dimensions_url_with_local_files():
    for loc in ["land", "sea", "air", "trajectory"]:
        result = values.get_common_dimensions_url(
            loc=loc, use_local_files="/local/path"
        )
        assert result == f"/local/path/_common/dimensions-{loc}.tsv"


def test_get_common_dimensions_url_with_invalid_location():
    with pytest.raises(ValueError):
        values.get_common_dimensions_url(loc="invalid")


def test_get_common_dimensions_url_with_latest_tag():
    with requests_mock.Mocker() as m:
        m.get(
            "https://github.com/ncasuk/AMF_CVs/releases/latest",
            status_code=302,
            headers={
                "Location": "https://github.com/ncasuk/AMF_CVs/releases/tag/v1.2.3"
            },
        )
        m.get(
            "https://github.com/ncasuk/AMF_CVs/releases/tag/v1.2.3", text="dummy text"
        )
        for loc in ["land", "sea", "air", "trajectory"]:
            result = values.get_common_dimensions_url(loc=loc)
            assert (
                result
                == f"https://raw.githubusercontent.com/ncasuk/AMF_CVs/v1.2.3/product-definitions/tsv/_common/dimensions-{loc}.tsv"
            )


def test_get_common_dimensions_url_with_specific_tag():
    for loc in ["land", "sea", "air", "trajectory"]:
        result = values.get_common_dimensions_url(loc=loc, tag="v1.2.3")
        assert (
            result
            == f"https://raw.githubusercontent.com/ncasuk/AMF_CVs/v1.2.3/product-definitions/tsv/_common/dimensions-{loc}.tsv"
        )


def test_get_instruments_url_with_local_files():
    result = values.get_instruments_url(use_local_files="/local/path")
    assert (
        result
        == "/local/path/_instrument_vocabs/ncas-instrument-name-and-descriptors.tsv"
    )


def test_get_instruments_url_with_latest_tag():
    with requests_mock.Mocker() as m:
        m.get(
            "https://github.com/ncasuk/ncas-data-instrument-vocabs/releases/latest",
            status_code=302,
            headers={
                "Location": "https://github.com/ncasuk/ncas-data-instrument-vocabs/releases/tag/v1.2.3"
            },
        )
        m.get(
            "https://github.com/ncasuk/ncas-data-instrument-vocabs/releases/tag/v1.2.3",
            text="dummy text",
        )
        result = values.get_instruments_url()
        assert (
            result
            == "https://raw.githubusercontent.com/ncasuk/ncas-data-instrument-vocabs/v1.2.3/product-definitions/tsv/_instrument_vocabs/ncas-instrument-name-and-descriptors.tsv"
        )


def test_get_instruments_url_with_specific_tag():
    result = values.get_instruments_url(tag="v1.2.3")
    assert (
        result
        == "https://raw.githubusercontent.com/ncasuk/ncas-data-instrument-vocabs/v1.2.3/product-definitions/tsv/_instrument_vocabs/ncas-instrument-name-and-descriptors.tsv"
    )


def test_get_community_instruments_url_with_local_files():
    result = values.get_community_instruments_url(use_local_files="/local/path")
    assert (
        result
        == "/local/path/_instrument_vocabs/community-instrument-name-and-descriptors.tsv"
    )


def test_get_community_instruments_url_with_latest_tag():
    with requests_mock.Mocker() as m:
        m.get(
            "https://github.com/ncasuk/ncas-data-instrument-vocabs/releases/latest",
            status_code=302,
            headers={
                "Location": "https://github.com/ncasuk/ncas-data-instrument-vocabs/releases/tag/v1.2.3"
            },
        )
        m.get(
            "https://github.com/ncasuk/ncas-data-instrument-vocabs/releases/tag/v1.2.3",
            text="dummy text",
        )
        result = values.get_community_instruments_url()
        assert (
            result
            == "https://raw.githubusercontent.com/ncasuk/ncas-data-instrument-vocabs/v1.2.3/product-definitions/tsv/_instrument_vocabs/community-instrument-name-and-descriptors.tsv"
        )


def test_get_community_instruments_url_with_specific_tag():
    result = values.get_community_instruments_url(tag="v1.2.3")
    assert (
        result
        == "https://raw.githubusercontent.com/ncasuk/ncas-data-instrument-vocabs/v1.2.3/product-definitions/tsv/_instrument_vocabs/community-instrument-name-and-descriptors.tsv"
    )


def test_get_all_data_products_url_with_local_files():
    result = values.get_all_data_products_url(use_local_files="/local/path")
    assert result == "/local/path/_vocabularies/data-products.tsv"


def test_get_all_data_products_url_with_latest_tag():
    with requests_mock.Mocker() as m:
        m.get(
            "https://github.com/ncasuk/AMF_CVs/releases/latest",
            status_code=302,
            headers={
                "Location": "https://github.com/ncasuk/AMF_CVs/releases/tag/v1.2.3"
            },
        )
        m.get(
            "https://github.com/ncasuk/AMF_CVs/releases/tag/v1.2.3", text="dummy text"
        )
        result = values.get_all_data_products_url()
        assert (
            result
            == "https://raw.githubusercontent.com/ncasuk/AMF_CVs/v1.2.3/product-definitions/tsv/_vocabularies/data-products.tsv"
        )


def test_get_all_data_products_url_with_specific_tag():
    result = values.get_all_data_products_url(tag="v1.2.3")
    assert (
        result
        == "https://raw.githubusercontent.com/ncasuk/AMF_CVs/v1.2.3/product-definitions/tsv/_vocabularies/data-products.tsv"
    )
