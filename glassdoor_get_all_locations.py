"""
This script retrieves all citys on glassdoor
"""
import requests
from bs4 import BeautifulSoup
import re
import IPython
import pandas as pd
import json

website = "https://www.glassdoor.com"
location_url = "https://www.glassdoor.com/sitedirectory/city-jobs.htm"
headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36"}

# log in here
login_url = "https://www.glassdoor.com/profile/login_input.htm"
with open("login_data.json") as fp:
    login_data = json.load(fp)

sess = requests.Session()
response = sess.get(login_url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser').text
template = r'"gdToken":"([^"]*)"'
token = re.search(template, soup, flags=re.MULTILINE).groups()[0]
login_data["gdToken"] = token
sess.post(login_url, data=login_data, headers=headers)

# get location url
response = sess.get(location_url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')
target = r'/sitedirectory/city-jobs/(.*?).htm'
states = soup.find_all('a', href=re.compile(r'/sitedirectory/city-jobs/.*'))

df = pd.DataFrame(columns=["city", "name", "srch", "link"])
icity = 0
city_template = r"/Job/(.*?)-jobs-(.*?)_IC\d+.htm"

for state in states:
    link = website + state["href"]
    name = state.text
    ipage = 1
    while True:
        state_reps = sess.get(link, headers=headers)
        state_soup = BeautifulSoup(state_reps.text, 'html.parser')
        state_cities = soup.find_all('a', href=re.compile(r'/Job/.*-jobs-SRCH.*'))
        for state_city in state_cities:
            city_name, city_srch = re.match(city_template, state_city["href"]).groups()
            df.loc[icity] = [state_city.text, city_name, city_srch, state_city["href"]]
            icity = icity + 1
        ipage = ipage + 1
        link = website + state["href"][:-4] + "_P" + str(ipage) + ".htm"

    print(name + " is done.")

df.to_csv("glassdoor_city_list.tsv", sep="\t", header=True, index=False)

IPython.embed()