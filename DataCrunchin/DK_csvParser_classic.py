import csv
import psycopg2
import numpy as np
import os

# need to check if team abbr match up

# each new csv i might need to manually input stuff

# returns np 2d array (n x 15), n is number of players
# number of arrays depends on the number of games


# heuristic is inserted by individual lineup generators

# insert injury thing here, so that parser gets rid of injured players
def csvTo2dList() :
    
    conn = psycopg2.connect("dbname=basketball user = nd2")
    cur = conn.cursor()

    noMatchingPlayers_dk = set()
    noMatchingTeams = set()

    games = dict()
    gameNum = 0;

    gameSets = list()
    gameSets_games = list()
    # boolean 
    first = True

    # these people do not show up on nba stats, need to watch out in the scenario that these people pop off
    untouchables = ["Julian Washburn", "Stephan Hicks"]

    for aCsvFile in os.listdir(os.getcwd()+"/DK_salaries/classic"):
        
        with open(os.getcwd()+"/DK_salaries/classic/"+aCsvFile, newline='') as csvfile:
            print(aCsvFile)
            #reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
            reader = csv.DictReader(csvfile)
            count = 0;
            players = list()
            daGames = set()
            
            for row in reader:
                #print (', '.join(row))
                if(count > 6):
                    onePlayer = list();
                    #print(row)
                    #print(row[2])
                    #print(row[3])
                    player = (row[None])
                    name = player[1]
                    
                    if(name in untouchables):
                        print(name)
                        continue
                    
                    dk_id = player[2]
                    slots = player[3].split("/")
                    salary = int(player[4])
                    game = (player[5].split(" "))[0].split("@")
                    if (player[5].split(" ")[0] not in games):
                        games[player[5].split(" ")[0]] = gameNum
                        gameNum+=1
                        
                    if(games[player[5].split(" ")[0]] not in daGames):
                        daGames.add(games[player[5].split(" ")[0]])
                        
                    whichGame = games[player[5].split(" ")[0]]
                    team = player[6]
                    if (team == game[1]):
                        home = 1
                    else:
                        home = 0;

                    cur.execute("select nba_id from players where dk_name = %s",(name,))
                    if(cur.rowcount == 0):
                        print("["+name+"]"+" no match")
                        noMatchingPlayers_dk.add(name)
                        continue
                    nbaId = cur.fetchall()[0][0]

                    cur.execute("select nba_abbr from teams where dk_abbr = %s",(team,) )
                    if(cur.rowcount == 0):
                        #print("["+team+"]"+" no match")
                        noMatchingTeams.add(team)
                        continue
                    nba_abbr = cur.fetchall()[0][0]
                    PG = 0;
                    if 'PG' in slots:
                        PG = 1;
                    SG = 0;
                    if 'SG' in slots:
                        SG = 1;
                    SF = 0;
                    if 'SF' in slots:
                        SF = 1;
                    PF = 0;
                    if 'PF' in slots:
                        PF = 1;
                    C = 0;
                    if 'C' in slots:
                        C = 1;
                    G = 0;
                    if 'G' in slots:
                        G = 1;
                    F = 0;
                    if 'F' in slots:
                        F = 1;
                    UTIL = 1;
                    onePlayer.extend([name,nbaId,dk_id ,salary,whichGame,home,nba_abbr,PG,SG,SF,PF,C,G,F,UTIL]);
                    players.append(onePlayer)
                count+=1
            gameSets.append(players)
            gameSets_games.append(daGames)
        doSomeUpdatesFirst = False

    if(len(noMatchingTeams) != 0):
            print("dk abbr ",noMatchingTeams)
            doSomeUpdatesFirst = True

    if(len(noMatchingPlayers_dk) != 0):
            print("dk name ",noMatchingPlayers_dk)
            doSomeUpdatesFirst = True

    cur.close()
    conn.close()

    if(doSomeUpdatesFirst):
        quit()
    #print(gameSets,games,gameSets_games)
    return (gameSets),games,gameSets_games

#print(csvTo2dList())
