import requests
import psycopg2
import json
from Utilities import yearsGenerator
from time import sleep
import sys

# if ran will update players table by populating with nba_id, name, team_nba_id, height, weight, draft team, draft pick, draft year, college, country
startUrl = "https://stats.nba.com/stats/leaguedashplayerbiostats"


conn = psycopg2.connect("dbname=basketball user = nd2")
cur = conn.cursor()
types = set(["Regular Season", "Playoffs", "Pre Season"])        
years = yearsGenerator(19,5)

if (sys.argv[1] == "update"):
    years = yearsGenerator(19,1)

playersSeen = set()
print("start")

for year in years:
    for type in types:
        sleep(2)
        params = dict(LeagueID="00",Season=year,SeasonType=type,PerMode="Totals")
        resp = requests.get(url=startUrl, params = params, headers = {'User-Agent' :  'Mozilla/5.0 (X11; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0'})
        jsonFile = json.loads(resp.text)
        players = jsonFile['resultSets'][0]['rowSet']
        for player in players:
            nbaId = player[0]
            if nbaId not in playersSeen:
                name = player[1]
                height = player[6]
                weight = player[7]
                college = player[8]
                country = player[9]
                draftYear = player[10]
                draftPick = 0
                if draftYear != "Undrafted" and player[12] is not None:
                    draftPick = int(player[12])
                if draftYear == "Undrafted":
                    draftYear = 0
                playersSeen.add(nbaId)
                #print(name)
                cur.execute("insert into players (nba_name,msf_name,dk_name,rg_name, nba_id, height, weight, college, birth_country, draft_year, draft_number) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) on conflict (nba_id) do update set nba_name = %s, nba_id = %s, height = %s, weight = %s, college = %s, birth_country = %s, draft_year = %s, draft_number = %s",(name,name,name,name,nbaId,height,weight,college,country,draftYear,draftPick,name,nbaId,height,weight,college,country,draftYear,draftPick))
                conn.commit()
                
# print("next")

# url ="https://stats.nba.com/stats/commonallplayers?LeagueID=00&Season=2017-18&IsOnlyCurrentSeason=00"
# resp = requests.get(url=url, params = params, headers = {'User-Agent' :  'Mozilla/5.0 (X11; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0'})

# jsonFile = json.loads(resp.text)
# players = jsonFile['resultSets'][0]['rowSet']
# for player in players:
#     id = player[0]
#     nameNba = player[2]
#     print(nameNba)
#     cur.execute("insert into players (nba_id,nba_name) values (%s,%s) on conflict (nba_id) do update set nba_name = %s",(id,nameNba,nameNba))
#     conn.commit()
                    

cur.close()
conn.close()
