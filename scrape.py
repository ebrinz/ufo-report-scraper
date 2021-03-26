import json
import re
import os
import urllib.request
import requests
from bs4 import BeautifulSoup

def manage_index(index):
    output = []
    return output

def parse_site(index=0):
    base_url = 'http://www.nuforc.org/webreports/'
    starting_slug = 'ndxevent.html'
    output = []
    # grab  months page
    months_page = requests.get(base_url + starting_slug).content
    # scrape month urls from table
    month_urls = []
    soup_months = BeautifulSoup(months_page, 'html.parser')
    months = soup_months.find_all('td')
    for month in months:
        if month.find('a', href=True):
            month_urls.append(month.a['href'])
    # get report urls from each month
    report_urls = []
    for month in month_urls[0:1]: # release me! ------------------------- * <----
        reports_page = requests.get(base_url + month).content
        soup_reports = BeautifulSoup(reports_page, 'html.parser')
        table = soup_reports.find('tbody')
        a = table.find_all('a', href=True)
        for href in a:
            report_urls.append(href['href'])
    # handle output file
    # with open('raw_reports.json', 'w+') as raw_file:
    #     if os.path.getsize('raw_reports.json') == 0:
    #         reports_array = []
    #     else:
    #         reports_array = json.load(raw_file)
    #     print(reports_array)
    
    for report in report_urls:
        print(parse_report(base_url+report))
    

def parse_report(url):
    report = {}
    # grab report id from url
    report['report_id'] = url.rsplit('/', 1)[-1].split('.')[0]
    # grab report page
    raw_report_page = urllib.request.urlopen(url)
    report_page_bytes = raw_report_page.read()
    report_page = report_page_bytes.decode("utf8")
    raw_report_page.close()
    # scrape table
    table_data = []
    soup_report = BeautifulSoup(report_page, 'lxml')
    table = soup_report.table
    rows = table.find_all('tr')
    # scrape field values in upper tr
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
    # scrape description in lower tr
    report['description'] = rows[2].td.font.get_text()
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