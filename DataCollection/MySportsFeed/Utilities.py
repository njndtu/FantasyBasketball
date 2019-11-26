import base64
import requests
import pdftotext
import io
import json
import time as sleeper

def send_request(urlToPass,params):
    # Request

    try:
        print("start")
        response = requests.get(
            url=urlToPass,
            headers={
                "Authorization": "Basic " +
                base64.b64encode('{}:{}'.format("173c8b69-56ae-4b05-8176-f7b789","MYSPORTSFEEDS").encode('utf-8')).decode('ascii')
            }, params = params )
        print('Response HTTP Status Code: {status_code}'.format(
            status_code=response.status_code))
        print(response.url)
        return response
    except requests.exceptions.RequestException:
        print('HTTP Request failed')
        
def salaryFiller(year,date,cur,conn,gameCache,playerCache,manualAdds):
    dateF = date[0].strftime("%Y%m%d")
    url  = "https://api.mysportsfeeds.com/v2.0/pull/nba/"+year+"/date/"+dateF+"/dfs.json"
    sleeper.sleep(0.5)
    params = dict()
    resp = send_request(url,params)
    sleeper.sleep(6)
    jsonFile = json.loads(resp.text)
    
    try:
        sources = jsonFile['dfsEntries']
    except KeyError:
        return
    fdExists = False
    dkExists = False
    fdIndex = 0
    dkIndex = 0
    for index in range(0,len(sources)):
        if (sources[index]['dfsSource'] == "DraftKings"):
            dkExists = True
            dkIndex = index
        if (sources[index]['dfsSource'] == "FanDuel"):
            fdExists = True
            fdIndex = index


    if(dkExists):
        salariesDK = jsonFile['dfsEntries'][dkIndex]['dfsRows']
        for entry in salariesDK:
            msfId = entry['player']['id']
            jersey = entry['player']['jerseyNumber']
            name = entry['player']['firstName'] +" " + entry['player']['lastName']
            idDK = entry['dfsSourceId']
            salaryDK = entry['salary']
            team = entry['team']['abbreviation']
            abbr = msfToNbaAbbr(team,cur)
            try:
                gameId = dateAndTeamToGame(date,abbr,cur)
            except IndexError:
                break
            try:
                nbaId = msfToNbaId(msfId,cur)
            except IndexError:
                print(msfId)
                try:
                    nbaId = nameToNbaId(name,cur)
                except IndexError:
                    if name not in manualAdds:
                        manualAdds.append(name)
            if(msfId not in playerCache[0]):
               # cur.execute("update players set dk_id = %s where nba_id = %s",(idDK,nbaId))
            #conn.commit()
                playerCache[0].add(msfId)
            try:
                gameMsfId = entry['game']['id']
                if(gameMsfId not in gameCache):
                    cur.execute("update games set msf_id = %s where date_of_game = %s and (home = %s or away = %s)",(gameMsfId,date,abbr,abbr))
                    conn.commit()
                    gameCache.add(gameMsfId)
            except KeyError:
                print(str(gameId) +"not available")

                cur.execute("update game_statlines set jersey = %s,salary_dk = %s where game_id = %s and player_id = %s",(jersey, salaryDK,gameId,nbaId))
            conn.commit()
    if(fdExists):    
        salariesFD = jsonFile['dfsEntries'][fdIndex]['dfsRows']
        for entry in salariesFD:
            msfId = entry['player']['id']
            name = entry['player']['firstName'] +" " + entry['player']['lastName']
            jersey = entry['player']['jerseyNumber']
            idFD = entry['dfsSourceId']
            salaryFD = entry['salary']
            team = entry['team']['abbreviation']
            try:
                nbaId = msfToNbaId(msfId,cur)
            except IndexError:
                print(msfId)
                try:
                    nbaId = nameToNbaId(name,cur)
                except IndexError:
                    if name not in manualAdds:
                        manualAdds.append(name)
            abbr = msfToNbaAbbr(team,cur)
            try:
                gameId = dateAndTeamToGame(date,abbr,cur)
            except IndexError:
                break
            if(msfId not in playerCache[1]):
               # cur.execute("update players set fd_id = %s where nba_id = %s",(idFD,nbaId))
                #conn.commit()
                playerCache[1].add(msfId)

            cur.execute("update game_statlines set jersey = %s,salary_fd = %s where game_id = %s and player_id = %s",(jersey, salaryFD,gameId,nbaId))

            conn.commit()

def msfToNbaId(msfId,cur):
    cur.execute("select nba_id from players where msf_id = "+ str(msfId))
    nbaId = cur.fetchall()[0][0]
    return nbaId                
def nameToNbaId(name,cur):
    cur.execute("select nba_id from players where nba_name = %s or %s = any(other_names) ",(name,name))
    print(name)
    nbaId = cur.fetchall()[0][0]
    return nbaId

def dateAndTeamToGame(date,team,cur):
    cur.execute("select nba_id from games where date_of_game = %s and (home = %s or away = %s)",(date,team,team))
    gameId = cur.fetchall()[0][0]
    return gameId

def msfToNbaAbbr(abbr,cur):
    cur.execute("select nba_abbr from teams where msf_abbr = %s",(abbr,))
    nbaAbbr = cur.fetchall()[0][0]
    return nbaAbbr
