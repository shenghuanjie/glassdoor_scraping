# convert 2 tsv files with location and job information into 1 json file

import pandas as pd
import json


location_file = "output/glassdoor_city_list.tsv"
job_file = "output/glassdoor_salary_list.tsv"
json_file = "config/jobs_of_interest.json"

df_location = pd.read_csv(location_file, sep="\t", index_col=False, header=0)
df_job = pd.read_csv(job_file, sep="\t", index_col=False, header=0)

locations = list(df_location.iloc[:, 0].values)
jobs = list(df_job.iloc[:, 0].values)

with open(json_file, "w+") as fp:
    json.dump({"jobs": jobs, "locations": locations}, fp, indent=4, sort_keys=True)
