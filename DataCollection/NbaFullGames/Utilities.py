import requests
import json
import psycopg2
import time as sleeper


# returns list of YYYY-YYYY, starting with currentYear-1 - currentYear
def yearsGenerator(currentYear, yearsBack):
    endYear = list()
    for year in range(0,yearsBack):
        endYear.append(currentYear - year)
    yearStrings = list()
    for year in endYear:
        yearString = "20"+str(year - 1)+"-"+str(year)
        yearStrings.append(yearString)
    return yearStrings



def gameStatLineParser(game,type,cur,conn,logging):    
    gameId = "00"+str(game[0])
    url = "https://stats.nba.com/stats/"+str(type)+"?EndPeriod=14&EndRange=50000&GameID="+gameId+"&RangeType=0&StartPeriod=0&StartRange=0"
    #print(url)
    try:
        resp = requests.get(url = url, headers = {'User-Agent' :'Mozilla/5.0 (X11; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0'},timeout = 20)
    except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
        logging.warning(url)
        return 
    data = resp.text
    jsonFile = json.loads(data)


    if(type == "boxscoresummaryv2"):
        refs = jsonFile['resultSets'][2]['rowSet']
        refIds = list()
        for ref in refs:
            refId = ref[0]
            firstName = ref[1]
            lastName = ref[2]
            jersey = ref[3]
            if (len(jersey.split()) == 0):
                jersey = 7777
            refIds.append(refId)
            cur.execute("insert into officials (nba_id,first_name,last_name,jersey_num) values (%s,%s,%s,%s) on conflict (nba_id) do update set first_name = %s, last_name = %s, jersey_num = %s",(refId, firstName,lastName,jersey,firstName,lastName,jersey))
            conn.commit()

        attendence = jsonFile['resultSets'][4]['rowSet'][0][1]
        cur.execute("update games set refs = %s, attendence = %s where nba_id = %s",(refIds,attendence,int(gameId)))
        inactives = jsonFile['resultSets'][3]['rowSet']
        for inactive in inactives:
            playerId = inactive[0]
            teamId = inactive[4]
            cur.execute("insert into game_statlines (game_id,player_id,team_id,was_active) values (%s,%s,%s,%s) on conflict on constraint game_statlines_pkey do update set team_id = %s,was_active = %s",(gameId, playerId,teamId, False, teamId,False))
            conn.commit()

    if(type == "boxscoretraditionalv2"):
        players = jsonFile['resultSets'][0]['rowSet']
        for player in players:
            teamId = player[1]
            playerId = player[4]
            #seconds
            duration = 0
            status = ""
            wasActive = False
            if(player[8] is not None):
                time = str(player[8]).split(':')
                if(len(time) == 1 and time[0]):
                    duration += int(time[0]) * 60
                else:
                    duration += int(time[0]) * 60 + int(time[1])
                wasActive = True
            else:
                status = player[7]
            if duration == 0:
                wasActive = False
            fgm = player[9]
            fga = player[10]
            threepm = player[12]
            threepa = player[13]
            ftm = player[15]
            fta = player[16]
            oreb = player[18]
            dreb = player[19]
            ast = player[21]
            tos = player[24]
            stl = player[22]
            blk = player[23]
            pf = player[25]
            plusMinus = player[27]
            cur.execute("insert into game_statlines (game_id,player_id,team_id,was_active,status,duration,fgm,fga,threepm,threepa,ftm,fta,oreb,dreb,ast,tos,stl,blk,pf,plus_minus) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) on conflict on constraint game_statlines_pkey do update set team_id = %s,was_active = %s,status=%s, duration = %s, fgm = %s,fga = %s, threepm = %s, threepa = %s, ftm = %s, fta = %s, oreb = %s, dreb = %s, ast = %s, tos = %s, stl = %s, blk = %s, pf = %s, plus_minus = %s",(gameId,playerId,teamId,wasActive,status,duration,fgm,fga,threepm,threepa,ftm,fta,oreb,dreb,ast,tos,stl,blk,pf,plusMinus,teamId,wasActive,status,duration,fgm,fga,threepm,threepa,ftm,fta,oreb,dreb,ast,tos,stl,blk,pf,plusMinus))
            conn.commit()

    if(type == "boxscoreadvancedlv2"):
        players = jsonFile['resultSets'][0]['rowSet']
        for player in players:
            playerId = player[4]
            pace = player[22]
            cur.execute("insert into games (game_id,player_id,pace) values (%s,%s,%s) on conflict on constraint game_statlines_pkey do update set pace = %s",(gameId, playerId,pace,pace))
            conn.commit()

    if(type == "boxscoremiscv2"):
        players = jsonFile['resultSets'][0]['rowSet']
        for player in players:
            playerId = player[4]
            poto = player[9]
            scp = player[10]
            fbp = player[11]
            pitp = player[12]
            blka = player[18]
            pfd = player[20]
            cur.execute("insert into game_statlines (game_id,player_id,poto,scp,fbp,pitp,blka,pfd) values (%s,%s,%s,%s,%s,%s,%s,%s) on conflict on constraint game_statlines_pkey do update set poto = %s,scp = %s,fbp = %s,pitp = %s, blka = %s, pfd = %s",(gameId,playerId,poto,scp,fbp,pitp,blka,pfd,poto,scp,fbp,pitp,blka,pfd))
    if(type == "boxscorescoringv2"):
        players = jsonFile['resultSets'][0]['rowSet']
        for player in players:
            playerId = player[4]
            if (player[18] is not None):
                twoMadeAst = player[18]
                twoMadeUast = player[19]
                threeMadeAst = player[20]
                threeMadeUast = player[21]
                cur.execute("insert into game_statlines (game_id,player_id, two_made_ast,two_made_uast,three_made_ast,three_made_uast) values (%s,%s,%s,%s,%s,%s) on conflict on constraint game_statlines_pkey do update set two_made_ast = %s, two_made_uast = %s, three_made_ast = %s, three_made_uast = %s",(gameId,playerId,twoMadeAst,twoMadeUast,threeMadeAst,threeMadeUast,twoMadeAst,twoMadeUast,threeMadeAst,threeMadeUast))
                conn.commit()

    if(type == "boxscoreusagev2"):
        players = jsonFile['resultSets'][0]['rowSet']
        for player in players:
            playerId = player[4]
            usage = player[9]
            cur.execute("insert into game_statlines (game_id,player_id,usage) values (%s,%s,%s) on conflict on constraint game_statlines_pkey do update set usage = %s", (gameId,playerId,usage,usage))

    if(type == "boxscoreplayertrackv2"):
        players = jsonFile['resultSets'][0]['rowSet']
        for player in players:
            playerId = player[4]
            speed = player[9]
            distance = player[10]
            touches = player[14]
            passes = player[17]
            dfgm = player[26]
            dfga = player[27]
            orbc = player[11]
            drbc = player[12]
            contestedFgm = player[19]
            contestedFga = player[20]
            uncontestedFgm = player[22]
            uncontestedFga = player[23]
            cur.execute("insert into game_statlines (game_id, player_id, distance,speed,touches,passes,dfgm,dfga,orbc,drbc,contested_fgm,contested_fga, uncontested_fgm, uncontested_fga) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) on conflict on constraint game_statlines_pkey do update set distance = %s, speed = %s, touches = %s, passes = %s, dfgm = %s,dfga = %s, orbc = %s,drbc = %s, contested_fgm = %s, contested_fga = %s, uncontested_fgm = %s, uncontested_fga = %s", (gameId,playerId,distance,speed ,touches,passes,dfgm,dfga,orbc,drbc,contestedFgm,contestedFga,uncontestedFgm,uncontestedFga,distance,speed,touches,passes,dfgm,dfga,orbc,drbc,contestedFgm,contestedFga,uncontestedFgm,uncontestedFga))
            conn.commit()

    if(type == "hustlestatsboxscore"):
        players = jsonFile['resultSets'][1]['rowSet']
        for player in players:
            playerId = player[4]
            if(playerId != ""):
                screenAssists = player[15]
                deflections = player[12]
                looseballRecovered = player[13]
                chargesDrawn = player[14]
                twosContested = player[10]
                threesContested = player[11]
                cur.execute("insert into game_statlines (game_id,player_id,screen_assists,deflections,looseball_recovered,charges_drawn,twos_contested,threes_contested) values (%s,%s,%s,%s,%s,%s,%s,%s) on conflict on constraint game_statlines_pkey do update set screen_assists = %s, deflections = %s, looseball_recovered = %s, charges_drawn = %s, twos_contested = %s, threes_contested = %s", (gameId,playerId,screenAssists,deflections,looseballRecovered,chargesDrawn, twosContested,threesContested,screenAssists,deflections,looseballRecovered,chargesDrawn, twosContested,threesContested ))
                conn.commit()

        #everything gathered from matchups 
    if(type == "boxscorematchups"):
        matchups = jsonFile['resultSets'][0]['rowSet'] 
        for matchup in matchups:
            offPlayerId = matchup[5]
            defPlayerId = matchup[11]
            poss = matchup[13]
            ast = matchup[17]
            tov = matchup[18]
            blk = matchup[19]
            fgm = matchup[22]
            fga = matchup[23]
            threepm = matchup[25]
            threepa = matchup[26]
            ftm = matchup[28]
            shootingf = matchup[29]
            deff = matchup[30]
            offf = matchup[31]
            if(defPlayerId is not None):
                cur.execute("insert into matchups (game_id,off_player,def_player,poss,ast,tov,blk,fgm,fga,threepm,threepa,ftm,shooting_foul,def_foul,off_foul) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) on conflict on constraint matchups_pkey do update set poss = %s, ast = %s, tov = %s,blk = %s, fgm = %s, fga = %s, threepm = %s, threepa = %s, ftm = %s, shooting_foul = %s, def_foul = %s, off_foul = %s",(gameId, offPlayerId,defPlayerId, poss,ast,tov,blk,fgm,fga,threepm,threepa,ftm,shootingf,deff,offf,poss,ast,tov,blk,fgm,fga,threepm,threepa,ftm,shootingf,deff,offf))
                conn.commit()

