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

### 3. Set up notbook for notebook

Quit and reopen your text editor and select the kernel and python interpreter dynamically named for this repo

### 4. Bringup postgres database container

```bash
docker-compose -f db/docker-compose.yml up --build -d
```

### 5. Execute seeding pipeline


This script is designed to process and manage UFO report data by providing a series of modular commands for different pipeline stages. Each stage is controlled via command-line arguments.


Run the script with one or more of the following arguments:

```bash
python seed_pipeline.py --extract --ingest --transform --embed --reference --setup_summary
```

# ingesting and especially transforming take **way too long** right now - will fix soon with bulk insert, etc.

Command-Line Arguments
Argument	Description
```bash
--extract	Extracts data from a tar file in the archive.
--ingest	Seeds the ufo_reports_raw table in the database with raw data from the archive.
--transform	Transforms and formats the raw data into a cleaner state (e.g., for analysis or reporting).
--embed	Creates vectorized embeddings from report descriptions for machine learning or analytics tasks.
--reference	Creates reference tables, such as geographical lookups for enhanced data enrichment.
--setup_summary	Checks previous steps for incomplete or missing data and provides a summary of the pipeline.
```

## Directory Details

- **`data/`**: Houses all data files and subdirectories.
  - **`archive/`**: Contains the original compressed data files.
  - **`reference/`**: Holds lookup and reference tables, such as geographical or metadata files.
  - **`raw/`**: Stores raw data extracted from archives.
  - **`processed/`**: Contains data after preprocessing or transformations.
- **`src/`**: Includes all Python scripts or other code for data preprocessing and pipeline steps.
- **`notebooks/`**: Contains Jupyter notebooks for exploratory data analysis (EDA) and modeling.
- **`db/`**: Files related to database schema, queries, or configuration.
- **`deprecated/`**: There's nothing to see here.
