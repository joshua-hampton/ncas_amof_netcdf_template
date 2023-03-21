from ncas_amof_netcdf_template import util


def test_check_int():
    assert util.check_int("12321") is True
    assert util.check_int("12.432") is False
    assert util.check_int("one") is False


def test_check_float():
    assert util.check_float("12321") is True
    assert util.check_float("12.432") is True
    assert util.check_float("one") is False
