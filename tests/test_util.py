import pytest
import requests


from ncas_amof_netcdf_template import util


def test_check_int():
    assert util.check_int('12321') == True
    assert util.check_int('12.432') == False
    assert util.check_int('one') == False

def test_check_float():
    assert util.check_float('12321') == True 
    assert util.check_float('12.432') == True
    assert util.check_float('one') == False
