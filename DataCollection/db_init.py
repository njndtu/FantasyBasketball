# database initial table creations
import requests
import json
import psycopg2
import os

conn = psycopg2.connect("dbname=basketball user = nd2")
cur = conn.cursor()


# create tables, database basketball must already preexist


# copy nba_abbr to dk_abbr,msf_abbr,

cur.execute("create table if not exists teams ( city text,name text unique,nba_abbr text unique,nba_id integer unique ,msf_id integer unique ,msf_abbr text unique,dk_abbr text unique,rg_abbr text unique,conference boolean,division text, br_abbr text unique); ")

cur.execute("create table if not exists games (date_of_game date,time_of_game time,court text, home text,away text,nba_id integer unique,msf_id integer unique,home_coach text,away_coach text,duration smallint,refs text[],type text,attendence integer,updated boolean);")

cur.execute("create table if not exists officials(nba_id integer unique, first_name text, last_name text, jersey_num smallint); ")

# copy nba name to dk name 
cur.execute("create table if not exists players (nba_name text, msf_name text,dk_name text,rg_name text nba_id integer unique , msf_id integer unique , dk_id integer unique , fd_id integer unique, bday date, birth_city text, birth_country text, college text, twitter text unique, instagram text unique, shooting_hand bool, draft_team text, draft_year smallint, draft_number smallint, height integer, weight integer, other_names text[]); ")

cur.execute("create table if not exists game_statlines(game_id integer, player_id integer, team_id integer, jersey smallint, was_active bool, status text, salary_dk smallint, salary_fd smallint, duration smallint, fgm smallint, fga smallint, threepm smallint, threepa smallint, ftm 
smallint, fta smallint, oreb smallint, dreb smallint, ast smallint, tos smallint, stl smallint, blk smallint, pf smallint, plus_minus smallint, pace real, poto smallint, scp smallint,fbp smallint, pitp smallint, blka smallint, pfd smallint, two_made_ast real, two_made_uast real, three_made_ast real, three_made_uast real, usage real, distance real, speed real, touches smallint, passes smallint, dfgm smallint, dfga smallint, orbc smallint, drbc smallint, contested_fgm smallint, contested_fga smallint, uncontested_fgm smallint, uncontested_fga smallint, screen_assists smallint, deflections smallint, looseball_recovered smallint, charges_drawn smallint, twos_contested smallint, threes_contested smallint,rg_floor small int ,rg_ceiling smallint,rg_predicted smallint ,primary key (game_id,player_id)); ")


cur.execute("create table if not exists matchups(game_id integer, off_player integer, def_player integer, poss smallint, ast smallint, tov smallint, blk smallint, fgm smallint, fga smallint, threepm smallint, threepa smallint, ftm smallint, shooting_foul smallint, def_foul smallint, off_foul smallint, primary key(game_id,off_player,def_player)); ")

cur.execute("create table if not exists coaches(name text unique not null, br_link text);")

# to store rotogrinders
# note this nba_name is actually rg_name
cur.execute("create table if not exists rotogrinders_predictions(rg_name text unique, floor smallint, ceiling smallint, predicted smallint,rg_abbr text)")

conn.commit()


# grab list of players
os.system("python NbaFullGames/NbaPlayers")

# now get initial team ids
os.system("cd ScrapySpiders/ && scrapy crawl nbaTeams && cd ..")

# grab players from MSF
os.system("python MySportsFeed/MsfPlayers")

# grab teams from MSF
os.system("python MySportsFeed/MsfTeamsAndVenues")

# grab gameIds
os.system("python NbaFullGames/NbaTeamGames")

# get actual game stats for each players
os.system("python NbaFullGames/NbaGameStatline")

# now get the salaries for fantasy


cur.close()
conn.close()
