import requests
import json
import psycopg2
import time as sleeper
from Utilities import gameStatLineParser
import logging
import sys
#update games set updated = false;

def updateLoop(conn,cur,types):
    logging.basicConfig(filename='gameStatline.log',level = logging.WARNING,filemode = 'w')
    while(True):
        #cur.execute("select nba_id from games where updated = false order by date_of_game desc")
        cur.execute("select nba_id from games where date_of_game >= '10-17-2017' and updated = false")
        games = cur.fetchall()
        leftovers = list()

        total = len(games)
        print(total)
        if(total == 0):
            return 
        completed = 0

        for game in games:
            for type in types:
                sleeper.sleep(0.5)
                gameStatLineParser(game,type,cur,conn,logging)
            cur.execute("update games set updated = true where nba_id = %s ", (str(game[0]),))
            conn.commit()
            completed = completed + 1
            print("            ("+str(completed) + '/' + str(total)+")", end= "\r")


summaryUrl = "https://stats.nba.com/stats/"

types = ["boxscoresummaryv2", "boxscoretraditionalv2", "boxscoreadvancedv2", "boxscoremiscv2","boxscorescoringv2","boxscoreusagev2", "boxscoreplayertrackv2", "hustlestatsboxscore","boxscorematchups","boxscoredefensive"]
#types = ["boxscorematchups"]

conn = psycopg2.connect("dbname=basketball user = nd2")
cur = conn.cursor()


# tweek here to see how far to update
if(sys.argv[1] == "update"):
    cur.execute("select * from games where date_of_game >= current_date - 2 ")
else:
# entire reupdate
    cur.execute("update games set updated = false;")

conn.commit()
updateLoop(conn,cur,types)
        
cur.close()
conn.close()
