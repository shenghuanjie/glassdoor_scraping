import requests
from bs4 import BeautifulSoup
import scrapy
import json
from scrapy.spiders import Spider
from scrapy.selector import Selector
from scrapy.item import Item, Field
import re

import IPython

headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36"}
name = "glassdoor"
allowed_domains = ["glassdoor.com"]
start_urls = [
"https://www.glassdoor.com/Salaries/los-angeles-software-engineer-salary-SRCH_IL.0,11_IM508_KO12,29.htm"
]
login_url = "https://www.glassdoor.com/profile/login_input.htm"
with open("login_data.json") as fp:
    login_data = json.load(fp)

# log in here
sess = requests.Session()
response = sess.get(login_url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser').text
template = r'"gdToken":"([^"]*)"'
token = re.search(template, soup, flags=re.MULTILINE).groups()[0]
login_data["gdToken"] = token
sess.post(login_url, data=login_data, headers=headers)

url = start_urls[0]
response = sess.get(url, headers=headers)
sel = Selector(response)
sites = sel.xpath('//ul/li')
items = []

for site in sites:
    item = dict()
    item['title'] = site.xpath('a/text()').extract()
    item['link'] = site.xpath('a/@href').extract()
    item['desc'] = site.xpath('text()').extract()
    items.append(item)
print(items)

IPython.embed()
