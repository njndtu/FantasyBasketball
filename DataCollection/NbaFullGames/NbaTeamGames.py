import requests
import psycopg2
import json
from time import sleep
from Utilities import yearsGenerator
import sys

# if ran will completely reupdate, gameId, date, duration, home and away



# currentYear = 18


# returns a list, [0] = home, [1] = away
def homeAwayParser(matchupString):
    words = matchupString.split()
    result = list()
    
    if (words[1] == '@'):
        result.append(words[2])
        result.append(words[0])
    else:
        result.append(words[0])
        result.append(words[2])
    return result
                      


conn = psycopg2.connect("dbname=basketball user = nd2")
cur = conn.cursor()
cur.execute("select nba_id from teams;")
teams = cur.fetchall()
startUrl = "https://stats.nba.com/stats/teamgamelog"
years = yearsGenerator(19,3)
types = set(["Regular Season", "Playoffs", "Preseason"])

if (sys.argv[1] == "update"):
    years = yearsGenerator(19,1)
    types = set(["Regular Season"])


# goes thru all gmaes, adds entries to games table, the process loops thru each team's games
for year in years:
    gamesSeen = set()
    for team in teams:
        for type in types:
            sleep(1)
            params = dict(Season=year,SeasonType=type,TeamID=team)
            sleep(1)
            resp = requests.get(url = startUrl, params = params, headers = {'User-Agent' : 	'Mozilla/5.0 (X11; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0'})
            data = resp.text
            print(resp.url)
            jsonFile = json.loads(data)
            games = jsonFile['resultSets'][0]['rowSet']
            for game in games:
                gameId = game[1]
                if gameId not in gamesSeen:
                    date = game[2]
                    homeAway = homeAwayParser(game[3])
                    home = homeAway[0]
                    away = homeAway[1]
                    seconds = game[8] / 5 * 60
                    gamesSeen.add(gameId)
                    cur.execute("insert into games (date_of_game, home, away, nba_id,duration,type,updated) values (%s,%s,%s,%s,%s,%s,false) on conflict (nba_id) do update set date_of_game = %s, home = %s, away = %s,nba_id = %s, duration = %s, type = %s", (date,home,away,gameId,seconds,type, date,home,away,gameId,seconds,type))
                    conn.commit()
                
cur.close()
conn.close()


