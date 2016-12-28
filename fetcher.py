#!/usr/bin/env python
# @(#) a simple python page fetcher, that caches a local copy 

import requests
from readability import Document
import sys
from bs4 import BeautifulSoup
import re

if len(sys.argv) < 2:
    print "Usage: fetcher.py <url0> <url1> ... <urlN>"
    sys.exit(0)

slugify = re.compile('[^a-zA-Z0-9]+')

for arg in sys.argv[1:]:
    response = requests.get(arg)
    doc = Document(response.text)
    title = doc.title().lower()
    slug = slugify.sub("-", title)
    print slug
    soup = BeautifulSoup(doc.get_clean_html(), "lxml")
    text = soup.getText()
    site = "original site: {0}".format(arg)
    tag = soup.new_tag("a", href=arg, contents=site)
    soup.body.insert(0, tag)
    html = soup.prettify("utf-8")
    with open('./cache/{0}.html'.format(slug), "w") as fh:
        fh.write(html)
