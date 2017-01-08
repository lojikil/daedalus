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
        self.tokens = {}
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
        idf = {}
        for doc in self.documents:
            for tok in self.documents[doc]:
                if tok in idf:
                    idf[tok] += 1
                else:
                    idf[tok] = 1.0

        for doc in self.documents:
            for tok in self.documents[doc]:
                ifreq = log(doc_count / idf[tok])
                tf = self.documents[doc][tok]['term_frequency']
                self.documents[doc][tok]['tf_idf'] = tf * ifreq

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

    def dump_database(self, infile, reindex=False):
        """ Addendum 03DEC2010: added database dump."""

        # really need to parameterize these...
        docsql = "INSERT INTO docs (document) VALUES ('%s')"
        frqsql = "INSERT INTO tokens (tok,tok_count,doc_id,tf_idf) VALUES (\"%s\", %d, %d, %f)"
        sqlcon = sqlite3.connect(infile)
        cur = sqlcon.cursor()

        # This will actually become an issue on
        # reindex. Either need to pull the document
        # ID from the doc itself, or just look up
        # each time. May just be easiest to say
        # "if this is a reindex, select the max docid
        # from `docs`, and set docid = to that + 1"
        # fixed below
        doc_id = 1

        if reindex:
            # this actually fixes the above:
            # we first fetch the mac doc_id
            # from the`docs` table, and then
            # we use _that_ as the base to
            # iterate over
            tmp = cur.execute("SELECT max(doc_id) FROM docs;")
            result = tmp.fetchall()
            doc_id = result[0][0]

            if doc_id is not None:
                doc_id = doc_id - 1
            else:
                doc_id = 1

            cur.execute("DELETE FROM docs;")
            cur.execute("DELETE FROM tokens;")

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

    def load_database(self, dbfile):
        docsql = "SELECT document FROM docs ORDER BY doc_id"
        frqsql = "SELECT tok, tok_count, doc_id FROM tokens"
        docs = []

        sqlcon = sqlite3.connect(dbfile)
        cur = sqlcon.execute(docsql)

        for row in cur.fetchall():
            self.documents[row[0]] = {}
            # we keep this so that we can just look up
            # which document here...
            docs.append(row[0])

        cur = sqlcon.execute(frqsql)

        for row in cur.fetchall():
            tok = row[0]
            cnt = row[1]
            print row[2]
            docid = row[2] - 1
            print docid
            dockey = docs[docid]
            self.documents[dockey][tok] = dict(term_frequency=cnt, tf_idf=0.0)

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
