# @(#) the meat of the token storage system

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
import sqlite3  # Addenudum 03DEC2010: added this for Arc90 demo


class TokenStore(object):

    def __init__(self, corpus, stopwords):
        self.documents = {}
        self.token_count = 0
        self.corpus = corpus
        self.stopwords = stopwords
        self.filter_nonan = re.compile('[^a-zA-Z0-9 \']')

    def add(self, token, did):

        if did not in self.documents:
            self.documents[did] = {}

        self.token_count += 1

        if token in self.documents[did]:
            self.documents[did][token]['term_frequency'] += 1
        else:
            self.documents[did][token] = {'term_frequency': 1,
                                          'tf_idf': 0.0}

    def build_index(self):
        doc_count = float(len(self.corpus))
        for doc in self.documents:
            filter_list = self.documents[doc]
            # filter_count = float(len(self.documents[doc].keys()))
            for tok in filter_list:
                ifreq = log(doc_count /
                            float(filter_list[tok]['term_frequency']))
                tf = float(filter_list[tok]['term_frequency'])
                filter_list[tok]['tf_idf'] = tf * ifreq

    def _reducer(self, term):
        return lambda x: x['tok'] == term

    def doc_search(self, terms):
        """Dead simple document search"""
        return_list = []
        term = None
        mapper = lambda x: (x['doc_id'], x['tf_idf'])
        for term in terms:
            return_list[len(return_list):] = [map(mapper,
                                              filter(self._reducer(term),
                                                     self.token_list))]
        return return_list

    def dump_database(self, infile):
        """ Addendum 03DEC2010: added database dump."""

        # really need to parameterize these...
        docsql = "INSERT INTO docs (document) VALUES ('%s')"
        frqsql = "INSERT INTO tokens (tok,tok_count,doc_id,tf_idf) VALUES (\"%s\", %d, %d, %f)"
        sqlcon = sqlite3.connect(infile)
        cur = sqlcon.cursor()
        doc_id = 1  # fudge the index of document keys
        for doc in self.documents:
            # parameterize this...
            cur.execute(docsql % doc)
            for token in self.documents[doc]:
                cur.execute(frqsql %
                            (token,
                             self.documents[doc][token]['term_frequency'],
                             doc_id,
                             self.documents[doc][token]['tf_idf']))
            doc_id += 1

        sqlcon.commit()
        cur.close()

    def tokenize_text(self, text):
        return [t for t in
                self.filter_nonan.sub(' ', text).lower().split()
                if t not in self.stopwords]

    def tokenize_file(self, infile):
        """ Break apart a file, remove surperflous markings
            and return a token list."""
        with open(infile, 'r') as fh:
            return [t for t in
                    self.filter_nonan.sub(' ',
                                          fh.read()).lower().split()
                    if t not in self.stopwords]

    def tokenize_and_add(self, infile, text=None, new=False):
        if text is None:
            tokens = self.tokenize_file(infile)
        else:
            tokens = self.tokenize_text(text)

        if new:
            self.corpus.append(infile)

        for token in tokens:
            self.add(token, infile)

    def ingest_corpus(self):
        for doc in self.corpus:
            self.tokenize_and_add(doc)