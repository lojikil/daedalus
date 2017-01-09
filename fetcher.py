#!/usr/bin/env python
# @(#) a simple python page fetcher, that caches a local copy 

import requests
import re
import sys
import time
from readability import Document
from bs4 import BeautifulSoup
from TokenStore import TokenStore

def process(arg, slugify, stopwords, ts, headers):
    try:
        print "requesting {0}".format(arg)
        response = requests.get(arg, headers)
        doc = Document(response.text)
        title = doc.title().lower()
        slug = slugify.sub("-", title)
        soup = BeautifulSoup(doc.get_clean_html(), "lxml")
        text = soup.getText()
        rtime = time.ctime().replace(' ', '-')
        site = "original site: {0}".format(arg)
        tag = soup.new_tag("a", href=arg)
        tag.append(site)
        soup.body.insert(0, tag)
        html = soup.prettify("utf-8")
        if len(slug) > 100:
            slug = slug[0:100]
        filename = './cache/{0}-{1}.html'.format(rtime, slug)
        ts.tokenize_and_add(filename[2:], text=text, new=True)
        with open(filename, "w") as fh:
            fh.write(html)
    except Exception as e:
        print e
        print sys.exc_info()
        print "skipping..."
        pass

if len(sys.argv) < 2:
    print "Usage: fetcher.py [-F] <pat0> <pat1> ... <patN>"
    print "pat :== (<url> | <filepat>)"
    print "filepat :== -f (filename | '-')"
    print "-F: force a database refresh (ignore previous contents)"
    sys.exit(0)

slugify = re.compile('[^a-zA-Z0-9]+')
stopwords = open('stopwords.dat').read().split()

ts = TokenStore([], stopwords)

args = sys.argv[1:]
fresh = False

if args[0] != '-F':
    ts.load_database('./index_test.db')
else:
    # here, we strip off the '-F' and
    # do not load the database
    fresh = True
    args = args[1:]

headers = requests.utils.default_headers()
headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36'
})

# hackety hack: this is the flag
# we use to signal that the argument
# following this one should be interpreted
# as a file to be read for links
flag = False

for arg in args:
    if arg == '-f':
        flag = True
    elif flag:
        if arg == '-':
            for line in sys.stdin:
                process(line.strip(), slugify, stopwords, ts, headers)
        else:
            # these two cases _probably_ could be combined...
            with file(arg) as fh:
                for line in fh:
                    process(line.strip(),
                            slugify,
                            stopwords,
                            ts,
                            headers)
        flag = False
    else:
        process(arg, slugify, stopwords, ts, headers)

ts.build_index()
ts.dump_database("./index_test.db", reindex=True)
