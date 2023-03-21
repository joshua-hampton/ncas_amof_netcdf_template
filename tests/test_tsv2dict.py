import pytest
import requests


from ncas_amof_netcdf_template import tsv2dict


@pytest.mark.parametrize(
    "product", ["mean-winds", "aerosol-optical-depth", "o2n2-concentration-ratio"]
)
def test_links_exist(product):
    url = tsv2dict.create_variables_tsv_url(product)
    request = requests.get(url)
    assert request.status_code == 200
