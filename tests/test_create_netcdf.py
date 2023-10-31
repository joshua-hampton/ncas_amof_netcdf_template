import pytest
import os
from netCDF4 import Dataset
import numpy as np

import ncas_amof_netcdf_template as nant


def test_make_netcdf():
    nc = nant.create_netcdf.main(
        "ncas-aws-10", date="20221117", dimension_lengths={"time": 5}, return_open=True
    )
    assert os.path.exists("ncas-aws-10_iao_20221117_surface-met_v1.0.nc")
    assert nc["air_temperature"].size == 5
    nant.util.update_variable(nc, "air_temperature", [12.3, 14.54, 23.5, 12.4, 65.3])
    assert nc["air_temperature"].valid_min == np.float32(12.3)
    nc.close()
    os.remove("ncas-aws-10_iao_20221117_surface-met_v1.0.nc")


@pytest.mark.parametrize(
    "instrument, products",
    [
        ("ncas-ceilometer-3", ["aerosol-backscatter", "cloud-base", "cloud-coverage"]),
        ("ncas-aws-10", ["surface-met"]),
    ],
)
def test_list_products(instrument, products):
    test_products = nant.create_netcdf.list_products(instrument)
    assert test_products == products
