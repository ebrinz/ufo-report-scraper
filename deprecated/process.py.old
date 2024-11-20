#!/usr/bin/env python3

# import json
# import re
# import os
# import time

# import transformers as tx

# INPUT_DIR= 'data/raw_month_data/'
# OUTPUT_DIR= 'data/processed_month_data/'

# def processed_report():
#     return dict.fromkeys([
#         'report_id',
#         'occurred',
#         'reported',
#         'location',
#         'shape',
#         'duration',
#     ])

# def get_files():
#     output = []
#     for root, dirs, files in os.walk(INPUT_DIR):
#         for filename in files:
#             output.append(filename)
#     return output

# def process_pipeline(data):
#     p_report = processed_report()
#     p_report['report_id'] = data['report_id']
#     p_report['occurred'] = {'scrape': data['occurred'], 'format': tx.format_timestamp(data['occurred'])}
#     p_report['reported'] = {'scrape': data['reported'], 'format': tx.format_timestamp(data['reported'])}
#     p_report['location'] = {'scrape': data['location'], 'format': tx.format_location(data['location'])}
#     p_report['shape'] = {'scrape': data['shape'], 'format': tx.format_shape(data['shape'])}
#     p_report['duration'] = {'scrape': data['duration'], 'format': tx.format_duration(data['duration'])}
#     # print(p_report)
#     return p_report


# def execute():
#     if not os.path.exists(f'{OUTPUT_DIR}'):
#         os.makedirs(f'{OUTPUT_DIR}')
#     files = get_files()

#     # only looking at one file rn ([-1])
#     # in future add: for file in files....
#     with open(f'{INPUT_DIR}{files[-1]}') as f:
#         filename = f'{OUTPUT_DIR}{files[-1]}'
#         raw_reports = json.load(f)
#         processed_reports = []
#         for raw_report in raw_reports:
#             processed_report = process_pipeline(raw_report)
#             processed_reports.append(processed_report)
#         with open(filename, 'w', encoding='utf-8') as f:
#             json.dump(processed_reports, f, ensure_ascii=False, indent=4)

# if __name__ == "__main__":
#     execute()



####### going to use openAI code below in a pinch for time (above commented-out code is older original)

import json
import os
import logging

import transformers as tx

# Set up logging configuration
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

INPUT_DIR = 'data/raw_month_data/'
OUTPUT_DIR = 'data/processed_month_data/'

def processed_report():
    return dict.fromkeys([
        'report_id',
        'occurred',
        'reported',
        'location',
        'shape',
        'duration',
    ])

def get_files():
    output = []
    for root, dirs, files in os.walk(INPUT_DIR):
        for filename in files:
            output.append(os.path.join(root, filename))
    logging.debug(f"Found {len(output)} files in {INPUT_DIR}")
    return output

def process_pipeline(data):
    p_report = processed_report()
    p_report['report_id'] = data['report_id']
    p_report['occurred'] = {'scrape': data['occurred'], 'format': tx.format_timestamp(data['occurred'])}
    p_report['reported'] = {'scrape': data['reported'], 'format': tx.format_timestamp(data['reported'])}
    p_report['location'] = {'scrape': data['location'], 'format': tx.format_location(data['location'])}
    p_report['shape'] = {'scrape': data['shape'], 'format': tx.format_shape(data['shape'])}
    p_report['duration'] = {'scrape': data['duration'], 'format': tx.format_duration(data['duration'])}
    p_report['description'] = {'scrape': data['description'], 'cleaned': tx.clean_text(data['description'])}
    
    logging.debug(f"Processed report ID: {p_report['report_id']}")
    return p_report

def execute():
    if not os.path.exists(f'{OUTPUT_DIR}'):
        os.makedirs(f'{OUTPUT_DIR}')
        logging.info(f"Created output directory: {OUTPUT_DIR}")
    
    files = get_files()

    for file in files:
        logging.info(f"Processing file: {file}")
        try:
            with open(file, 'r', encoding='utf-8') as f:
                raw_reports = json.load(f)
                processed_reports = []
                for raw_report in raw_reports:
                    processed_report = process_pipeline(raw_report)
                    processed_reports.append(processed_report)
                
                # Save processed report to corresponding file in OUTPUT_DIR
                output_filename = os.path.join(OUTPUT_DIR, os.path.basename(file))  # Save with the same filename
                with open(output_filename, 'w', encoding='utf-8') as outfile:
                    json.dump(processed_reports, outfile, ensure_ascii=False, indent=4)
                logging.info(f"Processed and saved file: {output_filename}")
        
        except Exception as e:
            logging.error(f"Failed to process file {file}. Error: {str(e)}")

if __name__ == "__main__":
    execute()
