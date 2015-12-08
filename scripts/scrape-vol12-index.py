# coding: utf-8

from bs4 import BeautifulSoup
from datetime import datetime
from urlparse import urljoin
import urllib2
import csv
import re
import os


URL = 'http://www.iisd.ca/enb/vol12/'

RE_SINGLE_MONTH = re.compile(r'(\d{1,2})-(\d{1,2}) (\w+) (\d{4})')
RE_TWO_MONTHS = re.compile(r'(\d{1,2}) (\w+) - (\d{1,2}) (\w+) (\d{4})')

MONTHS = [
    'january', 'february','march', 'april', 'may', 'june', 'july',
    'august', 'september', 'october', 'november', 'december'
]


def make_soup_from_url(url):
    response = urllib2.urlopen(url)
    text = response.read()
    return BeautifulSoup(text, 'lxml')


def process_soup(soup, url):
    events = []
    documents = []

    table = soup.find('table', class_='volumes')
    rows = table.find_all('tr')
    event_id = None

    for row in rows:
        th = row.find('th')

        if th:
            a = th.find('a')
            h3 = th.find('h3')

            if a and not h3:
                event_id = a['name']
            elif h3 and (not a or 'href' in a.attrs):
                events.append(process_event(th, h3, event_id))

        else:
            documents.append(process_document(row, event_id, url))
            
    return events, documents


def process_event(th, h3, event_id):
    short_name, raw_date, raw_location = th.contents[1].split(' | ')

    name = h3.text
    city, country = parse_location(raw_location)
    start_date, end_date, no_day = parse_date_interval(raw_date)

    return {
       'id': event_id,
       'short_name': short_name,
       'name': name,
       'start_date': serialize_date(start_date, no_day),
       'end_date': serialize_date(end_date, no_day),
       'city': city,
       'country': country
    }


def process_document(row, event_id, url):
    raw_issue, raw_date, raw_pdf, raw_html = row.find_all('td')

    issue = parse_issue(raw_issue)
    date = parse_date(raw_date)
    pdf = parse_url(raw_pdf, url)
    html = parse_url(raw_html, url)

    return {
        'event_id': event_id,
        'id': issue,
        'date': serialize_date(date),
        'pdf': pdf,
        'html': html  
    }


def parse_issue(raw):
    return int(re.search(r'Issue# (\d+)', raw.text, re.I).group(1))


def parse_url(raw, base):
    return urljoin(base, raw.a['href'])


def parse_location(raw):
    try:
        res = raw.split(', ')
        return res[0], res[1]
    except IndexError:
        return None, None


def parse_date(raw):
    try:
        date = raw.text.lower()
        date = datetime.strptime(date, '%d %B %Y')
    except ValueError:
        pass

    return date


def parse_date_interval(raw):
    # 9 October 1999
    try:
        date = datetime.strptime(raw, '%d %B %Y')
        return date, date, False
    except ValueError:
        pass

    # 27-31 October 2014
    try:
        d1, d2, m, y = RE_SINGLE_MONTH.match(raw).groups()
        d1, d2, y = int(d1), int(d2), int(y)
        m = MONTHS.index(m.lower()) + 1
        return datetime(y, m, d1), datetime(y, m, d2), False
    except AttributeError:
        pass

    # 28 March - 7 April 1995
    try:
        d1, m1, d2, m2, y = RE_TWO_MONTHS.match(raw).groups()
        d1, d2, y = int(d1), int(d2), int(y)
        m1, m2 = MONTHS.index(m1.lower()) + 1, MONTHS.index(m2.lower()) + 1
        return datetime(y, m1, d1), datetime(y, m2, d2), False
    except AttributeError:
        pass

    # December 1995
    date = datetime.strptime(raw, '%B %Y')
    return date, date, True


def serialize_date(d, no_day=False):
    if hasattr(d, 'date'):
        d = d.date().isoformat()

        if no_day:
            return d[:-3]
        else:
            return d
    else:
        return d.lower()


def write_csv(events, documents):
    evfn = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        '../data/events.csv'
    )

    dcfn = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        '../data/documents.csv'
    )

    EVENTS_HEADERS = [
        'id', 'short_name', 'name', 'start_date', 'end_date', 'city', 'country'
    ]

    DOCUMENTS_HEADERS = [
        'id', 'event_id', 'date', 'pdf', 'html'
    ]

    _write_csv(evfn, events, EVENTS_HEADERS)
    _write_csv(dcfn, documents, DOCUMENTS_HEADERS)


def _write_csv(filename, data, headers):
    with open(filename, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(headers)

        for entry in data:
            entry = serialize_entry(entry, headers)
            writer.writerow(dump_entry(entry))


def serialize_entry(entry, headers):
    return [entry[key] for key in headers]


def dump_entry(entry):
    return [unicode(v).encode('utf-8') if v else '' for v in entry]


def main():
    soup = make_soup_from_url(URL)
    events, documents = process_soup(soup, URL)
    write_csv(events, documents)


if __name__ == '__main__':
    main()
