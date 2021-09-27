# -*- coding: utf-8 -*-
"""
Created on Tue Aug  3 16:53:58 2021

@author: carlo
"""
# %% Import

import scrapy
from scrapy.crawler import CrawlerProcess
# from scrapy.selector import Selector
import json
import datetime as dt
import pandas as pd
import time
import random

#%% Clase
# Scrapper Class
class CommercialSale(scrapy.Spider):
    
    # base url común de todas las paginas
    base_url="https://www.idealista.com/buscar/"
    # custom headers
    # inspeccionar página, en Network ->28001 ->Request headers, selleccionar desde accept hasta final
    headers= {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "es-ES,es;q=0.9,en;q=0.8,en-GB;q=0.7",
        "cache-control": "max-age=0",
        "referer": "https://www.idealista.com/",
        "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
        "sec-ch-ua-mobile": "?0",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "same-origin",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"
        }
    
    # Override Custom Settings
    custom_settings = {
        "CONCURRENT_REQUESTS_PER_DOMIAN":1,
        "DOWNLOAD_DELAY": 3
        }
    
    # Current Page counter
    current_page = 1
    
    # Postcodes lists
    postcodes = []
    
    # init constructor
    def __init__(self, alquiler=True):
        # postcodes content
        content=""
        
        # open "post codes" file
        with open("codigos_postales.txt", "r") as f:
            for line in f.read():
                content += line
        f.close()
        #parse content
        self.postcodes = list(filter(None,content.split("\n")))        
        
        if alquiler:
            self.base_url += 'alquiler-locales/'
            self.alquiler= 'alquiler'
        else:
            self.base_url += 'venta-locales/'
            self.alquiler= 'compra'
    
    def open_url(self, url='https://www.idealista.com'):
        from selenium import webdriver
        
        driver = webdriver.Chrome(r"C:\Users\carlos\Google Drive\master\curso2020-2021\99 - tfm\restaurant\chromedriver.exe")
        # load web
        driver.get(url)
        time.sleep(random.randint(15,25))
        # content = driver.page_source

    # crawler's entry point
    def start_requests(self):

        # reset current page counter
        self.current_page=1
        
        # loop over postcodes
        for postcode in self.postcodes:
            # init filename
            filename = 'idealista_' + self.alquiler + "_" + postcode + '_' + \
                dt.datetime.today().strftime("%Y-%m-%d-%H-%M-%S") + '.json'
            
            # generate next postcode URL
            next_postcode = self.base_url + str(postcode) + "/"
            
            # post code counters
            count = 1
            try:

                yield scrapy.Request(
                    url = next_postcode,
                    headers = self.headers,
                    meta = {
                        'postcode': postcode,
                        'filename': filename,
                        'count': count
                        },
                    callback = self.parse_links
                    )
                time.sleep(random.randint(4,7))
                
            except Exception as e:
                print('\n\n\n ---------------\n',e, '\n-------------\n\n\n')
                self.open_url(next_postcode)
                yield scrapy.Request(
                    url = next_postcode,
                    headers = self.headers,
                    meta = {
                        'postcode': postcode,
                        'filename': filename,
                        'count': count
                        },
                    callback = self.parse_links
                    )
                time.sleep(random.randint(4,7))
                

            # Increment current postcode counter
            count += 1
            break

    # Parse links
    def parse_links(self, response):
        
        # extract meta data
        postcode = response.meta.get('postcode')
        filename = response.meta.get('filename')
        count = response.meta.get('count')
        
        # cards url
        card_urls = []
        
        # extract cards
        cards_hightop = response.css('article[class="item item_contains_branding ite_hightop item_multimedia-container"]')
        cards_casual = response.css('article[class="item  item_contains_branding item-multimedia-container"]')
        
        # Extract hightop card URLs
        for card in cards_hightop:
            card_urls.append(card.css('a[class="item-link"]::attr(href)').get())

        # Extract casual card URLs
        for card in cards_casual:
            card_urls.append(card.css('a[class="item-link"]::attr(href)').get())

        # loop over property card URLs
        for card_url in card_urls:
            try:
                # crawl property listing
                yield response.follow(
                    url = card_url,
                    headers = self.headers,
                    meta={
                        'postcode':postcode,
                        'filename': filename
                        },
                    callback = self.parse_listing
                    )
                time.sleep(random.randint(4,7))
                # break
            except:
                self.open_url(self.base_url + card_url)
                yield response.follow(
                    url = card_url,
                    headers = self.headers,
                    meta={
                        'postcode':postcode,
                        'filename': filename
                        },
                    callback = self.parse_listing
                    )
                time.sleep(random.randint(4,7))

        # Handle pagination within each postcode URL
        try:
            try:
                # extract total pages
                total_pages = response.css('div[class="pagination"]')
                total_pages = total_pages.css('li *::text').getall()
                total_pages= max([
                    int(page.replace('\r\n', '').strip())
                        for page in total_pages
                        if page.replace('\r\n', '').strip().isdigit()
                        ])
                # increment current page counter
                self.current_page += 1
                print()
                
            except:
                total_pages = 1
                self.current_page = 1
            
            # print debug info
            print('POSTCODE %s | %s out of %s postcodes' % (postcode, count, len(self.postcodes)))

            # print('total: ', total_pages, self.current_page)
            
            # check if the current page is within the legal page range
            if self.current_page <= total_pages:
                next_page = self.base_url + str(postcode) + '/'
                next_page += 'pagina-' + str(self.current_page) + '.htm'
                
                # print debug information
                print('PAGE %s | %s' % (self.current_page, total_pages))
                try:
                    # crawl next page
                    yield response.follow(
                        url = next_page,
                        headers = self.headers,meta = {
                            'postcode': postcode,
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
                        headers = self.headers,meta = {
                            'postcode': postcode,
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

        # Extract meta data
        postcode = response.meta.get('postcode')
        filename = response.meta.get('filename')
        
        def rep(z):
            ree={
                '\u00b2':"2",
                '\u00aa':'',
                '\u00fa': 'u',
                '\u00f3': 'o',
                '\u00e1': 'a',
                '\u00e9': 'e',
                '\u00da': 'U',
                'á':'a',
                'é': 'e',
                'í': 'i',
                'ó': 'o',
                'ú':'u',
                }
            for i in ree:
                if i in z:
                    z= z.replace(i, ree[i])
                    if i != '\u00b2':
                        break
            return z

        # data extraction logic
        features = {
            'id': response.url.strip('https://www.idealista.com/inmueble/').split('/')[0],
            'url': response.url,
            'postcode': postcode,
            'title': response.css('span[class="main-info__title-main"]::text')
                                    .get(),
            'address': response.css('span[class="main-info__title-minor"]::text')
                                    .get(),
            'price': response.css('span[class="txt-bold"]::text') # 1:18:00
                                    .get(),
            'floor_area': response.css('div[class="info-features"] *::text').getall()[2],
                                    
            'location': list(filter(None, 
                                    [rep(text.strip()) for text in 
                                    response.css('div[id="headerMap"] *::text').getall() 
                                    if "Madrid" not in text])),

            'key_features': list(filter(None, [text.strip() for text in 
                                            response.css('div[class="details-property"]')
                                            .css('li::text').getall()])),

            'coordinates': {
                            'latitude': '',
                            'longitude': ''
                            },
            'date': dt.datetime.today().strftime("%Y-%m-%d")
            }
        features['key_features'] = [rep(str(i)) for i in features['key_features']]
        try:
            features['location'].remove("Ubicacion")
        except:
            pass
        
        # extract script containing JSON data
        try:
            script= ''.join([text.get() for text in response.css('body[data-taxonomy-city-id="328022"]::text').getall()])
            features['coordinates'] = {
                'latitude': script.split('"latitude":')[1].split(",")[0],
                'longitude': script.split('"longitude":')[1].split(",")[0]
                    }
        except:
            pass
        
        filename = 'idealista_' + self.alquiler + "_" + postcode + '_' + \
                dt.datetime.today().strftime("%Y-%m-%d-%H-%M-%S") + '.json'

        with open(filename, 'w') as f:
            f.write(json.dumps(features) + '\n')

# main driver
if __name__== "__main__":
    # run scraper
    process = CrawlerProcess()
    process.crawl(CommercialSale)
    process.start()
    
    # CommercialSale.parse_listing(CommercialSale, '')


import glob
import json
data=[]
archivos = glob.glob(r'C:\Users\carlos\Google Drive\master\curso2020-2021\99 - tfm\idealista_alquiler*')

for path in archivos:
    f = open(path)
    data.append(json.load(f))

with open('data_idealista.json', 'w') as f:
    json.dump(data, f)

# with open('data_idealista.json', 'r') as f:
#     z = json.load(f)





