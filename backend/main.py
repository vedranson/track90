from time import strptime
from datetime import date

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


@app.get('/')
async def root():
    return {'message': 'root'}
