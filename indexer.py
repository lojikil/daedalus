#!/usr/bin/env python
# @(#) 2008 Ok sedwards@; Daedalus Search example

""" My dead simple 'Search Engine', which I nick named Daedalus,
    out of sheer humility, comparing myself to Daedalus, and the
    corpus to the Minotaur :D

    Don't use for anything real, it's merely an example of what
    we can do with proper search.

    Computes tf x idf of a corpus (in this case, the programming
    archive of textfiles.com) and stores it in a TokenStore instance.
    This could be dumped to a SQL server (addendum 03DEC2010: added
    sqlite in order to use this as a code sample for Arc90) & used
    for search, if you were crazy. Indexing takes quite a while, and
    it's probably overly reliant on Python functional-style, but
    that's just how I think^wroll.

    ROOM FOR IMPROVEMENT:
        - porter stemming would be the most obvious choice
        - soundex or levenstein or the like in doc_search (catch
          some mispellings)
        - dump to disk (addendum 03DEC2010: added this via SQLite,
          for a code sample at Arc90)

    NOTE BENE:
        This was written *AT HOME*, is not a *CERTIFIED PROJECT*,
        and if you, for some crazy reason, want to use it
        in a project, please check with <REDACTED> before hand. Also,
        this code is pretty dirty.
"""

import re
from math import log
from os import walk
from os.path import join

import sqlite3 # Addenudum 03DEC2010: added this for Arc90 demo

corpus = []
stopwords = open('stopwords.dat').read().split()

class TokenStore(object):
    def __init__(self):
        self.documents = {}
        self.token_count = 0

    def add(self,token,did):

        if did not in self.documents:
            self.documents[did] = {}
        self.token_count += 1
        if token in self.documents[did]:
            self.documents[did][token]['term_frequency'] += 1
        else:
            self.documents[did][token] = {'term_frequency': 1,
                                        'tf_idf': 0.0}

    def build_index(self):
        global corpus
        doc_count = float(len(corpus))
        for doc in self.documents:
            filtre_list = self.documents[doc]
            filtre_count = float(len(self.documents[doc].keys()))
            for tok in filtre_list:
                ifreq = log(doc_count /
                            float(filtre_list[tok]['term_frequency']))
                filtre_list[tok]['tf_idf'] = float(filtre_list[tok]['term_frequency']) * ifreq

    def _reducer(self, term)
        return lambda x: x['tok'] == term

    def doc_search(self,terms):
        """Dead simple document search"""
        return_list = []
        term = None
        mapper = lambda x: (x['doc_id'], x['tf_idf'])
        reducer = lambda x: x['tok'] == term
        for term in terms:
            return_list[len(return_list):] = [map(mapper,
                                              filter(self._reducer(term),
                                                     self.token_list))]
        return return_list

    def dump_database(self,file):
        """ Addendum 03DEC2010: added database dump. Given the time,
            I would also clean up the globals I used :X"""
        sqlcon = sqlite3.connect(file)
        cur = sqlcon.cursor()
        doc_id = 1 # fudge the index of document keys
        for doc in self.documents:
            # parameterize this...
            cur.execute("INSERT INTO docs (document) VALUES ('%s')" % doc)
            for token in self.documents[doc]:
                cur.execute("INSERT INTO tokens (tok,tok_count,doc_id,tf_idf) VALUES (\"%s\",%d,%d,%f)" %
                               (token,
                                self.documents[doc][token]['term_frequency'],
                                doc_id,
                                self.documents[doc][token]['tf_idf']))
            doc_id += 1

        sqlcon.commit()
        cur.close()

# Move the below into a class, so that multiple corpora can
# be instantiated, each with a token Store (might want to just jam
# it all into TokenStore, with a pretty method set). 

filter_nonan = re.compile('[^a-zA-Z0-9 \']')

def tokenize_file(n):
    """ Break apart a file, remove surperflous markings and return a token list."""
    global stopwords
    with open(n, 'r') as fh:
        return [t for t in
                filter_nonan.sub(' ',
                             fh.read()).lower().split()
                if t not in stopwords]

if __name__ == "__main__":

    for root,dirs,files in walk('programming'):
        corpus[len(corpus):] = [join(root,file) for file in files]

    ts = TokenStore()
    for f in corpus:
        print "Processing",f,"..."
        tokens = tokenize_file(f)
        for tok in tokens:
            ts.add(tok,f)

    print "Building index..."
    ts.build_index()
    ts.dump_database("./index_test.db")
    print "Completed..."
    print "Number of documents in corpus:",len(corpus)
    print "Number of tokens in TokStor:",ts.token_count
    #print "Search for [\"limited\",\"field\"]",
    #print ts.doc_search(["limited","field"])
