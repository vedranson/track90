from datetime import date

import pytest
from fastapi.testclient import TestClient
from backend.main import app, DateRange, StayCollection

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
    date_range = DateRange(start=date(year=3333, month=11, day=22),
                           end=date(year=3333, month=11, day=22))
    assert date_range.start == date(year=3333, month=11, day=22)
    assert date_range.end == date(year=3333, month=11, day=22)


def test_date_range_str_to_date():
    assert DateRange.str_to_date('3333-11-22') == date(year=3333, month=11, day=22)


def test_date_range_init_str_type_arguments():
    date_range = DateRange(start='3333-11-22', end='3333-11-22')
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
    assert DateRange(start='3333-11-22') == DateRange(start='3333-11-22')
    assert DateRange(start='3333-11-22') == DateRange(start='3333-11-22', end=None)
    assert not (DateRange(start='3333-11-22') == DateRange(start='4444-11-22'))
    assert not (DateRange(start='3333-11-22', end='4444-11-12') ==
                DateRange(start='4444-11-22'))


def test_date_range_order_start_before_end():
    date_range = DateRange(start='3333-11-22', end='4444-11-22')
    date_range.order()
    assert date_range.start == date(year=3333, month=11, day=22)
    assert date_range.end == date(year=4444, month=11, day=22)


def test_date_range_order_end_before_start():
    date_range = DateRange(start='4444-11-22', end='3333-11-22')
    date_range.order()
    assert date_range.start == date(year=3333, month=11, day=22)
    assert date_range.end == date(year=4444, month=11, day=22)


def test_date_range_order_same_dates():
    date_range = DateRange(start='2222-11-22', end='2222-11-22')
    date_range.order()
    assert date_range.start == date(year=2222, month=11, day=22)
    assert date_range.end == date(year=2222, month=11, day=22)


def test_date_range_when_end_is_none():
    date_range = DateRange(start='3333-11-22')
    with pytest.raises(TypeError, match='Cannot order dates if end date is None'):
        date_range.order()


def test_date_range_are_start_end_same():
    date_range = DateRange(start='2222-11-22')
    assert date_range.are_start_end_same() is False
    date_range = DateRange(start='2222-11-22', end='2222-11-23')
    assert date_range.are_start_end_same() is False
    date_range = DateRange(start='2222-11-22', end='2222-11-22')
    assert date_range.are_start_end_same() is True


def test_stay_collection():
    stays = StayCollection()
    assert stays.stays == []
    assert stays.no_end_idx is None


def test_stay_collection_from_list_with_one_str_date():
    stays = StayCollection(['1111-11-22'])
    assert stays.stays == [DateRange(start=date(year=1111, month=11, day=22))]
    assert stays.no_end_idx == 0


def test_stay_collection_from_list_with_two_dates():
    stays = StayCollection(['1111-11-22', '2222-11-22'])
    assert stays.stays == [
        DateRange(start=date(year=1111, month=11, day=22),
                  end=date(year=2222, month=11, day=22)),
    ]
    assert stays.no_end_idx is None


def test_stay_collection_from_list_with_the_two_same_dates():
    stays = StayCollection(['2222-11-22', '2222-11-22'])
    assert stays.stays == [
        DateRange(start=date(year=2222, month=11, day=22),
                  end=date(year=2222, month=11, day=22)),
    ]
    assert stays.no_end_idx is None


def test_stay_collection_from_list_with_three_dates():
    stays = StayCollection(['1111-11-22', '2222-11-22', '3333-11-22'])
    assert stays.stays == [
        DateRange(start=date(year=1111, month=11, day=22),
                  end=date(year=2222, month=11, day=22)),
        DateRange(start=date(year=3333, month=11, day=22))
    ]
    assert stays.no_end_idx == 1


def test_stay_collection_from_list_with_none():
    with pytest.raises(TypeError, match='None instead of a date string'):
        StayCollection(['1111-11-22', None, '3333-11-22'])


def test_stay_collection_add_date():
    stays = StayCollection()
    stays.add_date(date(year=3333, month=11, day=22))
    assert stays.stays == [DateRange(start=date(year=3333, month=11, day=22))]
    assert stays.no_end_idx == 0
    assert (stays.stays[stays.no_end_idx] ==
            DateRange(start=date(year=3333, month=11, day=22)))


def test_stay_collection_add_date_add_date():
    stays = StayCollection()
    stays.add_date(date(year=3333, month=11, day=22))
    stays.add_date(date(year=4444, month=11, day=22))
    assert stays.stays == [
        DateRange(start=date(year=3333, month=11, day=22),
                  end=date(year=4444, month=11, day=22)),
    ]
    assert stays.no_end_idx is None


def test_check_action_same_start_end_outside_existing_date_range():
    """ When the new date range
        has the same start and end and,
        it does not intersect with any other data range
        just add the new date range.

    """
    stays = StayCollection([day_str(1), day_str(2)])
    stays.add_date(day(4))
    stays.add_date(day(4))
    assert stays.stays == [
        DateRange(start=day(1), end=day(2)),
        DateRange(start=day(4), end=day(4)),
    ]


def test_check_action_same_start_end_inside_existing_date_range():
    """ When the new date range
        has the same start and end and,
        that start/end is contained in an existing data range
        remove both the new and the existing data range.
    """
    stays = StayCollection([
        day_str(1), day_str(3),
    ])
    stays.add_date(day(2))
    stays.add_date(day(2))
    assert stays.stays == []

    stays = StayCollection([
        day_str(1), day_str(2), day_str(4), day_str(5),
    ])
    stays.add_date(day(1))
    stays.add_date(day(1))
    assert stays.stays == [
        DateRange(start=day(4), end=day(5)),
    ]

    stays = StayCollection([
        day_str(1), day_str(2), day_str(4), day_str(5), day_str(7), day_str(8)
    ])
    stays.add_date(day(4))
    stays.add_date(day(4))
    assert stays.stays == [
        DateRange(start=day(1), end=day(2)),
        DateRange(start=day(7), end=day(8)),
    ]


def test_check_action_without_intersection():
    """ When the new date range
        has different start and end and,
        it does not intersect with any other data range
        just add the new date range.
    """
    stays = StayCollection([
        day_str(1), day_str(2)
    ])
    stays.add_date(day(4))
    stays.add_date(day(4))
    assert stays.stays == [
        DateRange(start=day(1), end=day(2)),
        DateRange(start=day(4), end=day(4)),
    ]


def test_check_action_without_intersection_next_to_existing():
    """ When the new date range
        has different start and end and,
        it does not intersect with any other date range,
        but it's next to an existing date range
        add the new date range, and merge it with its neighbour(s).
    """
    stays = StayCollection([
        day_str(1), day_str(2),
    ])
    stays.add_date(day(3))
    stays.add_date(day(4))
    assert stays.stays == [
        DateRange(start=day(1), end=day(4)),
    ]

    stays = StayCollection([
        day_str(3), day_str(4),
    ])
    stays.add_date(day(1))
    stays.add_date(day(2))
    assert stays.stays == [
        DateRange(start=day(1), end=day(4)),
    ]

    stays = StayCollection([
        day_str(1), day_str(2), day_str(5), day_str(6), day_str(9), day_str(10),
    ])
    stays.add_date(day(3))
    stays.add_date(day(3))
    assert stays.stays == [
        DateRange(start=day(1), end=day(3)),
        DateRange(start=day(5), end=day(6)),
        DateRange(start=day(9), end=day(10)),
    ]
    stays.add_date(day(4))
    stays.add_date(day(4))
    assert stays.stays == [
        DateRange(start=day(1), end=day(6)),
        DateRange(start=day(9), end=day(10)),
    ]
    stays.add_date(day(7))
    stays.add_date(day(8))
    assert stays.stays == [
        DateRange(start=day(1), end=day(10)),
    ]


def test_check_action_with_intersection():
    """ When the new date range
        has different start and end and,
        either of them intersects with any other date range,
        add the new date range, and merge any intersecting date range.
    """
    stays = StayCollection([
        day_str(4), day_str(5),
    ])
    stays.add_date(day(4))
    stays.add_date(day(6))
    assert stays.stays == [
        DateRange(start=day(4), end=day(6)),
    ]
    stays.add_date(day(6))
    stays.add_date(day(7))
    assert stays.stays == [
        DateRange(start=day(4), end=day(7)),
    ]
    stays.add_date(day(10))
    stays.add_date(day(11))
    assert stays.stays == [
        DateRange(start=day(4), end=day(7)),
        DateRange(start=day(10), end=day(11)),
    ]
    stays.add_date(day(1))
    stays.add_date(day(12))
    assert stays.stays == [
        DateRange(start=day(1), end=day(12)),
    ]
