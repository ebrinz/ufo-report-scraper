import json
import re
import os
import time
import requests
import traceback
from bs4 import BeautifulSoup

def report_schema():
    return dict.fromkeys([
        "report_id",
        "entered",
        "occurred",
        "reported",
        "posted",
        "location",
        "shape",
        "duration",
        "description",
        "status_code"
    ])

def parse_site():
    base_url = 'http://www.nuforc.org/webreports/'
    starting_slug = 'ndxevent.html'
    if not os.path.exists('data/raw_month_data'):
        os.makedirs('data/raw_month_data')
    months_page = requests.get(base_url + starting_slug).content
    soup_months = BeautifulSoup(months_page, 'html.parser')
    months = soup_months.find_all('td')
    for month in months:
        if month.find('a', href=True):
            parse_monthly_report_list(month.a['href'])


def parse_monthly_report_list(month_slug):
    base_url = 'http://www.nuforc.org/webreports/'
    month_name = month_slug.split('.')[0]
    filename = f'data/raw_month_data/{month_name}.json'
    file_index = []
    if os.path.exists(filename):
        with open(filename) as f:
            file_contents = json.load(f)
        for report in file_contents:
            file_index.append(report['report_id'])
    else:
        file_contents = []
    reports_page = requests.get(base_url + month_slug).content
    soup_reports = BeautifulSoup(reports_page, 'html.parser')
    table = soup_reports.find('tbody')
    a = table.find_all('a', href=True)
    report_urls = []
    for href in a:
        report_id = href['href'].rsplit('/', 1)[-1].split('.')[0]
        if report_id not in file_index:
            report_urls.append(href['href'])
    for report in report_urls:
        print(f'consuming report: {month_name}: {report}')
        file_contents.append(parse_report(base_url+report))
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(file_contents, f, ensure_ascii=False, indent=4)
        print(f'file built at {filename}')
    

def parse_report(url):
    report = report_schema()
    report['report_id'] = url.rsplit('/', 1)[-1].split('.')[0]
    report_request = requests.get(url)
    report['status_code'] = report_request.status_code
    # (if) handle broken links
    if report['status_code'] != 200:
        return report
    report_page = report_request.content
    soup_report = BeautifulSoup(report_page, 'lxml')
    # (if) edge case handler for empty body or no table
    if soup_report.find('body') is None or \
        soup_report.body.find('table') is None:
        report['status_code'] = 418
        return report
    table = soup_report.table
    rows = table.find_all('tr')
    fields = rows[1].td.font
    field_list = []
    for elem in fields.descendants:
        if elem.find('br'):
            # (if) handle possible double field in Occurred/Entry
            reg_test = re.search('\(([^\)]+)\)', elem)
            str_test = elem[:5].lower() == 'occur'
            if reg_test and str_test:
                field = parse_field(re.sub('[()]', '', elem[reg_test.start():]))
                report[field['category']] = field['content']
                field = parse_field(elem[:reg_test.start()])
                report[field['category']] = field['content']
            else:
                field = parse_field(elem)
                report[field['category']] = field['content']
    description = rows[2].td.font.get_text()
    report['description'] = description.replace('"', '\\"')
    return report

def parse_field(input):
    parsed = input.split(':', 1)
    output = { 
        'category': parsed[0].split(' ')[0].lower(), 
        'content': parsed[1].strip()
    }
    return output

if __name__ == "__main__":
    start = time.time()
    start_stamp = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(start))
    print(f'job starts at GMT {start_stamp}')
    try:
        parse_site()
        end = time.time() - start
        end_stamp = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(end))
        print(f'job finishes at {end_stamp}')
        print(f'execution time: {end}')
    except Exception as e:
        end = time.time() - start
        end_stamp = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(end))
        print(f'job ends with fail at {end_stamp}')
        print(f'execution time: {end}')
        print(f'{traceback.print_exc()}')