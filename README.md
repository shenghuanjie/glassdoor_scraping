## Scraping salary information from glassdoor
A very simple script using requests, beautifulsoup(bs4), scrapy

### installation

1. Install (miniconda)[https://docs.conda.io/en/latest/miniconda.html]
2. Install packages in requirements.yml
```
conda env update -f=requirements.yml
```
3. Download correct chrome drive if provided ones are not working
4. prepare your json files in `config/jobs_of_interest.json`
5. run script `glassdoor_get_salary_of_jobs_locations_json.py`
```
python glassdoor_get_salary_of_jobs_locations_json.py
```
