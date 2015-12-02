'''
Example usage:

    python scripts/process.py scraped/1205000e.txt 
'''
import os

baseurl = 'http://www.iisd.ca/vol12/'

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

    fout.write('''---
title: %s
id: %s
url: %s
date:
---

''' % (title, fileid, baseurl + fileid)
)
    fout.write(text)
    fout.close()

def convertall():
    # TODO: walk through the scraped directory and process all ofthem
    # Before doing this i'd make sure we really have this working well
    pass

def txt2markdown(fileobj):
    txt = fileobj.read()
    lines = txt.split('\n')
    title = lines[0].replace('::TITLE::', '')
    lines = [ x.strip() for x in lines ]
    # drop title row
    lines = lines[1:]

    # TODO: see if there is an abstract

    def fix(line):
        line = line.replace('::H1::', '# ')
        line = line.replace('::H3::', '### ')
        line = line.replace('::BODY::', '')
        return line

    lines = [ fix(line) for line in lines ]

    txt = '\n\n'.join(lines)
    return (title, txt)

def test_it():
    path = 'samples/1205000e.txt'
    title, text = txt2markdown(open(path))
    lines = text.split('\n')
    print lines[:2]
    assert len(lines) == 0

import sys
if __name__ == '__main__':
    from_ = sys.argv[1]
    to_ = None
    if len(sys.argv) > 2:
       to_ = sys.argv[2]
    convert(from_, to_)

