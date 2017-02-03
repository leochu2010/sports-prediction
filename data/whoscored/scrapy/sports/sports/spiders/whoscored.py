# -*- coding: utf-8 -*-
import scrapy
import re
import time
from selenium import webdriver
from scrapy_splash import SplashRequest
from itertools import chain


#run with command: scrapy crawl whoscored
#procedure for setting up splash
#https://blog.scrapinghub.com/2015/03/02/handling-javascript-in-scrapy-with-splash/
class WhoscoredSpider(scrapy.Spider):
    name = "whoscored"
    allowed_domains = ["www.whoscored.com"]
        
    START_URL="https://www.whoscored.com/Matches/1085146/Live"
        
    DOMAIN = 'www.whoscored.com'

    def start_requests(self):
        urls = [
            self.START_URL,
            "https://www.whoscored.com/Matches/1085239",            
        ]
        for url in urls:
            #yield scrapy.Request(url=url, callback=self.parse)
            yield SplashRequest(url, self.parse,
                endpoint='render.html',
                args={'wait': 0.5},
                )

    def parse(self, response):

        match_report_link = 'https://'+self.DOMAIN+response.css('div.layout-content-2col-left li:nth-of-type(5) a::attr(href)').extract_first()        
        
        match = {
            'home_team_name': response.css("td.team:nth-of-type(1) a.team-link::text").extract_first(),
            'home_team_link': response.css("td.team:nth-of-type(1) a.team-link::attr(href)").extract_first(),
            'away_team_name': response.css("td.team:nth-of-type(3) a.team-link::text").extract_first(),
            'away_team_link': response.css("td.team:nth-of-type(3) a.team-link::attr(href)").extract_first(),
            'half_time': response.css("div.info-block:nth-of-type(2) dd:nth-of-type(1)::text").extract_first(),
            'full_time': response.css("div.info-block:nth-of-type(2) dd:nth-of-type(2)::text").extract_first(),
            'kick_off': response.css("div.info-block:nth-of-type(3) dd:nth-of-type(1)::text").extract_first(),
            'date': response.css("div.info-block:nth-of-type(3) dd:nth-of-type(2)::text").extract_first(),
            'tournament_name': response.css("div#content-header a::text").extract_first(),
            'tournament_link': response.css("div#content-header a::attr(href)").extract_first(),
            'country': response.css("span.iconize::text").extract_first()
        }
        
        
        #self.logger.info("Visited %s", response.url)        
        
        if len(match_report_link) > 10:            
            #return scrapy.Request(match_report_link, callback=self.parse_match_report)
            request = SplashRequest(match_report_link, 
                callback=self.parse_match_report,
                endpoint='render.html',
                args={'wait': 0.5}                
                )
            request.meta['match'] = match
            yield request
                    
    def parse_match_report(self, response):
        
        match = response.meta['match']
        
        match['home_shots'] = response.css("div.stat-group.no-top-margin div.stat:nth-of-type(1) span.stat-value:nth-of-type(1) span::text").extract_first()
        match['away_shots'] = response.css("div.stat-group.no-top-margin div.stat:nth-of-type(1) span.stat-value:nth-of-type(3) span::text").extract_first()
        match['home_shots_on_target'] = response.css("div.stat-group.no-top-margin div.stat:nth-of-type(2) span.stat-value:nth-of-type(1) span::text").extract_first()
        match['away_shots_on_target'] = response.css("div.stat-group.no-top-margin div.stat:nth-of-type(2) span.stat-value:nth-of-type(3) span::text").extract_first()
        match['home_pass_success'] = response.css("div.stat-group.no-top-margin div.stat:nth-of-type(3) span.stat-value:nth-of-type(1) span::text").extract_first()
        match['away_pass_success'] = response.css("div.stat-group.no-top-margin div.stat:nth-of-type(3) span.stat-value:nth-of-type(3) span::text").extract_first()
        match['home_aerial_duel_success'] = response.css("div.stat-group.no-top-margin div.stat:nth-of-type(4) span.stat-value:nth-of-type(1) span::text").extract_first()
        match['away_aerial_duel_success'] = response.css("div.stat-group.no-top-margin div.stat:nth-of-type(4) span.stat-value:nth-of-type(3) span::text").extract_first()
        match['home_dribbles_won'] = response.css("div.stat-group.no-top-margin div.stat:nth-of-type(5) span.stat-value:nth-of-type(1) span::text").extract_first()
        match['away_dribbles_won'] = response.css("div.stat-group.no-top-margin div.stat:nth-of-type(5) span.stat-value:nth-of-type(3) span::text").extract_first()
        match['home_tackles'] = response.css("div.stat-group.no-top-margin div.stat:nth-of-type(6) span.stat-value:nth-of-type(1) span::text").extract_first()
        match['away_tackles'] = response.css("div.stat-group.no-top-margin div.stat:nth-of-type(6) span.stat-value:nth-of-type(3) span::text").extract_first()
        match['home_possession'] = response.css("div.stat-group:nth-of-type(2) div.stat span.stat-value:nth-of-type(2) span::text").extract_first()
        match['away_possession'] = response.css("div.stat-group:nth-of-type(2) div.stat span.stat-value:nth-of-type(3) span::text").extract_first()
        
        return match
        
        