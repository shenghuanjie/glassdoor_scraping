import json
import requests
from bs4 import BeautifulSoup
import re
import os
import pandas as pd
import time
from random import randint
import numpy as np
import IPython

json_file = "config/job_salary_links.json"
with open(json_file) as fp:
    grouped_links = json.load(fp)

df_file = "output/glassdoor_salary_list.tsv"
if os.path.isfile(df_file):
    df = pd.read_csv(df_file, sep="\t", index_col=False, header=0)
else:
    df = pd.DataFrame(columns=["name", "category", "srch", "link",
                               "AveragePay", "MinPay", "MaxPay",
                               "AverageAdditional", "MinAdditional", "MaxAdditional",
                               "AveragePayRaw", "MinPayRaw", "MaxPayRaw",
                               "AdditionalCashRaw", "AdditionalRangeRaw"])
icity = len(df.index)
headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36"}

job_template = r"https://www.glassdoor.com/Salaries/(.*?)-salary-(.*?).htm"

save_count = 20
icount = 0

for category, links in grouped_links.items():
    for this_job_url in links:
        if this_job_url in df["link"]:
            print(this_job_url + " has been done. Skipping...")
            continue
        print(this_job_url + " has started.")
        sess = requests.Session()
        # IPython.embed()
        job_name, job_srch = re.match(job_template, this_job_url).groups()
        this_job_salary = sess.get(this_job_url, headers=headers)
        time.sleep(randint(1, 5))
        this_job_soup = BeautifulSoup(this_job_salary.text, 'html.parser')

        # get salary
        average_salary_field = this_job_soup.find(attrs={"data-test": "AveragePay"})

        if not average_salary_field:
            average_salary = "NaN"
            average_salary_int = np.nan
            min_salary = "NaN"
            min_salary_int = np.nan
            max_salary = "NaN"
            max_salary_int = np.nan
        else:
            average_salary = average_salary_field.text
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
        if not additional_pay:
            additional_average = "NaN"
            additional_average_int = np.nan

            additional_range = "NaN - NaN"
            additional_min_int = np.nan
            additional_max_int = np.nan
        else:
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
        df.loc[icity] = [job_name, category, job_srch, this_job_url,
                         average_salary_int, min_salary_int, max_salary_int,
                         additional_average_int, additional_min_int, additional_max_int,
                         average_salary, min_salary, max_salary,
                         additional_average, additional_range]
        icity = icity + 1
        print(this_job_url + " is done.\n")
        if icount >= save_count:
            df.to_csv(df_file, sep="\t", header=True, index=False)
            print(df_file + " has been saved")
            icount = 0
        else:
            icount += 1
