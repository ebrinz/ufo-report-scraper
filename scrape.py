import json
import re
import urllib.request
from bs4 import BeautifulSoup

def manage_index(index):
    output = []
    return output

def build_data(index=0):
    base_url = 'http://www.nuforc.org/webreports/ndxevent.html'
    one_report = parse_report('http://www.nuforc.org/webreports/162/S162245.html')
    print(one_report)

def parse_report(url):
    report = {}
    # grab report id from url
    report['report_id'] = url.rsplit('/', 1)[-1].split('.')[0]
    # grab report page
    raw_page = urllib.request.urlopen(url)
    page_bytes = raw_page.read()
    report_page = page_bytes.decode("utf8")
    raw_page.close()
    # scrape table
    table_data = []
    soup = BeautifulSoup(report_page, 'lxml')
    table = soup.table
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
    build_data()