"""
This script retrieves all jobs on glassdoor
"""
import requests
from bs4 import BeautifulSoup
import re
import IPython
import pandas as pd
import time
import json
from random import randint
import os


website = "https://www.glassdoor.com"
job_url = "https://www.glassdoor.com/sitedirectory/title-jobs.htm"
headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36"}

login_url = "https://www.glassdoor.com/profile/login_input.htm"
with open("login_data.json") as fp:
    login_data = json.load(fp)

# login here doesn't work
sess = requests.Session()
# response = sess.get(login_url, headers=headers)
# soup = BeautifulSoup(response.text, 'html.parser').text
# template = r'"gdToken":"([^"]*)"'
# token_text = re.search(template, soup, flags=re.MULTILINE).groups()[0]
# token = token_text.split(":")[0]
# login_data["gdToken"] = token
# headers["Authorization"] = token
# sess.post(login_url, data=login_data, headers=headers)

# response = sess.get(login_url, headers=headers)
# soup = BeautifulSoup(response.text, 'html.parser')
# with open("text.html", "w") as f:
#     print(soup.prettify(), file=f)
#
# IPython.embed()


response = sess.get(job_url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')
target = r'/sitedirectory/title-jobs/(.*?).htm'
categories = soup.find_all('a', href=re.compile(r'/sitedirectory/title-jobs/.*'))

job_template = r"/Job/(.*?)-jobs-(.*?).htm"
salary_template = "/Salaries/{job_name}-salary-{job_srch}.htm"
set_scraped_file = "job_salary_links.txt"

with open(set_scraped_file, "w+"):
    pass

with open(set_scraped_file, "r") as fscrap:
    scraped_set = set(fscrap.readlines())

print(scraped_set)

all_job_names = set()
with open(set_scraped_file, "a") as fscrap:
    for category in categories:
        link = website + category["href"]
        name = category.text
        if name in scraped_set:
            continue
        ipage = 1
        print("Category: " + name)

        job_reps = sess.get(link, headers=headers)
        time.sleep(randint(1, 3))
        job_soup = BeautifulSoup(job_reps.text, 'html.parser')
        job_positions = job_soup.find_all('a', href=re.compile(r"/sitedirectory/title-jobs/.*_P\d+.htm"))

        if not job_positions:
            npage = 1
        else:
            npage = max([int(position.text) if position.text.isdigit() else -1 for position in job_positions])
        for ipage in range(1, npage+1):
            print("Page: " + str(ipage))
            job_reps = sess.get(link, headers=headers)
            if job_reps.status_code != 200:
                print("cannot open " + link)
                break
            time.sleep(randint(1, 3))
            job_soup = BeautifulSoup(job_reps.text, 'html.parser')
            job_positions = job_soup.find_all('a', href=re.compile(r'/Job/.*-jobs-.*'))

            if not job_positions:
                print("cannot find jobs on " + link)
                break
            else:
                for job_position in job_positions:
                    # try:
                    # initial a new session every single time
                    sess = requests.Session()
                    job_name, job_srch = re.match(job_template, job_position["href"]).groups()
                    print(job_name + " has started.")

                    # if job_name in all_job_names:
                    #     IPython.embed()
                    # else:
                    #     all_job_names.add(job_name)

                    this_job_url = website + salary_template.format(job_name=job_name, job_srch=job_srch)

                    if this_job_url in scraped_set:
                        continue
                    print(job_position.text + " is done.")
                    scraped_set.add(this_job_url)
                    fscrap.write(this_job_url + "\n")

                    # except:
                    #     print(job_position.text + " failed.")
                    #     pass
                ipage = ipage + 1
                link = website + category["href"][:-4] + "_P" + str(ipage) + ".htm"

            scraped_set.add(name)
            fscrap.write(name + "\n")

        print(name + " is done.")

# IPython.embed()