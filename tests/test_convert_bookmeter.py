import pytest
import unittest.mock
from selenium import webdriver
from selenium.webdriver.common.by import By
from mypkg.convert_bookmeter import check_date
from mypkg.convert_bookmeter import set_input_date
from mypkg.convert_bookmeter import set_email
from mypkg.convert_bookmeter import set_password


@pytest.mark.parametrize(("x", "expected"), [
    ("2020-01-01", True),
    ("0000-01-01", False),
    ("2020-13-01", False),
    ("2020-01-32", False),
    ("2020-ab-01", False),
    ("202-01-01", False),
    ("2020-1-01", False),
    ("2020-01-1", False),
    ("test-dd-mm", False),
    ("2020/01/01", False),
    ("20200101", False),
    ("2020011", False),
    ("202001011", False),
    ("test", False),
    ("", False)])
def test_check_date(x, expected):
    res = check_date(x)
    assert res == expected


@pytest.mark.parametrize(("x", "expected"), [
    ("", ""),
    ("2020-01-01", "2020-01-01")
])
def test_set_input_date(x, expected):
    with unittest.mock.patch('builtins.input', return_value=x):
        res = set_input_date()
        assert res == expected


@pytest.mark.parametrize(("x", "expected"), [
    ("test@test.jp", "test@test.jp"),
])
def test_set_email(x, expected):
    driver = webdriver.Chrome()
    driver.get("https://bookmeter.com/login")

    with unittest.mock.patch('builtins.input', return_value=x):
        res = set_email(driver)
        assert res == expected
    driver.quit()


@pytest.mark.parametrize(("x", "expected"), [
    ("password", "password"),
])
def test_set_password(x, expected):
    driver = webdriver.Chrome()
    driver.get("https://bookmeter.com/login")

    with unittest.mock.patch('builtins.input', return_value=x):
        res = set_password(driver)
        assert res == expected
    driver.quit()


if __name__ == "__main__":
    pass
