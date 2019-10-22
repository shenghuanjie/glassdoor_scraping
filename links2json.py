import json

link_file = "job_salary_links.txt"
json_file = "job_salary_links.json"

with open(link_file, "r") as fp:
    links = fp.read().splitlines()

grouped_links = dict()
temp_list = []
for link in links:
    if "http" not in link:
        grouped_links[link] = temp_list
        temp_list = []
    else:
        temp_list.append(link)

with open(json_file, "w+") as fp:
    json.dump(grouped_links, fp, indent=4, sort_keys=True)
