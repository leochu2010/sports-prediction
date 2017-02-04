# -*- coding: utf-8 -*-
import scrapy
import re
import time
from selenium import webdriver
from scrapy_splash import SplashRequest
from itertools import chain
from chardet.hebrewprober import MIN_MODEL_DISTANCE


#run with command: scrapy crawl whoscored
#procedure for setting up splash
#https://blog.scrapinghub.com/2015/03/02/handling-javascript-in-scrapy-with-splash/
class WhoscoredSpider(scrapy.Spider):
    name = "whoscored"
    allowed_domains = ["www.whoscored.com"]
        
    DOMAIN = 'www.whoscored.com'
    MATCH_ID = 1085239    
    MIN_MATCH_ID = 1084209

    def start_requests(self):
        
        current_match_id = self.MATCH_ID 
        while current_match_id > self.MIN_MATCH_ID:
            current_match_id -= 1
            match_link = "https://www.whoscored.com/Matches/"+str(current_match_id)+"/Live"
            
            yield SplashRequest(match_link, self.parse,
                endpoint='render.html',
                args={'wait': 2},
                )            

    def parse(self, response):

        match_report_relative_link = response.css('div.layout-content-2col-left li:nth-of-type(5) a::attr(href)').extract_first()
        if match_report_relative_link is None:
            self.logger.info("%s doesn't have match detail", response.url)
            return
            
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
            'country': response.css("span.iconize::text").extract_first(),
            'match_link': response.url, 
            'match_report_link': match_report_link
        }
                    
        #return scrapy.Request(match_report_link, callback=self.parse_match_report)
        if len(match_report_link) > 30:
            self.logger.info("%s has match detail, start extracting", response.url) 
            request = SplashRequest(match_report_link, 
                callback=self.parse_match_report,
                endpoint='render.html',
                args={'wait': 2},
                meta = {'match':match}
                )
            yield request
        else:            
            self.logger.info("%s doesn't have match detail", response.url) 
                    
    def parse_match_report(self, response):
        
        match = response.meta['match']
                
        if len(response.css("div.stat-group.no-top-margin div.stat:nth-of-type(1) span.stat-value:nth-of-type(1)")) == 0:
           self.logger.info("url:%s, body:%s",response.url,response.css("body").extract()) 
           
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
        
        