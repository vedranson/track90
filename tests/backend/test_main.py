from datetime import date

import pytest
from fastapi.testclient import TestClient
from backend.main import app, DateRange, StayCollection

client = TestClient(app)


def day(d):
    return date(year=1, month=1, day=d)


def day_str(d):
    return str(date(year=1, month=1, day=d))


def test_root():
    response = client.get('/')
    assert response.status_code == 200
    assert response.json() == {'message': 'root'}


def test_date_range_init():
    date_range = DateRange(start=day(1))
    assert date_range.start == day(1)
    assert date_range.end is None


def test_date_range_str_to_date():
    assert DateRange.str_to_date(day_str(1)) == day(1)


def test_date_range_init_date_type_arguments():
    """ The DateRange constructor takes datetime.date or string type arguments.
        The instance start and end attributes get datetime.date type.
    """
    date_range = DateRange(start=day(1), end=day(2))
    assert date_range.start == day(1)
    assert date_range.end == day(2)

    date_range = DateRange(start=day_str(1), end=day_str(2))
    assert date_range.start == day(1)
    assert date_range.end == day(2)

    date_range = DateRange(start=day(1), end=day_str(2))
    assert date_range.start == day(1)
    assert date_range.end == day(2)

    date_range = DateRange(start=day_str(1), end=day(2))
    assert date_range.start == day(1)
    assert date_range.end == day(2)


def test_date_range_str_to_date_fails_when_invalid_date():
    with pytest.raises(ValueError,
                       match="time data '1111-00-00' "
                             "does not match format '%Y-%m-%d'"):
        DateRange.str_to_date('1111-00-00')
    with pytest.raises(ValueError,
                       match="day is out of range for month"):
        DateRange.str_to_date('1111-02-29')


def test_date_range__eq__():
    assert DateRange(start=day(1)) == DateRange(start=day(1))
    assert DateRange(start=day(1)) == DateRange(start=day(1), end=None)
    assert not (DateRange(start=day(1)) == DateRange(day(2)))
    assert not (DateRange(start=day(1), end=day(2)) == DateRange(start=day(1)))


def test_date_range_order_start_before_end():
    """ If start and end are already ordered, change neither.
    """
    date_range = DateRange(start=day(1), end=day(2))
    date_range.order()
    assert date_range.start == day(1)
    assert date_range.end == day(2)


def test_date_range_order_end_before_start():
    """ If end is later than start, switch the two.
    """
    date_range = DateRange(start=day(2), end=day(1))
    date_range.order()
    assert date_range.start == day(1)
    assert date_range.end == day(2)


def test_date_range_order_same_dates():
    """ If start and end are the same, change neither.
    """
    date_range = DateRange(start=day(1), end=day(1))
    date_range.order()
    assert date_range.start == day(1)
    assert date_range.end == day(1)


def test_date_range_when_end_is_none():
    date_range = DateRange(start=day(1))
    with pytest.raises(TypeError, match='Cannot order dates if end date is None'):
        date_range.order()


def test_date_range_are_start_end_same():
    date_range = DateRange(start=day(1))
    assert date_range.are_start_end_same() is False
    date_range = DateRange(start=day(1), end=day(2))
    assert date_range.are_start_end_same() is False
    date_range = DateRange(start=day(1), end=day(1))
    assert date_range.are_start_end_same() is True


def test_date_range_is_date_within():
    date_range = DateRange(start=day(2), end=day(4))
    assert date_range.is_date_within_range(day(1)) is False
    assert date_range.is_date_within_range(day(2)) is True
    assert date_range.is_date_within_range(day(3)) is True
    assert date_range.is_date_within_range(day(4)) is True
    assert date_range.is_date_within_range(day(5)) is False


def test_stay_collection():
    stays = StayCollection()
    assert stays.stays == []
    assert stays._no_end_range is None


def test_stay_collection_from_list_with_one_str_date():
    stays = StayCollection([day_str(1)])
    assert stays.stays == [DateRange(start=day(1))]
    assert stays._no_end_range == DateRange(start=day(1))


def test_stay_collection_from_list_with_two_dates():
    stays = StayCollection([day_str(1), day(2)])
    assert stays.stays == [
        DateRange(start=day(1), end=day(2)),
    ]
    assert stays._no_end_range is None


def test_stay_collection_from_list_with_the_two_same_dates():
    stays = StayCollection([day_str(1), day_str(2)])
    assert stays.stays == [
        DateRange(start=day(1), end=day(2)),
    ]
    assert stays._no_end_range is None


def test_stay_collection_from_list_with_three_dates():
    stays = StayCollection([day_str(1), day_str(2), day_str(3)])
    assert stays.stays == [
        DateRange(start=day(1), end=day(2)),
        DateRange(start=day(3))
    ]
    assert stays._no_end_range == DateRange(start=day(3))


def test_stay_collection_from_list_with_none():
    with pytest.raises(TypeError, match='None instead of a date string'):
        StayCollection([day_str(1), None, day(2)])


def test_stay_collection_add_date():
    stays = StayCollection()
    stays.add_date(day(1))
    assert stays.stays == [
        DateRange(start=day(1)),
    ]
    assert stays._no_end_range == DateRange(start=day(1))


def test_stay_collection_add_date_as_string():
    stays = StayCollection()
    stays.add_date(day_str(1))
    assert stays.stays == [
        DateRange(start=day(1)),
    ]
    assert stays._no_end_range == DateRange(start=day(1))


def test_stay_collection_add_date_add_date():
    stays = StayCollection()
    stays.add_date(day(1))
    stays.add_date(day(2))
    assert stays.stays == [
        DateRange(start=day(1), end=day(2)),
    ]
    assert stays._no_end_range is None


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
