# -*- coding: utf-8 -*-
import scrapy
import unidecode
import re

cleanString = lambda x: '' if x is None else unidecode.unidecode(re.sub(r'\s+',' ',x))


def get_movie_id(movie_url):
    regex = r"(t{2}[0-9]+)"
    return re.findall(regex, movie_url)[0]

def get_actor_id(actor_url):
    regex = r"(nm[0-9]+)"
    return re.findall(regex, actor_url)[0]


class imdbSpider(scrapy.Spider):
    name = 'imdb'
    domain = 'www.imdb.com'
    allowed_domains = [domain]
    start_urls = ["https://www.imdb.com/title/tt0096463/fullcredits/"]

    def parse(self, response):
        for actor in response.css(".cast_list tr"):
            print("*********************************************")
            actor_name = actor.xpath('td[2]/a/span/text()').extract_first()
            if(actor_name == None):
                continue
            print(actor_name)
            actor_id = actor.xpath('td[4]/a/text()').extract_first()
            # yield {
            #         'movie_id': get_movie_id(response.url),
            #         'movie_name': actor.css('.parent>a::text').extract_first(),
            #         'movie_year': get_movie_id(response.url),
            #         'movie_id': get_movie_id(response.url),
            #         'actor_name': actor.xpath('td[2]/a/span/text()').extract_first(), # works
            #         'actor_id': get_actor_id(actor_url),
            #         'role_name': actor.xpath('td[4]/a/text()').extract_first(), # works
            #     }



        # movie_name = response.css('div.parent>a::text').extract_first()
        # print(movie_name)
        # for actor in response.css("table.cast_list .itemprop"):
        #     actor_url = self.domain + actor.css('.itemprop>a::attr(href)').extract_first()
        #     print(actor_url)
        #     yield {
        #         'movie_id': get_movie_id(response.url),
        #         'movie_name': actor.css('.parent>a::text').extract_first(),
        #         'movie_year': get_movie_id(response.url),
        #         'movie_id': get_movie_id(response.url),
        #         'actor_name': cleanString(actor.css('.itemprop>a::text').extract_first()),
        #         'actor_id': get_actor_id(actor_url),
        #         'role_name': cleanString(actor.css('p.byline::text').extract_first())
        #     }
        #     next_page = actor_url
        #     if next_page is not None:
        #         yield response.follow(next_page, callback=self.parse_actor)

    def parse_actor(self, response):
        for article in response.css("section.top-news article.story"):
            article_url = article.css('.story-heading>a::attr(href)').extract_first()
            yield {
                'appears_ulr': response.url,
                'title': cleanString(article.css('.story-heading>a::text').extract_first()),
                'article_url': article_url,
                'author': cleanString(article.css('p.byline::text').extract_first()),
                'summary': cleanString(article.css('p.summary::text').extract_first()) + cleanString(
                    ' '.join(article.css('ul *::text').extract())),
            }
            next_page = article_url
            if next_page is not None:
                yield response.follow(next_page, callback=self.parse_article)

