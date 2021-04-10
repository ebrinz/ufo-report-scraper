import json
import re
import os
import time

import transformers as tx

INPUT_DIR= 'data/raw_month_data/'
OUTPUT_DIR= 'data/processed_month_data/'

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
            output.append(filename)
    return output

def process_pipeline(data):
    p_report = processed_report()
    p_report['report_id'] = data['report_id']
    p_report['occurred'] = tx.format_timestamp(data['occurred'])
    p_report['reported'] = tx.format_timestamp(data['reported'])
    p_report['location'] = tx.format_location(data['location'])
    p_report['shape'] = tx.format_shape(data['shape'])
    p_report['duration'] = tx.format_duration(data['duration'])
    print(p_report)
    return p_report


def execute():
    if not os.path.exists(f'{OUTPUT_DIR}'):
        os.makedirs(f'{OUTPUT_DIR}')
    files = get_files()

    # for file in files....
    with open(f'{INPUT_DIR}{files[-1]}') as f:
        filename = f'{OUTPUT_DIR}{files[-1]}.json'
        raw_reports = json.load(f)
        processed_reports = []
        for raw_report in raw_reports:
            processed_report = process_pipeline(raw_report)
            processed_reports.append(processed_report)
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(processed_reports, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    execute()