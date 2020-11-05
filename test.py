

import datetime

weekinfo='8/2/1958'
weekid = datetime.strptime(weekinfo, '%m/%d/%Y')
year = weekid.year
print(year)