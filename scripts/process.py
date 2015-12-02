import unittest

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
   to_ = sys.argv[2]
   title, text = txt2markdown(open(from_))
   fout = open(to_, 'w')
   fout.write('---\ntitle: %s\n---\n\n' % title)
   fout.write(text)
   fout.close()

