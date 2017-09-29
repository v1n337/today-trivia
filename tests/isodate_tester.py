import isodate
from datetime import date, timedelta

date_string = "2020-08"

print(isodate.parse_date(date_string))
print(date.today())

other_date = isodate.parse_date(date_string)
today_date = date.today()

while other_date > today_date:
    other_date -= timedelta(days=365)

print(other_date)
