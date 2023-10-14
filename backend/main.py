from time import strptime
from datetime import date, timedelta
from operator import itemgetter

from fastapi import FastAPI

app = FastAPI()

ISO_DATE_FORMAT = '%Y-%m-%d'


class DateRange:
    """ Represents a stay with a start date and an optional end date.
        Allows arguments of type timedate.date or ISO date format string.
    """

    def __init__(self,
                 start: date | str,
                 end: date | str | None = None):
        self.start: date = self.str_to_date(start)
        self.end: date = self.str_to_date(end)

    def order(self):
        if self.end is None:
            raise TypeError('Cannot order dates if end date is None')
        if self.end < self.start:
            self.start, self.end = self.end, self.start

    def are_start_end_same(self) -> bool:
        return self.end is not None and self.start == self.end

    def is_date_within_range(self, d: date | str) -> bool:
        d = self.str_to_date(d)
        return self.start <= d <= self.end

    @staticmethod
    def str_to_date(d: str | date | None) -> date | None:
        if d is not None:
            if isinstance(d, str):
                try:
                    a_date = strptime(d, ISO_DATE_FORMAT)
                except Exception as e:
                    raise e
                return \
                    date(year=a_date.tm_year, month=a_date.tm_mon, day=a_date.tm_mday)
            return d

    def __eq__(self, other):
        return other is not None and self.start == other.start and self.end == other.end


class StayCollection:
    """ Represents a collection of date ranges.
    """

    def __init__(self, dates: list[str] = None):
        self.stays: list[DateRange] = []
        self._no_end_range: DateRange | None = None

        if dates is not None:
            self._process(dates)

    def add_date(self, d: date | str) -> None:
        if self._no_end_range is None:
            self._add_no_end_date_range(d)
        else:
            self._update_no_end_date_range(d)

    def _update_no_end_date_range(self, d):
        self.stays.remove(self._no_end_range)
        self._no_end_range.end = DateRange.str_to_date(d)
        self._no_end_range.order()
        self._check_action(self._no_end_range)
        self._no_end_range = None

    def _add_no_end_date_range(self, d):
        self._no_end_range = DateRange(start=d)
        self.stays.append(self._no_end_range)

    def _check_action(self, new_date_range: DateRange):
        if new_date_range.are_start_end_same() and \
                (stay := self._is_date_in(new_date_range.start)):
            self.stays.remove(stay)
        else:
            self.stays.append(new_date_range)
            self._merge()

    def _is_date_in(self, d: str | date) -> DateRange | None:
        for stay in self.stays:
            if stay.is_date_within_range(d):
                return stay

    def _process(self, dates):
        for d in dates:
            if d is None:
                raise TypeError('None instead of a date string')
            self.add_date(d)

    def _merge(self):
        stays = sorted([(stay.start, stay.end) for stay in self.stays],
                       key=itemgetter(0))
        merged = []
        i = 0
        start, end = stays[i]
        for i in range(1, len(stays)):
            next_stay = stays[i]
            if end + timedelta(days=1) >= next_stay[0]:
                end = max(end, next_stay[1])
            else:
                merged.append(DateRange(start, end))
                start, end = next_stay
        merged.append(DateRange(start, end))
        self.stays = merged


@app.get('/')
async def root():
    return {'message': 'root'}
