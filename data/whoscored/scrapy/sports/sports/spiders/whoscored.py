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
    #2015/16
    #MATCH_ID = 959257 (959532)         
    #MIN_MATCH_ID = 958445 (958436)
    
    #2014/15
    #829900-830250        
    #MATCH_ID = 831500
    #MIN_MATCH_ID = 828500
    
    #2013/14
    #719891-721561
    MATCH_ID = 722600
    MIN_MATCH_ID = 718800
    
    RETRY_LIST = []
    RETRY_LOG = open("retry.log","w")

    def start_requests(self):
        
        urls2 = {
            "https://www.whoscored.com/404.html?aspxerrorpath=/Matches/10000000/live",
            "https://www.whoscored.com/Matches/1085217/Live"            
            }
        
        urls = {
            }
        
        
        urls1 = {
            "https://www.whoscored.com/Matches/1083858/Live",
            "https://www.whoscored.com/Matches/1083598/Live",
            "https://www.whoscored.com/Matches/1083599/Live",
            "https://www.whoscored.com/Matches/1083600/Live",
            "https://www.whoscored.com/Matches/1083601/Live",
            "https://www.whoscored.com/Matches/1083602/Live"
        }
        
        
        for url in urls:
            yield SplashRequest(url, self.parse,
                endpoint='render.html',
                args={'wait': 2},
                priority = -1
                )            
        
        current_match_id = self.MATCH_ID 
        while current_match_id > self.MIN_MATCH_ID:
            current_match_id -= 1
            match_link = "https://www.whoscored.com/Matches/"+str(current_match_id)+"/Live"
            
            yield SplashRequest(match_link, self.parse,
                endpoint='render.html',
                args={'wait': 3},
                priority=-1
                )
                
            while len(self.RETRY_LIST) > 0:                
                retry_url = self.RETRY_LIST.pop()       
                     
                self.logger.info("retry failed matches: %s",retry_url)
                
                yield SplashRequest(retry_url, self.parse,
                    endpoint='render.html',
                    args={'wait': 3},
                    dont_filter=True,
                    priority=1
                    )         

    def parse(self, response):
        invalid_page = response.css('div:nth-of-type(1)::text').extract_first()
        if invalid_page is None:
            self.logger.info("%s wasn't rendered properly, retry later", response.url)
            self.RETRY_LIST.append(response.url)
            self.RETRY_LOG.write(response.url+"\n")
            self.RETRY_LOG.flush()                        
            return
                                
        if "The page you requested does not exist" in invalid_page:
            self.logger.info("%s doesn't exists", response.url)
            return

        match_report_relative_link = response.css('div.layout-content-2col-left li:nth-of-type(5) a::attr(href)').extract_first()
        if match_report_relative_link is None:
            self.logger.info("%s wasn't rendered properly, retry later", response.url)
            self.RETRY_LIST.append(response.url)
            self.RETRY_LOG.write(response.url+"\n")
            self.RETRY_LOG.flush()                        
            return
        
        match_report_link = 'https://'+self.DOMAIN+match_report_relative_link
        
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
            self.logger.info("%s has match report", response.url)
            
            request = SplashRequest(match_report_link, 
                callback=self.parse_match_report,
                endpoint='render.html',
                args={'wait': 3},
                meta = {'match':match, 'match_link': response.url},
                dont_filter=True,
                )
            yield request
        else:            
            self.logger.info("%s doesn't have match report", response.url) 
                    
    def parse_match_report(self, response):
        
        match = response.meta['match']
        match_link = response.meta['match_link']

        #put to retry list
        if len(response.css("div.stat-group.no-top-margin div.stat:nth-of-type(1) span.stat-value:nth-of-type(1)")) == 0:
            self.logger.info("%s wasn't rendered properly, retry with %s later", response.url, match_link)
            self.RETRY_LIST.append(match_link)
            self.RETRY_LOG.write(match_link+"\n")
            self.RETRY_LOG.flush()
            return
           
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
        
        