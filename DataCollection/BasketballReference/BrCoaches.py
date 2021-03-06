import requests
import psycopg2
from lxml.html import fromstring
import sys

# have to copy nba_abbr to br_abbr
# update teams set br_abbr = nba_abbr
# phx = pho
# bkn = brk
#cha = cho

url ="https://www.basketball-reference.com/coaches/NBA_stats.html"

resp = requests.get(url, headers = {'User-Agent' :  'Mozilla/5.0 (X11; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0'} )
source = fromstring(resp.content)

items= source.xpath("//tbody/tr/td[@class='left ']/a")

conn = psycopg2.connect("dbname=basketball user = nd2")
cur = conn.cursor()


for coach in items:
    name = coach.text
    if name is None:
        name = coach.xpath("strong/text()")[0]
    htmlCoach = coach.attrib['href']
   # print(str(name))
    #print("-----")
    #print(htmlCoach)
    cur.execute("insert into coaches (name,br_link) values (%s,%s) on conflict (name) do update set br_link = %s",(name,htmlCoach,htmlCoach))
    conn.commit()


years = ['2015','2016','2017','2018','2019']

cur.execute("select br_abbr,nba_abbr from teams")
teams = cur.fetchall()
print(teams)

if (sys.argv[1] == "update"):
    years = ['2019']

for team in teams:
    for year in years:
        url =  "https://www.basketball-reference.com/teams/"+team[0] +"/"+year +".html"
        resp = requests.get(url, headers = {'User-Agent' :  'Mozilla/5.0 (X11; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0'} )
        source = fromstring(resp.content)
        coaches = source.xpath("//div[1]/div[2]/p[contains(strong,'Coach')]/a/text()")
        records = source.xpath("//div[1]/div[2]/p[contains(strong,'Coach')]/text()")
        counts = list()
        for record in records:
            number = str(record)
            if "-" in number:
                number = number.replace(" ","")
                number = number.replace("(","")
                number = number.replace(")","")
                number = number.replace(",","")
                numbers = number.split('-')
                ws = numbers[0]
                ls = numbers[1]
                games = int(ws)+int(ls)
                counts.append(games)
        #for count in counts
        offset = 0
        for coach in range(0,len(coaches)):
            name = coaches[coach]
            games = counts[coach]
            teamAbbr = team[1]
            start = str(int(year)-1)+"-10-01"
            end = year+"-07-01"
            print(offset)
            print(games)
           
            cur.execute("update games set home_coach = %s where date_of_game in (select date_of_game from games where (home = %s or away = %s) and (date_of_game >= %s and date_of_game <= %s) and type = 'Regular Season' order by date_of_game asc offset %s limit %s) and home = %s",(name,teamAbbr,teamAbbr,start,end,offset,games,teamAbbr))
            cur.execute("update games set away_coach = %s where date_of_game in (select date_of_game from games where (home = %s or away = %s) and (date_of_game >= %s and date_of_game <= %s) and type = 'Regular Season' order by date_of_game asc offset %s limit %s) and away= %s",(name,teamAbbr,teamAbbr,start,end,offset,games,teamAbbr))
            conn.commit()
            offset = offset + games
            print(start)
            print(end)
            print(teamAbbr)
            print(name)
            
           



cur.close()
conn.close()
