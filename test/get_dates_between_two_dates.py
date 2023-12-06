from calendar import monthrange
from datetime import datetime, timedelta, date
from collections import OrderedDict
from cffi.backend_ctypes import xrange

dates = ["2014-10-10", "2016-01-07"]
start, end = [datetime.strptime(_, "%Y-%m-%d") for _ in dates]
result = OrderedDict(((start + timedelta(_)).strftime(r"%m-%Y"), None)
                     for _ in xrange((end - start).days)).keys()
last_dates = []
for i in list(result):
    date_object: date = datetime.strptime(i, '%m-%Y').date()
    last_month_day: int = monthrange(date_object.year, date_object.month)[1]
    last_date: date = date(date_object.year, date_object.month, last_month_day)
    last_dates.append(last_date)

print(list(result))
print(last_dates)
