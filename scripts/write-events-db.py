# coding: utf-8

import os
import re
import sys
import csv
import json
import urllib2
import unicodedata


USAGE = 'USAGE: python %s <json url>' % sys.argv[0]

JSON_HEADERS = [
    'id',
    'long_title',
    'year',
    'city',
    'country',
]

CSV_HEADERS = [
    'id',
    'title',
    'year',
    'city',
    'country',
]

IDS = {}

OUTPUT_FILENAME = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '../data/events.csv'
)


def parse_params():
    try:
        return sys.argv[1]
    except IndexError:
        print USAGE
        sys.exit(-1)


def read_json(url):
    response = urllib2.urlopen(url)
    data = json.loads(response.read()).values()

    return data


def remove_diacritics(s):
    return ''.join(
        c for c in unicodedata.normalize('NFD', s)
        if unicodedata.category(c) != 'Mn'
    )


def build_id(entry):
    city = remove_diacritics(entry['city'])
    city = re.sub(ur'\W+', '-', city, re.U).lower()
    _id = '%s-%s' % (city, entry['year'])

    try:
        IDS[_id]['count'] += 1
    except:
        IDS[_id] = {
            'count': 1,
            'usage': 0
        }

    return _id


def fix_id(entry):
    _id = entry['id']
    id_entry = IDS[_id]

    if id_entry['count'] > 1:
        _id += '%s' % chr(ord('a') + id_entry['usage'])
        id_entry['usage'] += 1

    return _id


def cmp_entries(a, b):
    ayear = int(a['year'])
    byear = int(b['year'])

    if ayear != byear:
        return cmp(ayear, byear)
    
    return cmp(a['id'], b['id'])


def serialize_entry(entry):
    return [entry[key] for key in JSON_HEADERS]


def process_data(data):
    # Attach id
    for entry in data:
        entry['id'] = build_id(entry)

    # Handle repeated ids
    for entry in data:
        entry['id'] = fix_id(entry)

    # Order data first by year and then by id
    data = sorted(data, cmp=cmp_entries)

    # Put data in the correct order
    return [serialize_entry(entry) for entry in data]


def dump_entry(entry):
    return [v.encode('utf-8') for v in entry]


def write_csv(data, filename):
    with open(filename, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(CSV_HEADERS)

        for entry in data:
            writer.writerow(dump_entry(entry))


def main():
    url = parse_params()
    data = read_json(url)
    data = process_data(data)
    write_csv(data, OUTPUT_FILENAME)


if __name__ == '__main__':
    main()
