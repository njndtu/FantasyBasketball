# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class ScrapyspidersItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass
class SagarinUSAItem(scrapy.Item):
    theThings = scrapy.Field()
    year = scrapy.Field()

class CoachItem(scrapy.Item):

    theThings = scrapy.Field()
    
class TeamItem(scrapy.Item):
    teamAbbr = scrapy.Field()
    teamId = scrapy.Field()
    
class GameItem(scrapy.Item):
    gameId = scrapy.Field()
    gameInfo = scrapy.Field()
    gameDuration = scrapy.Field()
    
class RotoGrindersItem(scrapy.Item):
    name = scrapy.Field()
    floor = scrapy.Field()
    ceiling = scrapy.Field()
    predicted = scrapy.Field()
    team = scrapy.Field()
