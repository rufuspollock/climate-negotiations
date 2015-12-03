# coding: utf-8

'''
Example usage:

    python scripts/process.py scraped/1205000e.txt 
'''

import datetime
import os
import sys
import re

baseurl = 'http://www.iisd.ca/vol12/'

# This regular expression can find dates in the following format:
# WEDNESDAY, 29 MARCH 1995
RE_DATE = re.compile(r'''
    (\d{1,2})       # Day
    \s+
    (\w+)           # Month name
    \s+
    (\d{4})         # Year
''', re.I | re.X)

def convert(inpath, outpath=None):
    fileid = os.path.splitext(os.path.basename(inpath))[0]
    print fileid
    if outpath == None:
        outpath = os.path.join('enb', fileid, 'index.md')

    parentdir = os.path.dirname(outpath)
    if not os.path.exists(parentdir):
        os.makedirs(parentdir)

    title, text = txt2markdown(open(inpath))
    fout = open(outpath, 'w')

    # Searches for the date in the title
    try:
        date = RE_DATE.search(title).groups()
        date = datetime.datetime.strptime(' '.join(date), '%d %B %Y')
        date = date.date().isoformat()
    except AttributeError, ValueError:
        date = ''

    fout.write('''---
title: %s
id: %s
url: %s
date: %s
---

''' % (title, fileid, baseurl + fileid, date)
)
    fout.write(text)
    fout.close()

def convertall():
    # TODO: walk through the scraped directory and process all ofthem
    # Before doing this i'd make sure we really have this working well
    pass

def txt2markdown(fileobj):
    def fix(line):
        # Replace sections
        line = line.replace('::H1::', '# ')
        line = line.replace('::H2::', '## ')
        line = line.replace('::H3::', '### ')
        line = line.replace('::TITLE::', '')
        line = line.replace('::BODY::', '')
        line = line.replace('::ABSTRACT::', '')

        # Make paragraphs out of '.§'
        line = line.replace('.\xc2\xa7', '.\n')

        # Remove extra §
        line = line.replace('\xc2\xa7', '')

        # Replace apostrophe
        line = line.replace('\xc2\x92', '\'')

        # Remove tabs
        line = line.replace('\t', '')

        # TODO: handle abstract

        return line.strip().split('\n')

    txt = fileobj.read()
    lines = [ fix(line) for line in txt.split('\n') ]
    lines = [ line for group in lines for line in group ]

    title = lines.pop(0)
    txt = '\n\n'.join(lines)

    return (title, txt)

def test_it():
    path = 'samples/1205000e.txt'
    title, text = txt2markdown(open(path))
    lines = text.split('\n')
    print lines[:2]
    assert len(lines) == 0

if __name__ == '__main__':
    from_ = sys.argv[1]
    to_ = None
    if len(sys.argv) > 2:
       to_ = sys.argv[2]
    convert(from_, to_)

