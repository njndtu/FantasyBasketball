# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import psycopg2
import csv


class TeamInfoPipeline(object):
  
    def process_item(self, item, spider):
            # need to parse teamId, get rid of the /team/ . . . / or do i parse in the pipeline
            item['teamId'] = item['teamId'].replace("/","")[4:]
            self.cur.execute("insert into teams (nba_abbr,msf_abbr,dk_abbr,rg_abbr, nba_id) values (%s,%s) on conflict (nba_abbr) do update set nba_abbr = %s, nba_id =%s",(item['teamAbbr'],item['teamAbbr'],item['teamAbbr'],item['teamAbbr'],item['teamId'],item['teamAbbr'],item['teamId']))
            self.conn.commit()
            return item
    def open_spider(self,spider):
        self.conn = psycopg2.connect("dbname=basketball user = nd2")
        self.cur = self.conn.cursor()
        print("connected")
    def close_spideR(self,spider):
        self.cur.close()
        self.conn.close()
        print("closed")



        
class USAToday_sagarin_Pipeline(object):
    csv_file = None
    file_writer = None

    def get_rank_and_team(self,string):
        string_splitted = string.split()
        rank = string_splitted[0]
        team = " ".join(string_splitted[1:-1])
        return team,rank
    
    def process_first(self,writer,rows,year):
        still_header = True
        current = 1
        count = 50
        a_row = list()
        for row in rows:
         
            
            count+=1
            if (count == 56):
                still_header = False
                count = 1
            if(still_header):
                continue
            if(count % 5 == 1):    
                if "UNRATED"  in row:
                    return "done"
            if(count < 51):       
                a_row.append(row)
            if (count % 5 == 0 and count <51) and not still_header:
                a_row.append("NA")
                team,rank = self.get_rank_and_team(a_row[0])
                to_prepend = [year,team,rank]
                a_row = to_prepend + a_row[1:]
                writer.writerow(a_row)                  
                a_row = list()
                continue
    def process_second(self,writer,rows,year):
            still_header = True
            count = 50
            a_row = list()
            for row in rows:
                count+=1
                if (count == 59):
                    still_header = False
                    count = 1
                if(still_header):
                    continue
                if(count % 5 == 1):    
                    if "UNRATED"  in row:
                        return "done"
                if(count < 51):       
                    a_row.append(row)
                if (count % 5 == 0 and count <51) and not still_header:
                    a_row.append("NA")
                    team,rank = self.get_rank_and_team(a_row[0])
                    to_prepend = [year,team,rank]
                    a_row = to_prepend + a_row[1:]
                    writer.writerow(a_row)                  
                    a_row = list()
                    continue
    def process_third(self,writer,rows,is2018,year):
        still_header = True
        lol = 7
        if(is2018):
            lol = 8
        count = lol * 10
        a_row = list()
        print("starting")
        rows = iter(rows)
        for row in rows:
            #print(row)
            count+=1
            if (count == lol*10+12):
                still_header = False
                count = 1
            if(still_header):
                continue
            if(count % lol == 1):    
                if "UNRATED"  in row:
                    return "done"
            if(count < lol*10+1 and count % lol != 4):       
                a_row.append(row)
            if (count % lol == 0 and count < lol*10+1) and not still_header:
               
                if(is2018):
                    a_row.pop()
                team,rank = self.get_rank_and_team(a_row[0])
                to_prepend = [year,team,rank]
                a_row = to_prepend + a_row[1:]
                writer.writerow(a_row)
                a_row = list()
                continue

            
    def process_13(self,writer,rows,year):
            still_header = True
            count = 81
            current = 0
            a_row = list()
            for row in rows:
                current+=1
                if(current <= 5):
                    continue
                count+=1
                if (count == 82):
                    still_header = False
                    count = 1
                if(still_header):
                    continue
                if(count % 7 == 1):    
                    if "UNRATED"  in row:
                        return "done"
                if(count < 71 and count % 7 != 4 ):       
                    a_row.append(row)
                if (count % 7 == 0 and count <71) and not still_header:
                    team,rank = self.get_rank_and_team(a_row[0])
                    to_prepend = [year,team,rank]
                    a_row = to_prepend + a_row[1:]
                    writer.writerow(a_row)                  
                    a_row = list()
                    continue
        

                
    def process_item(self,item,spider):
        first_set = [2006,2007,2008,2009,2010]
        # 5 header , 5 college 


        #11,12
        # 8 header, 5 college
        second_set = [2011,2012]

        
        # 13
        # 5,11 header, 7 college 3 blank 3
        


        # 14,15,16,17   18(+section)
        # 11 header, 7 college  3 [blank] 3, technically one extra being the elo score
        # 18 has 8 3 [blank] 3 [dont need]
        third_set = [2014,2015,2016,2017,2018]
        

        # i know when to stop when
        #if("UNRATED") in the first of college 
        
        if(item['year']  in first_set):
            self.process_first(self.file_writer,item['theThings'],item['year'])
            
        if(item['year']  in second_set):
            self.process_second(self.file_writer,item['theThings'],item['year'])
        if(item['year']  in third_set):
            if(item['year']==2018):
                self.process_third(self.file_writer,item['theThings'],True,item['year'])
                print(20181231)
            else:
                 self.process_third(self.file_writer,item['theThings'],False,item['year'])

        if(item['year'] == 2013):
           self.process_13(self.file_writer,item['theThings'],item['year'])
     
        # year, team, rank, rating 
            
        print("processing")
        
        

    def open_spider(self,spider):
        # headers = rank/team, rating, w/l/sched/10/30, golden mean, predictor, elo score
        
        print("opened")
        self.csv_file = open('USAToday_sangarin_football.csv','w')  
        self.file_writer = csv.writer(self.csv_file,  delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        self.file_writer.writerow(['year','team','rank', 'rating', 'w:l:sched:10:30', 'golden mean', 'predictor', 'elo score'])

 
            
        # create the csv file
    def close_spider(self,spider):
       
        print("closed")

class AJ_pipeline(object):
    csv_file = None
    file_writer = None
    
    def process_item(self,item,spider):
         #print(item)
         # add row(s) to csv file
        for one_row in item['theThings']:
             self.file_writer.writerow(one_row)
            # print(one_row)
        
        return item
        
    def open_spider(self,spider):
        print("connected")

            #-------------------------------------------#

        self.csv_file = open('USAToday_coach_salaries_football.csv','w')
        #self.csv_file = open('USAToday_coach_salaries_basketball.csv','w')

            #-------------------------------------------#

        self.file_writer = csv.writer(self.csv_file,  delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        self.file_writer.writerow(['rank','college','conf','year','coach','school','other','total','max','prior year bonus'])
sst
 
            
        # create the csv file
    def close_spider(self,spider):
       
        print("closed")
                
class AJ2_pipeline(object):
    csv_file = None
    file_writer = None
    
    def process_item(self,item,spider):
         #print(item)
         # add row(s) to csv file
        for one_row in item['theThings']:
             self.file_writer.writerow(one_row)
            # print(one_row)
        
        return item
        
    def open_spider(self,spider):
        print("connected")

    #-------------------------------------------#

        self.csv_file = open('USAToday_coach_salaries_football.csv','a')
        #self.csv_file = open('USAToday_coach_salaries_basketball.csv','a')

#-------------------------------------------#

        self.file_writer = csv.writer(self.csv_file,  delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        

 
            
        # create the csv file
    def close_spider(self,spider):
       
        print("closed")
                
class RotoGrindersPipeline(object):

    def process_item(self,item,spider):
        
         self.cur.execute("insert into rotogrinders_predictions (rg_name, floor, ceiling, predicted,rg_abbr) values (%s,%s,%s,%s,%s) on conflict (rg_name) do update set floor = %s, ceiling =%s, predicted = %s,rg_abbr=%s",(item['name'],item['floor'],item['ceiling'],item['predicted'],item['team'],item['floor'],item['ceiling'],item['predicted'],item['team']))
         self.conn.commit()
         return item
        
    def open_spider(self,spider):
        self.conn = psycopg2.connect("dbname=basketball user = nd2")
        self.cur = self.conn.cursor()
        print("connected")
    def close_spider(self,spider):
        self.cur.close()
        self.conn.close()
        print("closed")
        
class TeamGamesPipeline(object):
  
    def process_item(self, item, spider):
           self.conn.commit()
           return item
    def open_spider(self,spider):
        self.conn = psycopg2.connect("dbname=basketball user = nd2")
        self.cur = self.conn.cursor()
        print("connected")
    def close_spideR(self,spider):
        self.cur.close()
        self.conn.close()
        print("closed")
