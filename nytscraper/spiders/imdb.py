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

def is_valid_year(year):
    # return year.isnumeric() and 1979<int(year) and int(year)<1990
    return year.isnumeric() and  1999 < int(year) # movies in the 2000's to identify most financially successful movies of the 21st century


class imdbSpider(scrapy.Spider):
    name = 'imdb'
    domain = 'www.imdb.com'
    allowed_domains = [domain]
    start_urls = ["https://www.imdb.com/title/tt0096463/fullcredits/"]

    # Parsing the movie's full credits page
    def parse(self, response):
        movie_name = response.xpath('.//h3[@itemprop="name"]/text()').extract_first()
        movie_year = cleanString(response.xpath('.//h3[@itemprop="name"]/span/text()').extract_first().strip())
        movie_year = re.findall('\d+', movie_year ).pop() # get only numbers from year
        # print("Movie Year " + str(movie_year) + " Movie Name " + movie_name)
        for actor in response.css(".cast_list tr"):
            actor_name = actor.xpath('td[2]/a/span/text()').extract_first()
            if actor_name == None:
                continue
            role_name = actor.xpath('td[4]/a/text()').extract_first() # Get role names that are linked to an IMDB page
            if role_name == None: # Get role names that are not linked to an IMDB page
                role_name = actor.xpath('td[4]/text()').extract_first().strip()
            actor_url = actor.xpath('td[2]/a[1]/@href').extract_first()
            actor_url = actor_url[:actor_url.find('?')]
            # yield {
            #     'movie_id': get_movie_id(response.url),
            #     'movie_name': movie_name,
            #     'movie_year': movie_year,
            #     'actor_name': cleanString(actor_name),
            #     'actor_id': get_actor_id(actor_url),
            #     'role_name': cleanString(role_name)
            # }

            es.index(index='imdb',
                     doc_type='movies',
                     body={
                        'movie_id': get_movie_id(response.url),
                        'movie_name': movie_name,
                        'movie_year': movie_year,
                        'actor_name': cleanString(actor_name),
                        'actor_id': get_actor_id(actor_url),
                        'role_name': cleanString(role_name)
                     })

            yield response.follow(response.url.replace("/fullcredits", ""), callback=self.parse_movie)
            next_page = actor_url
            # print("Next actor page: " + actor_url + " for actor " + actor_name)
            if next_page is not None:
                yield response.follow(next_page, callback=self.parse_actor)



    # Parsing the actor's IMDb page
    def parse_actor(self, response):
        for movie in response.xpath("//*[contains(@class,'filmo-category-section')][1]/div"):
            # get only the films the person is an actor in (not producer, writer, etc.)

            type = movie.css("::text") # get ONLY movies (not series, video games, etc.)
            if '(TV Series)' in str(type) or '(Video Game)' in str(type) or ('TV Mini-Series') in str(type) \
                    or '(TV Series short)' in str(type) or '(Short Video)' in str(type) or ('TV Series documentary') in str(type) \
                    or ('Video') in str(type) or '(TV Mini-Series documentary)' in str(type) or '(TV Short)' in str(type):
                continue
            movie_year = cleanString(movie.xpath('span[1]/text()').extract_first().strip())
            if not is_valid_year(movie_year):
                continue
            movie_url = cleanString(movie.xpath('b[1]/a[1]/@href').extract_first())
            movie_url = movie_url[:movie_url.find('?')] + 'fullcredits/'
            next_page = movie_url
            # print("Next page: " + next_page + " " + movie_year)
            if next_page is not None:
                yield response.follow(next_page, callback=self.parse)

     # Parsing the movie's IMDb page
    def parse_movie(self,response):
        movie_name = cleanString(response.xpath('.//h1[@itemprop="name"]/text()').extract_first())
        for div_element in response.xpath("//div[contains(@class,'txt-block')]"):
            try:
                header = div_element.xpath("h4/text()")[0].extract()
            except IndexError:
                header = ""
            if(header == "Budget:"):
                budget_amount = cleanString(div_element.css("::text")[2].extract().replace('$',''))
            elif(header == "Cumulative Worldwide Gross:"):
                gross_amount = cleanString(div_element.css("::text")[2].extract().replace('$',''))
        print("-----------------------" + movie_name + "-----------------------")
        try:
            budget_amount and gross_amount
        except NameError:
            print("Data N/A")
        else:
            print("Budget: " + budget_amount + " Gross: " + gross_amount)
            es.index(index='imdb_budget',
                     doc_type='movies',
                     body={
                         'movie_id': get_movie_id(response.url),
                         'movie_name': movie_name,
                         'budget': budget_amount,
                         'gross': gross_amount
                     })



