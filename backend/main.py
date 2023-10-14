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

    def are_start_end_same(self):
        return self.end is not None and self.start == self.end

    @staticmethod
    def str_to_date(s: str | date | None) -> date | None:
        if s is not None:
            if isinstance(s, str):
                try:
                    a_date = strptime(s, ISO_DATE_FORMAT)
                except Exception as e:
                    raise e
                return \
                    date(year=a_date.tm_year, month=a_date.tm_mon, day=a_date.tm_mday)
            return s

    def __eq__(self, other):
        return other is not None and self.start == other.start and self.end == other.end


class StayCollection:
    """ Represents a collection of date ranges.
    """

    def __init__(self, dates: list[str] = None):
        self.stays: list[DateRange] = []
        self.no_end_idx: int | None = None

        if dates is not None:
            self._process(dates)

    def add_date(self, d: date | str) -> None:
        if self.no_end_idx is None:
            self._add_no_end_date_range(d)
        else:
            self._update_no_end_date_range(d)

    def _update_no_end_date_range(self, d):
        self.stays[self.no_end_idx].end = DateRange.str_to_date(d)
        self.stays[self.no_end_idx].order()
        self._check_action(self.stays[self.no_end_idx])
        self.no_end_idx = None

    def _add_no_end_date_range(self, d):
        self.stays.append(DateRange(start=d))
        self.no_end_idx = len(self.stays) - 1

    def _check_action(self, dr: DateRange):
        if dr.are_start_end_same():
            for stay in self.stays:
                if stay.start <= dr.start <= stay.end:
                    # remove both
                    break
        else:
            pass

    def _process(self, dates):
        for d in dates:
            if d is None:
                raise TypeError('None instead of a date string')
            self.add_date(d)

    def _merge(self, new: DateRange):
        if not self.stays:
            self.stays.append(new)
            return
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
