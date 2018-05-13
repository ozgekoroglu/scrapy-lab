# -*- coding: utf-8 -*-
import scrapy
import unidecode
import re
import os

from elasticsearch import Elasticsearch

ELASTIC_API_URL_HOST = os.environ['ELASTIC_API_URL_HOST']
ELASTIC_API_URL_PORT = os.environ['ELASTIC_API_URL_PORT']
ELASTIC_API_USERNAME = os.environ['ELASTIC_API_USERNAME']
ELASTIC_API_PASSWORD = os.environ['ELASTIC_API_PASSWORD']

es = Elasticsearch(host=ELASTIC_API_URL_HOST,
                   scheme='https',
                   port=ELASTIC_API_URL_PORT,
                   http_auth=(ELASTIC_API_USERNAME, ELASTIC_API_PASSWORD))

cleanString = lambda x: '' if x is None else unidecode.unidecode(re.sub(r'\s+',' ',x))


def get_movie_id(movie_url):
    regex = r"(t{2}[0-9]+)"
    return re.findall(regex, movie_url)[0]

def get_actor_id(actor_url):
    regex = r"(nm[0-9]+)"
    return re.findall(regex, actor_url)[0]

def check_year(year):
    return 1980<year and year<1990

def is_valid_year(year):
    return year.isnumeric()


class imdbSpider(scrapy.Spider):
    name = 'imdb'
    domain = 'www.imdb.com'
    allowed_domains = [domain]
    start_urls = ["https://www.imdb.com/title/tt0096463/fullcredits/"]


    def parse(self, response):
        movie_name = response.xpath('.//h3[@itemprop="name"]/a/text()').extract_first()
        movie_year = cleanString(response.xpath('.//h3[@itemprop="name"]/span/text()').extract_first())
        for actor in response.css(".cast_list tr"):
            actor_name = actor.xpath('td[2]/a/span/text()').extract_first()
            if actor_name == None:
                continue
            role_name = actor.xpath('td[4]/a/text()').extract_first() # Get role names that are linked to an IMDB page
            if role_name == None: # Get role names that are not linked to an IMDB page
                role_name = cleanString(actor.xpath('td[4]/text()').extract_first().split())
            actor_url = actor.xpath('td[2]/a[1]/@href').extract_first()
            actor_url = actor_url[:actor_url.find('?')]
            es.index(index='imdb',
                     doc_type='movies',
                     body={
                        'movie_id': get_movie_id(response.url), # works
                        'movie_name': movie_name,
                        'movie_year': movie_year,
                        'actor_name': cleanString(actor_name), # works
                        'actor_id': get_actor_id(actor_url), # works
                        'role_name': cleanString(role_name) # works
                     })

            next_page = actor_url
            # print("Next actor page: " + actor_url + " for actor " + actor_name)
            if next_page is not None:
                yield response.follow(next_page, callback=self.parse_actor)

    def parse_actor(self, response):
        for movie in response.xpath("//*[contains(@class,'filmo-category-section')]/div"):
            # type = movie.css("#text").extract_first()
            # print(type)
            # if '(TV Series)' or '(Video Game)' or ('TV Mini-Series') or '(TV Series short)' or 'Short Video' in type:
            #     continue
            movie_year = cleanString(movie.xpath('span[1]/text()').extract_first().strip())
            if not is_valid_year(movie_year) or not check_year(int(movie_year)):
                continue
            movie_url = cleanString(movie.xpath('b[1]/a[1]/@href').extract_first())
            movie_url = movie_url[:movie_url.find('?')] + 'fullcredits/'
            next_page = movie_url
            # print("Next page: " + next_page + " " + movie_year)
            if next_page is not None:
                yield response.follow(next_page, callback=self.parse)


