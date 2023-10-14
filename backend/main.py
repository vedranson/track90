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
        self._endless: DateRange | None = None

        if dates is not None:
            self._process(dates)

    def add_date(self, d: date | str) -> None:
        if self._endless is None:
            self._endless = DateRange(start=d)
            self.stays.append(self._endless)
        else:
            self._update_endless_stay(d)

    def _update_endless_stay(self, end):

        self.stays.remove(self._endless)

        new_stay = DateRange(self._endless.start, end)
        new_stay.order()

        self._endless = None

        self._remove_existing_or_merge_new(new_stay)

    def _remove_existing_or_merge_new(self, new_stay):

        possible_removal_requested = new_stay.are_start_end_same()

        if possible_removal_requested:
            stay_to_be_removed = self._get_stay_containing(new_stay.start)
            if stay_to_be_removed:
                self.stays.remove(stay_to_be_removed)
                return

        self._merge(new_stay)

    def _get_stay_containing(self, d: str | date) -> DateRange | None:
        for stay in self.stays:
            if stay.is_date_within_range(d):
                return stay

    def _process(self, dates):
        for d in dates:
            if d is None:
                raise TypeError('None instead of a date string')
            self.add_date(d)

    def _merge(self, new_stay: DateRange):
        self.stays.append(new_stay)
        stays = sorted([(stay.start, stay.end) for stay in self.stays],
                       key=itemgetter(0))
        merged = []
        i = 0
        start, end = stays[i]
        for i in range(1, len(stays)):
            next_start, next_end = stays[i]
            if end + timedelta(days=1) >= next_start:
                end = max(end, next_end)
            else:
                merged.append(DateRange(start, end))
                start, end = next_start, next_end
        merged.append(DateRange(start, end))
        self.stays = merged


@app.get('/')
async def root():
    return {'message': 'root'}
