from datetime import date

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root():
    response = client.get('/')
    assert response.status_code == 200
    assert response.json() == {'message': 'root'}


def test_date_range_init():
    date_range = DateRange(start=date(year=3333, month=11, day=22))
    assert date_range.start == date(year=3333, month=11, day=22)
    assert date_range.end is None


def test_date_range_init_date_type_arguments():
    date_range = DateRange(date(year=3333, month=11, day=22),
                           date(year=3333, month=11, day=22))
    assert date_range.start == date(year=3333, month=11, day=22)
    assert date_range.end == date(year=3333, month=11, day=22)


def test_date_range_str_to_date():
    assert DateRange.str_to_date('3333-11-22') == date(year=3333, month=11, day=22)


def test_date_range_init_str_type_arguments():
    date_range = DateRange('3333-11-22', '3333-11-22')
    assert date_range.start == date(year=3333, month=11, day=22)
    assert date_range.end == date(year=3333, month=11, day=22)


def test_date_range_str_to_date_fails_when_invalid_date():
    with pytest.raises(ValueError,
                       match="time data '3333-00-00' "
                             "does not match format '%Y-%m-%d'"):
        DateRange.str_to_date('3333-00-00')
    with pytest.raises(ValueError,
                       match="day is out of range for month"):
        DateRange.str_to_date('3333-02-29')


def test_date_range__eq__():
    assert DateRange('3333-11-22') == DateRange('3333-11-22')
    assert not (DateRange('3333-11-22') == DateRange('4444-11-22'))


def test_date_range_order_start_before_end():
    date_range = DateRange('3333-11-22', '4444-11-22')
    date_range.order()
    assert date_range.start == date(year=3333, month=11, day=22)
    assert date_range.end == date(year=4444, month=11, day=22)


def test_date_range_order_end_before_start():
    date_range = DateRange('4444-11-22', '3333-11-22')
    date_range.order()
    assert date_range.start == date(year=3333, month=11, day=22)
    assert date_range.end == date(year=4444, month=11, day=22)


def test_date_range_when_end_is_none():
    date_range = DateRange('3333-11-22')
    with pytest.raises(TypeError, match='Cannot order dates if end date is None'):
        date_range.order()
