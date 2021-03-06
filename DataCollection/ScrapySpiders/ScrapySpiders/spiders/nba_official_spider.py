
import scrapy
import scrapy_splash
import psycopg2
import time
import csv
import re
from ScrapySpiders.items import TeamItem, GameItem,RotoGrindersItem, CoachItem,SagarinUSAItem

class NbaTeamsSpider(scrapy.Spider):
    name = "nbaTeams"
    allowed_domains = ["www.nba.com"]
    custom_settings = {'ITEM_PIPELINES' : {'ScrapySpiders.pipelines.TeamInfoPipeline':400}}
    def start_requests(self):
        startUrl = "https://stats.nba.com/teams/"
        yield scrapy_splash.SplashRequest(url = startUrl, callback = self.parse_team, args = {'wait' : 0.5})



    def parse_team(self, response):
        xpath ='/html/body/main/div[2]/div/div[2]/div/div/div/div[2]/div[2]/div/div/div[2]/section/div/table/tbody/tr/td/a/img/@abbr'
        xpath1 = "/html/body/main/div[2]/div/div[2]/div/div/div/div[2]/div[2]/div/div/div[2]/section/div/table/tbody/tr/td/a/@href"
        teams = response.selector.xpath(xpath).extract()
        teamIds = response.selector.xpath(xpath1).extract()
        print(teams)
        print(teamIds)
        for num in range(0,len(teams)):
            entry = TeamItem()
            entry['teamAbbr'] = teams[num]
            entry['teamId'] = teamIds[num]
            yield entry 

class USAToday_sagarin_spider(scrapy.Spider):
    name = "USAToday_sagarin"
    custom_settings = {'ITEM_PIPELINES' : {'ScrapySpiders.pipelines.USAToday_sagarin_Pipeline':400}}
  
    def start_requests(self):

        startYear = 2006
        endYear = 2019 # exclude 2019
        endYear = 2019
        # 2018 - - - 2006
        
        while(startYear != endYear):
            start_url = "https://www.usatoday.com/sports/ncaaf/sagarin/"+str(startYear)+"/team/"
            startYear+=1
            time.sleep(2)
            the_request =  scrapy_splash.SplashRequest(url = start_url, callback = self.parse_year, args = {'wait' : 0.5})
            the_request.meta['year'] = startYear-1
            # start year 2016 => 2016-2017
            yield the_request

    def text_parser(self,the_string):
        bad = set()
        to_look = "\xa0"
        bad.add("<")
        bad.add("=")
        return re.findall('\xa0(.+?)[\<|\=]',the_string)
            
    def parse_year(self, response):
        the_section = "/html/body/article/div[1]/div/section/div[2]/div[2]/article/div[1]/pre[2]"

        if(response.meta['year'] == 2013):
            the_section = "/html/body/article/div[1]/div/section/div[2]/div[2]/article/div[1]/pre[3]/font/font"
      
      
        lol = response.selector.xpath(the_section).extract()
       
        print(response.meta['year'])
        print(len(lol))
        the_stuff = (self.text_parser(lol[0]))
        count = 0
        everything = list()
        for stuff in the_stuff:
            count+=1
            if(count <= 200):
               print("[  " + str(stuff) + "  ]")
            #everything.append(stuff)
            
            # each college makes up 5, the bs is 5 too, but only shows every 10
        #for one in (everything[:30]):
         #   print(one)

            
        entry = SagarinUSAItem()
        entry['theThings'] = the_stuff
        entry['year'] = response.meta['year']
        
        yield entry

            
class AJ_spider(scrapy.Spider):
    name = "college_coaches"
    #allowed_domains = ["www.sports.usatoday.com"]
    custom_settings = {'ITEM_PIPELINES' : {'ScrapySpiders.pipelines.AJ_pipeline':400}}
    counter = 0

    #-------------------------------------------#
    startUrl = "https://sports.usatoday.com/ncaa/salaries/"

        #basketball
    #startUrl = "https://sports.usatoday.com/ncaa/salaries/mens-basketball/coach/"    
    #-------------------------------------------#

    
    listofcolleges = set()
    def change_money(self,da_list):
        total = 6
        while(total!=1):
            total-=1
            da_list[-total] = int(da_list[-total].replace("--", "0").replace("$", "").replace(",",""))
        return da_list
            
    def start_requests(self):
        startUrl = "https://sports.usatoday.com/ncaa/salaries/"

        yield scrapy_splash.SplashRequest(url = startUrl, callback = self.parse_colleges, args = {'wait' : 0.5})


        # have to use css
    #  .datatable > tbody:nth-child(2) > tr:nth-child(1) > td:nth-child(2)
    # tr part iterate thru

    # starts at 1
    def return_css_lol(self,number):
        return ".datatable > tbody:nth-child(2) > tr:nth-child("+ str(number)+") > td:nth-child(2)"


    
    # this will get all the colleges to click thru
    def parse_colleges(self, response):
    #-------------------------------------------#

        startUrl = "https://sports.usatoday.com/ncaa/salaries/"

        #basketball
        #startUrl = "https://sports.usatoday.com/ncaa/salaries/mens-basketball/coach/"
    #-------------------------------------------#

        
        # next step is to simply create a dict that maps 
        all_them = "/html/body/div[6]/div[4]/div[2]/div[1]/div/div[1]/div/section/div[2]/table/tbody/tr/td[@class='']"
        lol = response.selector.xpath(all_them).extract()
        count = 0

        # click every second out of 4
        to_click = True
        for one in lol:
            count+=1
            #print(str(count)+" " + one)
            if (count % 2 == 0 and to_click):
                # request and click on button
                to_click = False
               # print(str(count)+" " + one)

            if(count % 4 == 0):
                to_click = True

        # count is now total number of colleges , I need 1-count

        #total_num = 131
        total_num = 81 #basketball
        for one in range(1,total_num):
            self.listofcolleges.add(one)
            
        while (len(self.listofcolleges) != 0):
            counter = self.listofcolleges.pop()
            button = self.return_css_lol(counter)
            time.sleep(3)
            LUA_SCRIPT = """
function main(splash)
    assert(splash:go(splash.args.url))
    local element = splash:select('%s')
    local bounds = element:bounds()
    assert(element:mouse_click{x=bounds.width/3, y=bounds.height/3})
    assert(splash:wait(5))
    return splash:html()
end
""" % (button)
            #print(button)
           # print(LUA_SCRIPT)
            SCRAPY_ARGS = {
    'lua_source': LUA_SCRIPT
}
            the_request =  scrapy_splash.SplashRequest(url = startUrl,callback = self.parse_college, endpoint = 'execute',args =  SCRAPY_ARGS)
            the_request.meta['counter'] = counter
            
            yield the_request

            
            
    # parse a college
    # need to somehow track which ones are good to go
    def parse_college(self,response):
        xpath = "/html/body/div[14]/div/div/div/div[2]/table/tbody/tr/td/text()"
        lol = response.selector.xpath(xpath).getall()
        
        college_xpath = "/html/body/div[14]/div/div/div/div[1]/div/div[2]/p[1]/text()"
        name = response.selector.xpath(college_xpath).extract()
        conf_xpath = '/html/body/div[14]/div/div/div/div[1]/div/div[2]/p[2]/text()'
        conf = response.selector.xpath(conf_xpath).extract()
        
        print(str(name) + "===================" + str(conf))
        items = CoachItem()

        items['theThings'] = list()

        current = 0
        total = 0
        one_list = list()

        one_list.append(str(response.meta['counter']))
        one_list.append(str(name)[2:-2])
        one_list.append(str(conf)[14:-2])
        for one in lol:

            current+=1
            one_list.append(str(one))
            if(current % 7 == 0):
                current = 0
                one_list = self.change_money(one_list)
                items['theThings'].append(one_list)
                one_list = list()
                one_list.append(str(response.meta['counter']))
                one_list.append(str(name)[2:-2])
                one_list.append(str(conf)[14:-2])
                total+=1
                
            # extract actual data from one 
            
        # when creating csv add college name and conference, can extract per button click
        #


        yield items

# run after AJ_spider, most likely AJ_spider will not get everything        
class AJ2_spider(scrapy.Spider):

    # one thing i may need to do is shove this into the meta part, since i think global variables miht intefere with other people
    name = "college_coaches2"
    still_need = set()

        #-----------------------------------------#

    total_teams = 131

    #basketball
    #total_teams = 81
        #-----------------------------------------#

    for i in range(1,total_teams):
        still_need.add(int(i))


        
    #-----------------------------------------#
    daname =  'USAToday_coach_salaries_football.csv'
   # daname = "USAToday_coach_salaries_basketball.csv"
    #-----------------------------------------#

    reader = csv.reader(open(daname,newline=''),delimiter = ',',)
        
    ignore_first = True

    print(still_need)
    for row in reader:
        if(ignore_first):
            ignore_first=False
            continue
        print("do not need this " + row[0])
        still_need.discard( int(row[0]) )
    
        
    #allowed_domains = ["www.sports.usatoday.com"]
    custom_settings = {'ITEM_PIPELINES' : {'ScrapySpiders.pipelines.AJ2_pipeline':400}}
    counter = 0

    THE_URL = "https://sports.usatoday.com/ncaa/salaries/"
    
    
    listofcolleges = set()

    def change_money(self,da_list):
        total = 6
        while(total!=1):
            total-=1
            da_list[-total] = int(da_list[-total].replace("--", "0").replace("$", "").replace(",",""))
        return da_list
    
    def start_requests(self):
        if(len(self.still_need) == 0):
            print("All good I'm done")
            quit()

            #-----------------------------------------#

        startUrl = "https://sports.usatoday.com/ncaa/salaries/"

        #basketball
        #startUrl = "https://sports.usatoday.com/ncaa/salaries/mens-basketball/coach/"
            #-----------------------------------------#

        yield scrapy_splash.SplashRequest(url = startUrl, callback = self.parse_colleges, args = {'wait' : 0.5})


        # have to use css
    #  .datatable > tbody:nth-child(2) > tr:nth-child(1) > td:nth-child(2)
    # tr part iterate thru

    # starts at 1
    def return_css_lol(self,number):
   
       # return ".datatable > tbody:nth-child(2) > tr:nth-child("+ str(number)+") > td:nth-child(2) >"
        return ".datatable > tbody:nth-child(2) > tr:nth-child("+str(number)+") > td:nth-child(2) > a:nth-child(1)"
    
    # this will get all the colleges to click thru
    def parse_colleges(self, response):

        #-----------------------------------------#

        startUrl = "https://sports.usatoday.com/ncaa/salaries/"

        #basketball
        #startUrl = "https://sports.usatoday.com/ncaa/salaries/mens-basketball/coach/"
    #-----------------------------------------#

        # next step is to simply create a dict that maps 
        all_them = "/html/body/div[6]/div[4]/div[2]/div[1]/div/div[1]/div/section/div[2]/table/tbody/tr/td[@class='']"
        lol = response.selector.xpath(all_them).extract()
        count = 0

        # click every second out of 4
        to_click = True
        for one in lol:
            count+=1
            #print(str(count)+" " + one)
            if (count % 2 == 0 and to_click):
                # request and click on button
                to_click = False
               # print(str(count)+" " + one)

            if(count % 4 == 0):
                to_click = True

        # count is now total number of colleges , I need 1-count

        
        
    
            
        while (len(self.still_need) != 0):
            counter = self.still_need.pop()
            print("Still need "+ str(counter))
            button = self.return_css_lol(counter)
            time.sleep(3)
            LUA_SCRIPT = """
function main(splash)
    assert(splash:go(splash.args.url))
    local element = splash:select('%s')
    local bounds = element:bounds()
    assert(element:mouse_click{x=bounds.width/3, y=bounds.height/3})
    assert(splash:wait(5))
    return splash:html()
end
""" % (button)
            #print(button)
           # print(LUA_SCRIPT)
            SCRAPY_ARGS = {
    'lua_source': LUA_SCRIPT
}
            the_request =  scrapy_splash.SplashRequest(url = startUrl,callback = self.parse_college, endpoint = 'execute',args =  SCRAPY_ARGS)
            the_request.meta['counter'] = counter
            
            yield the_request

            
            
    # parse a college
    # need to somehow track which ones are good to go
    def parse_college(self,response):
        xpath = "/html/body/div[14]/div/div/div/div[2]/table/tbody/tr/td/text()"
        lol = response.selector.xpath(xpath).getall()
        
        college_xpath = "/html/body/div[14]/div/div/div/div[1]/div/div[2]/p[1]/text()"
        name = response.selector.xpath(college_xpath).extract()
        conf_xpath = '/html/body/div[14]/div/div/div/div[1]/div/div[2]/p[2]/text()'
        conf = response.selector.xpath(conf_xpath).extract()
        
        print(str(name) + "===================" + str(conf))
        items = CoachItem()

        items['theThings'] = list()

        current = 0
        total = 0
        one_list = list()
        self.counter+=1

        one_list.append(str(response.meta['counter']))
        one_list.append(str(name)[2:-2])
        one_list.append(str(conf)[14:-2])
        for one in lol:

            current+=1
            one_list.append(str(one))
            if(current % 7 == 0):
                current = 0
                one_list = self.change_money(one_list)
                items['theThings'].append(one_list)
                one_list = list()
                one_list.append(str(response.meta['counter']))
                one_list.append(str(name)[2:-2])
                one_list.append(str(conf)[14:-2])
                total+=1
                
            # extract actual data from one 
            
        # when creating csv add college name and conference, can extract per button click
        #


        yield items
                
# todo
# save rotogrinders predicted values into game_statlines
# 
class RotogrindersSpider(scrapy.Spider):
    name = "rg_predictions"
    allowed_domains = ["www.rotogrinders.com"]
    custom_settings = {'ITEM_PIPELINES' : {'ScrapySpiders.pipelines.RotoGrindersPipeline':400}}
    def start_requests(self):
        startUrl = "https://rotogrinders.com/projected-stats/nba-player?site=draftkings"
        yield scrapy_splash.SplashRequest(url = startUrl, callback = self.parse_team, args = {'wait' : 0.5})

    def parse_team(self, response):
       # xpath =" /html/body/div[1]/div/section/div/section/div[2]/section/div/div[1]/div/div[2]/div[1]/div[contains(@class,'player')])"
        xpath ="/html/body/div[1]/div/section/div/section/div[2]/section/div/div[1]/div/div[2]/div[1]/div[@class='player']/a[@class='player-popup']/text()"

        xpath2 = "/html/body/div[1]/div/section/div/section/div[2]/section/div/div[3]/div/div[2]/div[3]/div/text()"
        xpath3 = "/html/body/div[1]/div/section/div/section/div[2]/section/div/div[3]/div/div[2]/div[2]/div/text()"
        xpath4 = "/html/body/div[1]/div/section/div/section/div[2]/section/div/div[3]/div/div[2]/div[4]/div/text()"
        xpath5 =  "/html/body/div[1]/div/section/div/section/div[2]/section/div/div[2]/div[1]/div[2]/div[1]/div/text()"

        
        players = response.selector.xpath(xpath).extract()
        floor = response.selector.xpath(xpath2).extract()
        floor = floor[1:]
        ceiling = response.selector.xpath(xpath3).extract()
        ceiling = ceiling[1:]
        predicted = response.selector.xpath(xpath4).extract()
        predicted = predicted[1:]
        teams = response.selector.xpath(xpath5).extract()
        teams = teams[1:]
        print((players))
        print(floor)
        print(ceiling)
        print(predicted)
        print(teams)
        
        for idx,player in enumerate(players):
            # does not work for 100 fp predicitons atm
            entry = RotoGrindersItem()
            entry['name'] = players[idx]
            entry['floor'] = int(float(floor[idx])*100)
            entry['ceiling'] = int(float(ceiling[idx])*100)
            entry['predicted'] = int(float(predicted[idx])*100)
            entry['team'] = teams[idx]
            yield entry
            
            
class NbaTeamSpider(scrapy.Spider):
    name = "nbaTeam"
    allowed_domains = ["www.nba.com"]
    custom_settings = {'ITEM_PIPELINES':{'ScrapySpiders.pipelines.TeamGamesPipeline' :400}}
    def start_requests(self):
        startUrl = "https://stats.nba.com/stats/teamgamelog?Season=2017-18&SeasonType=Regular+Season&TeamID=1610612738"
        years = set(["2017-18", "2016-17", "2015-16", "2014-15",])
        types = set(["Regular+Season", "Playoffs", "Preseason"])        
        
        conn = psycopg2.connect("dbname=basketball user = nd2")
        cur = conn.cursor()
        cur.execute("select nba_id from teams;")
        listOfIds = cur.fetchall()
        cur.close()
        conn.close()
        for year in years:
            for type in types:                
                for id in listOfIds:
                    print("lol")
                    yield scrapy_splash.SplashRequest(url = startUrl, callback = self.parse_games)


    def parse_games(self,response):
           print("haha")
           yield 
 
class OpenloadVideoSpider(scrapy.Spider):
    name = "OpenloadVideo"
    custom_settings = {'ITEM_PIPELINES' : {'scrapy.pipelines.files.FilesPipeline' : 1},'FILES_STORE' : '~/Documents/Creations/StudentOfTheGame/DataCollection/NbaFullGames' }

    def start_requests(self):
        startUrl = "https://openload.co/f/X5MFN93Dh2E/НБА.ГСВ-Клив.Флудилка_Групп.31.05.2018.Виасат.50fps.RU-EN.mkv"
        yield scrapy_splash.SplashRequest(url = startUrl, callback = self.parse_download, args = {'wait' : 0.5})
    
    def parse_download(self,response):
       pass  
