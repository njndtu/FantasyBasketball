import requests
import json
import psycopg2
from Utilities import send_request
from Utilities import salaryFiller
import sys
# just grab what I need then, cus this data be incomplete




conn = psycopg2.connect("dbname=basketball user = nd2")
cur = conn.cursor()

cur.execute("select distinct date_of_game from games where date_of_game >= '2016-04-16' and date_of_game <= '2016-06-19' ")
playoff2016 = cur.fetchall()

cur.execute("select distinct date_of_game from games where date_of_game >= '2017-04-15' and date_of_game <= '2017-06-12' ")
playoff2017 = cur.fetchall()

cur.execute("select distinct date_of_game from games where date_of_game >= '2018-04-14' and date_of_game <= '2018-06-08' ")
playoff2018 = cur.fetchall()

cur.execute("select distinct date_of_game from games where date_of_game >= '2016-10-25' and date_of_game <= '2017-04-12' ")
regular2016 = cur.fetchall()

cur.execute("select distinct date_of_game from games where date_of_game >= '2017-10-17' and date_of_game <= '2018-04-11' ")
regular2017 = cur.fetchall()

cur.execute("select distinct date_of_game from games where date_of_game >= '2018-10-16' and date_of_game <= '2019-04-10' ")
regular2018 = cur.fetchall()

years = ["2016-playoff","2016-2017-regular","2017-playoff","2017-2018-regular","2018-playoff","2018-2019-regular"]
manualAdds = list()

if (sys.argv[1] == "update"):
    years = ["update"]

for year in years:
    if (year == "2016-playoff"):
        gameCache = set()
        playerCache = [set(),set()]
        for date in playoff2016:
            salaryFiller(year,date,cur,conn,gameCache,playerCache,manualAdds)
    if (year == "2016-2017-regular"):
        gameCache = set()
        playerCache = [set(),set()]
        for date in regular2016:
            salaryFiller(year,date,cur,conn,gameCache,playerCache,manualAdds)
    if (year == "2017-playoff"):
        gameCache = set()
        playerCache = [set(),set()]
        for date in playoff2017:
            salaryFiller(year,date,cur,conn,gameCache,playerCache,manualAdds)
    if (year == "2017-2018-regular"):
        gameCache = set()
        playerCache = [set(),set()] 
        for date in regular2017:
            salaryFiller(year,date,cur,conn,gameCache,playerCache,manualAdds)
    if (year == "2018-playoff"):
        gameCache = set()
        playerCache = [set(),set()]
        for date in playoff2018:
            salaryFiller(year,date,cur,conn,gameCache,playerCache,manualAdds)
    if (year == "2018-2019-regular"):
        gameCache = set()
        playerCache = [set(),set()]
        for date in regular2018:
            salaryFiller(year,date,cur,conn,gameCache,playerCache,manualAdds)
    if(year == "update"):
        gameCache = set()
        playerCache = [set(),set()]
        year = "2018-2019-regular"
        # tweek here for number of days back
        cur.execute("select distinct date_of_game from games where date_of_game >= current_date - 2 ")
        toDo = cur.fetchall()
        for date in toDo:
            salaryFiller(year,date,cur,conn,gameCache,playerCache,manualAdds)

            
cur.close()
conn.close()
print(manualAdds)
