from Utilities import send_request
import json
import psycopg2


url = "https://api.mysportsfeeds.com/v2.0/pull/nba/players.json"
params = dict()
resp = send_request(url,params)
jsonFile = json.loads(resp.text)
players = jsonFile['players']
conn = psycopg2.connect("dbname=basketball user = nd2")
cur = conn.cursor()

for player in players:
    playerInfo = player['player']
    playerId = playerInfo['id']
    name = playerInfo['firstName'] + " " + playerInfo['lastName']
    print(name)
    birthdate = playerInfo['birthDate']
    city = playerInfo['birthCity']
    country = playerInfo['birthCountry']
    twitter = ""
    if (playerInfo['socialMediaAccounts']):
        twitter = playerInfo['socialMediaAccounts'][0]['value']
    handness = False
    if playerInfo['handedness']['shoots'] == "L":
        handness = True
    draftTeam = ""    
    if playerInfo['drafted']:
        draftTeam = playerInfo['drafted']['team']['abbreviation']
    if playerInfo['externalMappings']:
        nbaId = playerInfo['externalMappings'][0]['id']

        if(twitter == ""):
             cur.execute("update players set msf_id = %s, msf_name = %s, bday = %s, birth_city = %s, birth_country = %s,  shooting_hand = %s, draft_team = %s where nba_id = %s", (playerId,name,birthdate, city,country,handness,draftTeam,nbaId))
        else:
            cur.execute("update players set msf_id = %s, msf_name = %s, bday = %s, birth_city = %s, birth_country = %s, twitter = %s, shooting_hand = %s, draft_team = %s where nba_id = %s", (playerId,name,birthdate, city,country,twitter,handness,draftTeam,nbaId))
    else:
        if(twitter == ""):
            cur.execute("update players set msf_id = %s, msf_name = %s, bday = %s, birth_city = %s, birth_country = %s,  shooting_hand = %s, draft_team = %s where nba_name = %s", (playerId,name,birthdate, city,country,handness,draftTeam,name))
        else:
            cur.execute("update players set msf_id = %s, msf_name = %s, bday = %s, birth_city = %s, birth_country = %s, twitter = %s, shooting_hand = %s, draft_team = %s where nba_name = %s", (playerId,name,birthdate, city,country,twitter,handness,draftTeam,name))
    conn.commit()
        
cur.close()
conn.close()
