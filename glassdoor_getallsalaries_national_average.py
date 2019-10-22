"""
This script retrieves all citys on glassdoor
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
location_url = "https://www.glassdoor.com/sitedirectory/title-jobs.htm"
headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36"}

login_url = "https://www.glassdoor.com/profile/login_input.htm"
with open("login_data.json") as fp:
    login_data = json.load(fp)

# login here
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


response = sess.get(location_url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')
target = r'/sitedirectory/title-jobs/(.*?).htm'
categories = soup.find_all('a', href=re.compile(r'/sitedirectory/title-jobs/.*'))

df_file = "glassdoor_salary_list.tsv"
if os.path.isfile(df_file):
    df = pd.read_csv(df_file, sep="\t", index_col=False, header=0)
else:
    df = pd.DataFrame(columns=["job", "name", "srch", "link",
                               "AveragePay", "MinPay", "MaxPay",
                               "AverageAdditional", "MinAdditional", "MaxAdditional",
                               "AveragePayRaw", "MinPayRaw", "MaxPayRaw",
                               "AdditionalCashRaw", "AdditionalRangeRaw"])
icity = len(df.index)
job_template = r"/Job/(.*?)-jobs-(.*?).htm"
salary_template = "/Salaries/{job_name}-salary-{job_srch}.htm"
set_scraped_file = "job_salary_links.txt"

with open(set_scraped_file, "w+"):
    pass


with open(set_scraped_file, "r+") as fscrap:
    scraped_link_set = set(fscrap.readlines())
    new_link_list = []
    for category in categories:
        link = website + category["href"]
        name = category.text
        ipage = 1
        print(name)
        while True:
            print(ipage)
            job_reps = sess.get(link, headers=headers)
            if job_reps.status_code != 200:
                print("cannot open " + link)
                break
            time.sleep(randint(1, 3))
            job_soup = BeautifulSoup(job_reps.text, 'html.parser')
            job_positions = job_soup.find_all('a', href=re.compile(r'/Job/.*-jobs-.*'))
            for job_position in job_positions:
                # try:
                # initial a new session every single time
                sess = requests.Session()
                job_name, job_srch = re.match(job_template, job_position["href"]).groups()
                print(job_name + " has started.")
                this_job_url = website + salary_template.format(job_name=job_name, job_srch=job_srch)

                if this_job_url in scraped_link_set:
                    continue

                this_job_salary = sess.get(this_job_url, headers=headers)
                time.sleep(randint(1, 5))
                this_job_soup = BeautifulSoup(this_job_salary.text, 'html.parser')
                # print(this_job_soup.prettify())

                # get salary
                average_salary = this_job_soup.find(attrs={"data-test": "AveragePay"}).text
                average_salary_int = int(''.join([n for n in average_salary if n.isdigit()]))
                if 'K' in average_salary:
                    average_salary_int = average_salary_int * 1000

                min_salary = this_job_soup.find(attrs={"data-key": "0"}).text
                min_salary_int = int(''.join([n for n in min_salary if n.isdigit()]))
                if 'K' in min_salary:
                    min_salary_int = min_salary_int * 1000

                max_salary = this_job_soup.find(attrs={"data-key": "9"}).text
                max_salary_int = int(''.join([n for n in max_salary if n.isdigit()]))
                if 'K' in max_salary:
                    max_salary_int = max_salary_int * 1000

                additional_pay = this_job_soup.find_all(class_="occMedianModule__AdditionalCompensationStyle__amount")
                additional_average = additional_pay[0].text
                additional_average_int = int(''.join([n for n in additional_average if n.isdigit()]))
                if 'K' in additional_average:
                    additional_average_int = additional_average_int * 1000

                additional_range = additional_pay[1].text
                additional_range_array = additional_range.split('-')
                additional_min = additional_range_array[0]
                additional_min_int = int(''.join([n for n in additional_min if n.isdigit()]))
                if 'K' in additional_min:
                    additional_min_int = additional_min_int * 1000

                additional_max = additional_range_array[1]
                additional_max_int = int(''.join([n for n in additional_max if n.isdigit()]))
                if 'K' in additional_min:
                    additional_max_int = additional_max_int * 1000

                # this_job_soup.
                df.loc[icity] = [job_position.text, job_name, job_srch, this_job_url,
                                 average_salary_int, min_salary_int, max_salary_int,
                                 additional_average_int, additional_min_int, additional_max_int,
                                 average_salary, min_salary, max_salary,
                                 additional_average, additional_range]
                icity = icity + 1
                print(job_position.text + " is done.")
                scraped_link_set.add(this_job_url)
                new_link_list.append(this_job_url)

                # except:
                #     print(job_position.text + " failed.")
                #     pass
            ipage = ipage + 1
            link = website + category["href"][:-4] + "_P" + str(ipage) + ".htm"

        print(name + " is done.")
        for my_link in new_link_list:
            fscrap.write(my_link)
        df.to_csv(df_file, sep="\t", header=True, index=False)

df.to_csv(df_file, sep="\t", header=True, index=False)

IPython.embed()