import requests
from Utilities import send_request
import json
import psycopg2

dates = ["2015-2016-regular","2016-playoff","2016-2017-regular","2017-playoff", "2017-2018-regular,2018-playoff"]

conn = psycopg2.connect("dbname=basketball user = nd2")
cur = conn.cursor()

url = "https://api.mysportsfeeds.com/v2.0/pull/nba/2016-2017-regular/team_stats_totals.json"
params = dict()
resp = send_request(url,params)
jsonFile = json.loads(resp.text)
teams = jsonFile['teamStatsTotals']
for team in teams:
    msfId = team['team']['id']
    city = team['team']['city']
    name = team['team']['name']
    abbr = team['team']['abbreviation']
    print(abbr)
    cur.execute("update teams set city = %s,name = %s, msf_id = %s,msf_abbr = %s where nba_abbr = %s",(city,name,msfId,abbr,abbr))

    # discrepencies  
    if name == "Thunder" :
        cur.execute("update teams set city = %s,name = %s, msf_id = %s,msf_abbr = %s where nba_abbr = %s",(city,name,msfId,abbr,"OKC"))
    if name == "Nets" :
        cur.execute("update teams set city = %s,name = %s, msf_id = %s,msf_abbr = %s where nba_abbr = %s",(city,name,msfId,abbr,"BKN"))
    conn.commit()

cur.close()
conn.close()
