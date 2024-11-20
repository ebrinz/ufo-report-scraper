# NUFORC Data Analysis

This repository was originally created for developing a web scraper to extract data from the NUFORC (National UFO Reporting Center) website. However, due to significant changes in the website's structure in late 2022, the scraper is no longer functional. 

The repository has since been repurposed to analyze NUFORC data collected up until mid-2022. It now focuses on providing tools and methods to explore and gain insights from this data.

---

## Setup Instructions

### 1. Install `pipenv`
Ensure you have `pipenv` installed on your system. You can install it with pip:

```bash
pip install pipenv
```

### 2. Initialize pipenv and ipython kernel

```bash
pipenv --python 3.11
pipenv install ipykernel==6.28.0 python-dotenv==1.0.0
pipenv run python -m ipykernel install --user --name="da_$(basename $(pwd))" --display-name="da_$(basename $(pwd))"
```

### 3. Extract data from .tar file in data/archive

```bash
pipenv run python src/extract_archived_data.py
```

### 4. Set up notbook for notebook

Quit and reopen your text editor and select the kernel and python interpreter dynamically named for this repo


## Sitemap

├── data/ │ ├── archive/ # Contains compressed archived data │ ├── reference/ # Contains reference data │ ├── raw/ # Raw extracted data (after running extract_archived_data.py) │ ├── processed/ # Processed data ├── src/ # Preprocessing scripts ├── notebooks/ # Modeling notebooks ├── db/ # Database-related files ├── README.md # Project documentation