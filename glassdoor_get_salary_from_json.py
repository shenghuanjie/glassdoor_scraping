import json
import requests
from bs4 import BeautifulSoup
import re

json_file = "job_salary_links.json"
with open(json_file) as fp:
    grouped_links = json.load(fp)

for category, links in grouped_links.items():
    for link in links:
        sess = requests.Session()
        