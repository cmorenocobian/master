# -*- coding: utf-8 -*-
"""
Created on Tue Aug  3 16:53:58 2021

@author: carlo
"""
# %% Import

import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.selector import Selector
import json
import datetime as dt
import pandas as pd
import time
import random

#%% Clase
# Scrapper Class
class Restaurants(scrapy.Spider):
    
    # base url común de todas las paginas
    base_url="https://www.thefork.es/search/?cityId=328022"
    total_pages = 1
    # custom headers
    # inspeccionar página, en Network -> ->Request headers, selleccionar desde accept hasta final
    
    # headers= {
    #     'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    #     'accept-encoding': 'gzip, deflate, br',
    #     'accept-language': 'es-ES,es;q=0.9,en;q=0.8,en-GB;q=0.7',
    #     'cache-control': 'max-age=0',
    #     'referer': 'https://www.tripadvisor.es/Tourism-g187514-Madrid-Vacations.html',
    #     'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
    #     'sec-ch-ua-mobile': '?0',
    #     'sec-fetch-dest': 'document',
    #     'sec-fetch-mode': 'navigate',
    #     'sec-fetch-site': 'same-origin',
    #     'sec-fetch-user': '?1',
    #     'upgrade-insecure-requests': '1',
    #     'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'
    #     }
    
    headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8,en-GB;q=0.7',
        'Connection': 'keep-alive',
        'Content-Length': '3743',
        'content-type': 'text/plain',
        'Cookie': 'JSESSIONID=e0d48aac3d92ca5',
        'Host': 'bam-cell.nr-data.net',
        'Origin': 'https://www.thefork.es',
        'Referer': 'https://www.thefork.es/',
        'sec-ch-ua': '"Google Chrome";v="93", " Not;A Brand";v="99", "Chromium";v="93"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'cross-site',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36'
        }
    
    # Override Custom Settings
    custom_settings = {
        "CONCURRENT_REQUESTS_PER_DOMIAN":1,
        "DOWNLOAD_DELAY": 3
        }
    
    # Current Page counter
    current_page = 1
    
    # init constructor
    def __init__(self):
        pass

    def open_url(self, url=base_url):
        from selenium import webdriver
        print("\n\n\n ----------------------- CAPTCHA --------------------\n\n\n")
        driver = webdriver.Chrome(r"C:\Users\carlos\Google Drive\master\curso2020-2021\99 - tfm\restaurant\chromedriver.exe")
        # load web
        driver.get(url)
        time.sleep(20)
        # content = driver.page_source

    # crawler's entry point
    def start_requests(self):

        # reset current page counter
        self.current_page=1
        
        filename = 'thefork_' + dt.datetime.today().strftime("%Y-%m-%d-%H-%M") + \
                        '_' + str(self.current_page) + '.json'

        # counters
        count = 1
        try:
            print('\n\nstart ----')
            yield scrapy.Request(
                url = self.base_url,
                headers = self.headers,
                meta = {
                    'filename': filename,
                    'count': count
                    },
                callback = self.parse_links
                )
            # time.sleep(random.randint(4,7))
            
        except Exception as e:
            print('\n\n\n --------------- error exception\n',e, '\n-------------\n\n\n')
            self.open_url(self.base_url)
            yield scrapy.Request(
                self.base_url,
                headers = self.headers,
                meta = {
                    'filename': filename,
                    'count': count
                    },
                callback = self.parse_links
                )
            time.sleep(random.randint(4,7))
                

            # Increment current postcode counter
        count += 1

    # Parse links
    def parse_links(self, response):
        print('\n\n parse links:\n')
        print(response.meta.get('filename'))
        # extract meta data
        filename = response.meta.get('filename')
        count = response.meta.get('count')
        
        # extract cards
        # cards = list(response.css('a[class="_15_ydu6b"]::attr(href)').getall())
        cards = list(response.css('h2[class="css-siel6k e7dhrrp0"]').getall())
        cnt=1
        print(cards)

        # loop over property card URLs
        for card_url in cards:
            print('card nº: ' + str(cnt) + '; ' + card_url)
            try:
                # crawl property listing
                yield response.follow(
                    url = card_url,
                    headers = self.headers,
                    meta={
                        'filename': filename
                        },
                    callback = self.parse_listing
                    )
                time.sleep(random.randint(2,4))
                
            except:
                self.open_url(self.base_url + card_url)

                yield response.follow(
                    url = card_url,
                    headers = self.headers,
                    meta={
                        'filename': filename
                        },
                    callback = self.parse_listing
                    )
                time.sleep(random.randint(4,7))
            cnt += 1
        
        # Handle pagination within each postcode URL
        try:
            try:
                # extract total pages
                total_pages = response.css('a[variant="secondary"] *::text').getall()
                total_pages= list(filter(None,[x.replace('\r\n', '').strip() for x in total_pages]))
                if total_pages[-1].isnumeric:
                    total_pages = total_pages[:-1]
                total_pages =[int(x) for x in total_pages]
                total_pages = max(total_pages)
                self.total_pages = max(total_pages, self.total_pages)
                #increment number current page
                self.current_page += 1
                # print('a[data-page-number="' + str(self.current_page) +'"]::attr(href)')
                
            except:
                pass
            
            # check if the current page is within the legal page range
            if self.current_page <= total_pages:
                next_page = "https:www.thefork.es/search/?cityId=328022&p=" + str(self.current_page)
                self.current_page += 1
                print('siguiente pagina: ', next_page)
                # print debug information
                print('PAGE %s | %s' % (self.current_page, total_pages))
                try:
                    # crawl next page
                    yield response.follow(
                        url = next_page,
                        headers = self.headers,
                        meta = {
                            'filename': filename,
                            'count': count
                            },
                        callback = self.parse_links
                        )
                    time.sleep(random.randint(4,7))
                except:
                    self.open_url(next_page)
                    yield response.follow(
                        url = next_page,
                        headers = self.headers,
                        meta = {
                            'filename': filename,
                            'count': count
                            },
                        callback = self.parse_links
                        )
                    time.sleep(random.randint(4,7))

        except Exception as e:
            print(e)
            pass

    # Parse property card listing
    def parse_listing(self, response):
        print('\n\n scrapping --------------')

        # with open('trip2.html', 'w', encoding='utf-8') as f:
        #     f.write(response.text)
        
        # content=''
        # with open('trip.html', 'r', encoding="utf8") as f:
        #     for line in f.read():
        #         content +=  line
        # response = Selector(text=content)                
                
        features={
            'url': response.url,
            }
        
        try:
            features['nombre'] = response.css('h1[class="css-md0073 e7dhrrp0"]::text').get()
                                
        except:
            features['nombre'] = ''
            
        try:
            features['direccion'] = response.css('span[class="css-dj3hn7 eulusyj0"]::text').get()
        except:
            features['direccion'] = ''
            
        try:
            features['puntuacion'] = response.css('span[data-test="rating-value"]::text').get()
        except:
            features['puntuacion'] = ''
            
        try:
            features['opiniones'] = response.css('div[data-test="restaurant-page-reviews-count"]::text').get().rstrip(" opiniones")
        except:
            features['opiniones'] = ''
            
        try:
            features['tipo'] = response.css('span[class="css-p9y4s5 enrzupw2"]::text').get().rstrip(" opiniones")
        except:
            features['tipo'] = ''
            
        try:
            features['precio'] = response.css('p[class="css-7bm2zz eulusyj0"]').css('span').getall()[1][:-2]
        except:
            features['precio'] = ''
     

        
        
        try:
            script= ''.join([text.get() for text in response.css('script::text') 
                        if 'latitude' in text.get()]
                            )
            features['coordinates'] = {
                'latitude': script.split('"latitude":')[1].split(',')[0].strip('\\"'),
                'longitude': script.split('"longitude":')[1].split(',')[0].strip('\\"')
                    }
        except:
            features['coordinates'] = {'latitude':'', 'longitude': ''}
        
        # print(json.dumps(features, indent = 2))
        
        # Extract meta data
        filename = response.meta.get('filename')
        # guardamos el archivo con la info
        # filename = 'thefork_' + dt.datetime.today().strftime("%Y-%m-%d-%H-%M") + \
        #                 '_' + str(self.current_page) + '.jsonl'
        with open(filename, 'a') as f:
            f.write(json.dumps(features, indent = 2) + '\n')


# main driver
if __name__== "__main__":
    # run scraper
    process = CrawlerProcess()
    process.crawl(Restaurants)
    process.start()
    


import glob
import json
data=[]
archivos = glob.glob(r'C:\Users\carlos\Google Drive\master\curso2020-2021\99 - tfm\thefork_*')

for path in archivos:
    f = open(path)
    data.append(json.load(f))

with open('data_thefrork.json', 'w') as f:
    json.dump(data, f)

