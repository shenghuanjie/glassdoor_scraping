import json
import requests
from bs4 import BeautifulSoup
import re
import os
import pandas as pd
import time
from random import randint
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import IPython


json_file = "config/jobs_of_interest.json"
with open(json_file) as fp:
    job_location_info = json.load(fp)

last_url = "https://www.glassdoor.com/Salaries/san-francisco-data-scientist-salary-SRCH_IL.0,13_IM759_KO14,28.htm"
login_url = "https://www.glassdoor.com/profile/login_input.htm"
with open("config/login_data.json") as fp:
     login_data = json.load(fp)

if os.name == 'nt':
    chrome_path = "chrome\\chromedriver_win32\\chromedriver.exe"
elif os.name == 'posix':
    chrome_path = "chrome/chromedriver_linux64/chromedriver"
elif os.name == 'java':
    chrome_path = "chrome/chromedriver_lmac64/chromedriver"
else:
    raise OSError

# load existing data:
df_file = "output/glassdoor_salary_by_job_location_list.tsv"
nbins = 10
headers = ["job", "location", "link",
            "AveragePay", "MinPay", "MaxPay",
            "AverageAdditional", "MinAdditional", "MaxAdditional",
            "AveragePayRaw", "MinPayRaw", "MaxPayRaw",
            "AdditionalCashRaw", "AdditionalRangeRaw"] + ["HistBin" + str(nbin+1) for nbin in range(nbins)]
if os.path.isfile(df_file):
    df = pd.read_csv(df_file, sep="\t", index_col=False, header=0)
else:

    df = pd.DataFrame(columns=headers)
icity = len(df.index)


chrome_options = webdriver.ChromeOptions()
# chrome_options.add_argument("--incognito")
chrome_options.add_argument("--start-maximized")

# log in first
browser = webdriver.Chrome(chrome_path, chrome_options=chrome_options)
browser.get(login_url)
username_box = browser.find_element_by_id("userEmail")
username_box.send_keys(login_data["username"])
password_box = browser.find_element_by_id("userPassword")
password_box.send_keys(login_data["password"])
submit_button = browser.find_element_by_xpath("//button[@type='submit']")
submit_button.click()
time.sleep(5)

for job in job_location_info["jobs"]:
    for location in job_location_info["locations"]:
        failed = True
        while failed:
            browser.get(last_url)
            try:
                job_box = browser.find_element_by_id("sc.keyword")
                job_box.send_keys(Keys.CONTROL, "a")
                job_box.send_keys(job)

                location_box = browser.find_element_by_id("sc.location")
                location_box.send_keys(Keys.CONTROL, "a")
                location_box.send_keys(location)

                search_button = browser.find_element_by_id("HeroSearchButton")
                search_button.click()
                failed = False

            except Exception:
                print(job + " in " + location + " has filed")
                print("attemp to log in again")
                browser.get(login_url)
                username_box = browser.find_element_by_id("userEmail")
                username_box.send_keys(login_data["username"])
                password_box = browser.find_element_by_id("userPassword")
                password_box.send_keys(login_data["password"])
                submit_button = browser.find_element_by_xpath("//button[@type='submit']")
                submit_button.click()

        time.sleep(randint(5, 10))

        try:
            average_salary = browser.find_element_by_xpath("//span[@data-test='AveragePay']").text
            average_salary_int = int(''.join([n for n in average_salary if n.isdigit()]))
            if 'K' in average_salary:
                average_salary_int = average_salary_int * 1000
        except Exception:
            print(job + " in " + location + " average salary failed")
            average_salary = "NaN"
            average_salary_int = np.nan

        try:
            min_salary = browser.find_element_by_xpath("//div[@data-key='0']").text
            min_salary_int = int(''.join([n for n in min_salary if n.isdigit()]))
            if 'K' in min_salary:
                min_salary_int = min_salary_int * 1000
        except Exception:
            print(job + " in " + location + " minimum salary failed")
            min_salary = "NaN"
            min_salary_int = np.nan

        try:
            max_salary = browser.find_element_by_xpath("//div[@data-key='9']").text
            max_salary_int = int(''.join([n for n in max_salary if n.isdigit()]))
            if 'K' in max_salary:
                max_salary_int = max_salary_int * 1000
        except Exception:
            print(job + " in " + location + " maximum salary failed")
            max_salary = "NaN"
            max_salary_int = np.nan


        # get histogram:
        try:
            histogram_bins = browser.find_elements_by_class_name("common__HistogramStyle__bar")
            all_bins = []
            for histogram_bin in histogram_bins:
                this_bin = histogram_bin.get_attribute("style")
                this_bin = float(''.join([n for n in this_bin if n.isdigit() or n == '.'])) / 100
                all_bins.append(this_bin)
            if len(all_bins) != nbins:
                all_bins = all_bins + [np.nan] * nbins
                all_bins = all_bins[0:10]
        except Exception:
            print(job + " in " + location + " histogram failed")
            all_bins = [np.nan] * nbins
        sum_all_bins = np.nansum(all_bins)
        if sum_all_bins > 0:
            all_bins = [this_bin / sum_all_bins for this_bin in all_bins]

        try:
            additional_pay = browser.find_elements_by_class_name("occMedianModule__AdditionalCompensationStyle__amount")
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

        except Exception:
            print(job + " in " + location + " additional pay failed")
            additional_average = "NaN"
            additional_average_int = np.nan

            additional_range = "NaN - NaN"
            additional_min_int = np.nan
            additional_max_int = np.nan

        last_url = browser.current_url
        scraped_data = [job, location, browser.current_url,
                        average_salary_int, min_salary_int, max_salary_int,
                        additional_average_int, additional_min_int, additional_max_int,
                        average_salary, min_salary, max_salary,
                        additional_average, additional_range] + all_bins
        df = df.append(dict(zip(headers, scraped_data)), ignore_index=True)
        df.to_csv(df_file, sep="\t", index=False, header=True)

browser.close()

# IPython.embed()