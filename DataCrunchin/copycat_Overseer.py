# this will implement the paper's way
import psycopg2
import cvxpy as cp
import numpy as np
from DK_csvParser_classic import csvTo2dList
from DK_lineup_writer import write_it
import sys 

# blacklist here should be lowercased.
def copycat(totalToSpit,name_of_csv,blacklist):

    # get parsed info from donwloaded csv file from draftkings
    csvParsed = csvTo2dList()

    conn = psycopg2.connect("dbname=basketball user = nd2")
    cur = conn.cursor()
    # [0] the gameSets [1] game decoding [2] the games

    # link each player in the gamesets to an entry in 
    cur.execute("select * from rotogrinders_predictions")
    rg_predictions = cur.fetchall()
    # now I have the entire matrix
    rg_predictions_list = list()
    # name lower,upper,predicted team
    for player in rg_predictions:
        aPlayer = list()
        aPlayer.extend(list(player))
        aPlayer.append(False)
        rg_predictions_list.append(aPlayer)


    # rg_predcitions_list 
    noMatchingPlayers_rg = set()
    noMatchingTeams = set()

    heuristics = dict()

    for player in rg_predictions_list:
        cur.execute("select nba_id from players where rg_name = %s",(player[0],))
        if(cur.rowcount == 0):
            noMatchingPlayers_rg.add(player[0])
        else:
            player[0] = cur.fetchall()[0][0]
        cur.execute("select nba_abbr from teams where rg_abbr = %s",(player[4],))
        if(cur.rowcount == 0):
            noMatchingTeams.add(player[4])
        else:
            player[4] = cur.fetchall()[0][0]
        heuristics[player[0]] = player[1:4]
    # player : id,floor,ceiling,predicted,team   linked 




    # check to see if i need to manually change
    doSomeUpdatesFirst = False
    if(len(noMatchingTeams) != 0):
        print("rg abbr ",noMatchingTeams)
        doSomeUpdatesFirst = True
    if(len(noMatchingPlayers_rg) != 0):
        print("rg_name ",noMatchingPlayers_rg)
        doSomeUpdatesFirst = True
    if(doSomeUpdatesFirst):
        quit()



    # specify which game set to run
    for gameSet in csvParsed[0]:
        for player in gameSet:
            if(player[1] in heuristics):
                player.extend(heuristics[player[1]])
            else:
                # if player "injured" I will put 0 as predicted value
                player.extend([0,0,0])



    # change next time    
    players = csvParsed[0][0]
    # create dupe items to account for positions
    players2 = list()
    numOfPlayersOrig = 0

    game_count = len(csvParsed[1])


    for player in players:
        if(player[17] == 0):
            # I essentially do not factor in those without a prediction
            continue
        if(player[0].lower in blacklist):
            # blacklist will be players not to be used
            continue
        # add in the team and game variables here, I already know which game they belong to, and if home or not, so matrix will be [a1,h1,a2,h2 . . . a2,hn], n games, h is home a is away, I can get the total games and teams corresponding to each game number from the return items of csv parser
        game_num = int(player[4])
        is_home = int(player[5])

        numOfPlayersOrig += 1
        for slot in range(7,15):
            if (player[slot] == 1):
                team_affiliation = [0] * (game_count * 2)
                team_affiliation[(game_num * 2) + is_home ] = 1
                dupe = player.copy()
                dupe[7:15] = [0,0,0,0,0,0,0,0]
                dupe[slot] = 1
                dupe.extend(team_affiliation)
                players2.append(dupe)

    players2 = np.array(players2)


    # I think I might just create a copy of a player for each "slot" it can take

    numOfPlayers = players2.shape[0]

    print("available players : ", numOfPlayersOrig)
    print("available games : ", game_count)

    ##########################################################################
    # Start of LP formation
    ##########################################################################


    # X is the variables to solve
    X = cp.Variable((numOfPlayers,1), integer=True)
    X_lower = cp.Parameter((numOfPlayers,1))
    X_upper = cp.Parameter((numOfPlayers,1))
    X_lower.value = np.zeros((numOfPlayers,1),dtype = int)
    X_upper.value = np.ones((numOfPlayers,1),dtype = int)

    # let A be the heursitcs matrix.
    A = cp.Parameter((numOfPlayers,1))

    # 15, floor   16, ceiling     17 , predicted
    A.value = np.reshape(np.asarray(players2[:,17],dtype = int),(numOfPlayers,1))

    # C be the salary cost matrix
    C = cp.Parameter((numOfPlayers,1))
    C.value = np.reshape(np.asarray(players2[:,3],dtype = int),(numOfPlayers,1))

    # P be the position matrix

    P = cp.Parameter((numOfPlayers,8))
    P.value = np.reshape(np.asarray(players2[:,7:15],dtype = int),(numOfPlayers,8))
    PS = cp.Parameter((8,1))
    PS.value = np.ones((8,1), dtype = int)

    # D be the dupe player matrix, 8n is upperbound, D will look like a staircase of 1's, at each lvl the number of 1's correspond to number of dupes 

    DS = cp.Parameter((numOfPlayersOrig,1))
    DS.value = np.ones((numOfPlayersOrig,1),dtype = int)
    D = cp.Parameter((numOfPlayersOrig,numOfPlayers))
    D.value = np.zeros((numOfPlayersOrig,numOfPlayers),dtype = int)

    # L be the constraint that no two lineups are the same
    # I add to L everytime
    # L is simply a previous X, L.T @ X <= 7, L (8n X 20)

    # soft limit is 20 now, because if I use 150 it will blow up
    soft_limit = 150
    totalToSpit_copy= totalToSpit
    if(totalToSpit > soft_limit):
        totalToSpit = soft_limit
    L = cp.Parameter((numOfPlayers,totalToSpit))
    L.value = np.zeros((numOfPlayers,totalToSpit),dtype = int)
    totalToSpit = totalToSpit_copy

    # T be the team constraints, has to have players from this amount of teams
    # a (# teams x numOfPlayers) matrix
    # Tc.T@X <= (max players u wanna get from a team)
    Tc = cp.Parameter((numOfPlayers,game_count*2))
    Tc.value = np.reshape(np.asarray(players2[:,18:(18+(game_count*2))],dtype = int),((numOfPlayers,game_count*2)))

    # G be the game constraints, dk rules at least two games
    # upperbound on number of players from a game
    G = cp.Parameter((game_count,game_count*2))
    G.value = np.zeros((game_count,game_count*2),dtype = int)
    for game in range(0,game_count):
        row = game
        column = (row*2)
        G.value[row,column] = 1
        G.value[row,column+1] = 1


    # objective function : max( sum(AX) )
    obj = cp.Maximize(A.T@X)
    T = cp.Parameter(())

    playerCount = 0
    dupeCount = 0
    first = True
    current = players2[0,0]
    for player in players2:
        if(player[0] == current):
            D.value[playerCount,dupeCount] = 1
            dupeCount+=1
        else:
            current = player[0]
            playerCount+=1
            D.value[playerCount,dupeCount] = 1
            dupeCount+=1

    # base constraints
    constraints = [X >= 0, X <= 1, C.T@X <= 50000, P.T@X == PS, D@X <= DS, L.T@X <= 6, Tc.T@X <= 2, G@(Tc.T@X) <= 7]


    ##########################################################################
    # End of LP formation, start iterating thru 
    ##########################################################################

    # I am going to iteratively generate lineups, after each iteration I need to slap on the additional lineup uniqueness constraint

    all_lineups = list()
    at = 0

    for once in range(0,totalToSpit):

        prob = cp.Problem(obj,constraints)
        print("is dcp ", prob.is_dcp())

        prob.solve()

    #  print("status ", prob.status)
    # print("optimal ", prob.value)
        #print("da optimal", X.value)

        # create iterator for final
        final = (np.round(X.value))
        it = np.nditer(final,flags=["c_index"])


        oneLineup= [None] * 8
        playersUsed = list()

        while not it.finished:
            if(it[0] == 1):
                pos = np.array(players2[it.index,7:15],dtype = int)@np.array((0,1,2,3,4,5,6,7))
                oneLineup[pos] = players2[it.index,0]+" ("+(players2[it.index,2])+")"
                playersUsed.append(players2[it.index,0])
            it.iternext()

        # change L[:,once]
        for player in range(0,players2.shape[0]):
            if(players2[player,0] in playersUsed):
                L.value[player,once] = 1

        all_lineups.append(oneLineup)
        at += 1
        print(str(at)+" lineups created . . .  . .. . . ")



    write_it(all_lineups,name_of_csv)
