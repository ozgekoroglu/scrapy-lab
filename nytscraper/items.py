# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.item import Item,Field


class NytscraperItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html


class MovieItem(Item):
    Title = Field()
    MovieId = Field()
    Rating = Field()
    nrRatings = Field()
    ReleaseYear = Field()
    MainPageUrl = Field()

    # extra detials
    Director = Field()
    Producer = ()
    Writers = Field()
    Genres = Field()
    Budget = Field()
    Language = Field()
    Country = Field()
    Location = ()

    # technical details
    GrossProfit = Field()
    OpeningWeekendProfit = Field()

    CastMembers = Field()


class CastItem(Item):
	ActorName = Field()
	CharacterName = Field()
