#!/usr/bin/env python
# @(#) 2008 Ok sedwards@; Daedalus Search example
from TokenStore import TokenStore
from os import walk
from os.path import join


if __name__ == "__main__":

    corpus = []
    stopwords = open('stopwords.dat').read().split()

    for root, dirs, files in walk('programming'):
        corpus[len(corpus):] = [join(root, file) for file in files]

    ts = TokenStore(corpus, stopwords)
    ts.ingest_corpus()

    print "Building index..."
    ts.build_index()
    ts.dump_database("./index_test.db")
    print "Completed..."
    print "Number of documents in corpus:", len(corpus)
    print "Number of tokens in TokStor:", ts.token_count
    # print "Search for [\"limited\",\"field\"]",
    # print ts.doc_search(["limited","field"])
