import pytest

from ncas_amof_netcdf_template.create_netcdf import list_products


@pytest.mark.parametrize("instrument, products", [('ncas-ceilometer-3',['aerosol-backscatter','cloud-base','cloud-coverage']),('ncas-aws-10',['surface-met'])])
def test_list_products(instrument, products):
    test_products = list_products(instrument)
    assert test_products == products


