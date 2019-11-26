# database initial table creations
import requests
import json
import psycopg2
import os
from time import sleep
import sys

# arguments to pass in
# rg : just update rotogrinder predictions
# normal : run this base start everyday


# do this everyday
# run this script, manually remove csv files, then download the csv files

# time has yet to exceed 20 mins



# pass in rg to just run update on rg predicitons
if(sys.argv[1] == "rg"):
    os.chdir("ScrapySpiders")
    os.system("scrapy crawl rg_predictions")
    quit()

conn = psycopg2.connect("dbname=basketball user = nd2")
cur = conn.cursor()

# first get players
# update argument does some different
print("NBA players---------------------------------")
os.system("python NbaFullGames/NbaPlayers.py update")

print("MSF players---------------------------------")
os.system("python MySportsFeed/MsfPlayers.py")

print("NBA team games---------------------------------")
os.system("python NbaFullGames/NbaTeamGames.py update")

print("NBA statline---------------------------------")
os.system("python NbaFullGames/NbaGameStatline.py update")

print("MSF salaries---------------------------------")
os.system("python MySportsFeed/MsfSalaries.py update")

# now get the salaries from previous 
# lol them id's be wrong though

# now get coaches
print("BR coaches---------------------------------")
os.system("python BasketballReference/BrCoaches.py update")

# before deletion/update of rotogrinders, copy all rotogrinders predictions down



# need game id from games using current_date - 1
# need player id from players using rg_name from rotogrinders_predictions
#  by the time i get here, the game_statlines will already be here, I can create a view with these game ids, then update the player id

#(this view has to be dropped everytime)

#create view rg_prediction_updating as select game_statlines.game_id,game_statlines.player_id,game_statlines.rg_floor,game_statlines.rg_ceiling,game_statlines.rg_predicted FROM game_statlines inner join games on games.nba_id = game_statlines.game_id where games.date_of_game = current_date - 1

#create rule rg_prediction_updating_update as on update to rg_prediction_updating do instead(update game_statlines set rg_floor = NEW.rg_floor,rg_ceiling = NEW.rg_ceiling,rg_predicted = NEW.rg_predicted where game_id = OLD.game_id and player_id = OLD.player_id);

#(same for this view)

#I need to create a view between rg_predictions and players based on rg_name. Need player_id,floor,ceiling,predcited


#(final step is to update rg_prediction_updating)
#set the first views f,c,p into the second views f,c,p, where their playerids match

#with rotogrinders as (select * from rg_predictions), current_games as (select nba_id from games where date_of_game = current_date - 1), rg_player_and_id as (select rg_name, nba_id from players) update game_statlines set game_statlines.rg_floor = rotogrinders.floor,game_statlines.rg_ceiling = rotogrinders.ceiling,game_statlines.rg_predicted = rotogrinders.predicted where 


#cur.execute("insert into game_statlines (gameId, playerId) select ")
#conn.commit()



# update rotogrinders stuff, before updating clear the table

cur.execute("delete from rotogrinders_predictions")
conn.commit()

os.chdir("ScrapySpiders")
os.system("scrapy crawl rg_predictions")



cur.close()
conn.close()
