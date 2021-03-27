import json
import re
import os
import urllib.request
import requests
from bs4 import BeautifulSoup

def parse_site(index=0):
    if not os.path.exists('data/raw_month_data'):
        os.makedirs('data/raw_month_data')
    base_url = 'http://www.nuforc.org/webreports/'
    starting_slug = 'ndxevent.html'
    output = []
    months_page = requests.get(base_url + starting_slug).content
    month_urls = []
    soup_months = BeautifulSoup(months_page, 'html.parser')
    months = soup_months.find_all('td')
    for month in months:
        if month.find('a', href=True):
            month_urls.append(month.a['href'])
    for month in month_urls:
        filename = 'data/raw_month_data/' + os.path.splitext(month)[0] + '.json'
        file_index = []
        if os.path.exists(filename):
            with open(filename) as f:
                file_contents = json.load(f)
            for report in file_contents:
                file_index.append(report['report_id'])
        else:
            file_contents = []
        reports_page = requests.get(base_url + month).content
        soup_reports = BeautifulSoup(reports_page, 'html.parser')
        table = soup_reports.find('tbody')
        a = table.find_all('a', href=True)
        report_urls = []
        for href in a:
            report_id = href['href'].rsplit('/', 1)[-1].split('.')[0]
            if report_id not in file_index:
                report_urls.append(href['href'])
        for report in report_urls:
            file_contents.append(parse_report(base_url+report))
            print('consumed report: ' + os.path.splitext(month)[0] + ': ' + report)
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(file_contents, f, ensure_ascii=False, indent=4)
            print('file built at ' + filename)
    

def parse_report(url):
    report = {}
    report['report_id'] = url.rsplit('/', 1)[-1].split('.')[0]
    report_page = requests.get(url).content
    table_data = []
    soup_report = BeautifulSoup(report_page, 'lxml')
    table = soup_report.table
    rows = table.find_all('tr')
    fields = rows[1].td.font
    field_list = []
    for elem in fields.descendants:
        if elem.find('br'):
            test = re.search('\(([^\)]+)\)', elem)
            if test:
                field = parse_field(re.sub('[()]', '', elem[test.start():]))
                report[field['category']] = field['content']
                field = parse_field(elem[:test.start()])
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
    parse_site()