#!/usr/bin/env python
# @(#) 2008 Ok sedwards@; Daedalus Search example

""" My dead simple 'Search Engine', which I nick named Daedalus, out of sheer humility, comparing myself to Daedalus,
	and the corpus to the Minotaur :D
	
	Don't use for anything real, it's merely an example of what we can do with proper search.
	
	Computes tf x idf of a corpus (in this case, the programming archive of textfiles.com) and
	stores it in a TokenStore instance. This could be dumped to a SQL server (addendum 03DEC2010: added sqlite
	in order to use this as a code sample for Arc90) & used for search, if you were crazy. Indexing takes quite
	a while, and it's probably overly reliant on Python functional-style, but that's just how I think^wroll.
	ROOM FOR IMPROVEMENT:
		- porter stemming would be the most obvious choice
		- soundex or levenstein or the like in doc_search (catch some mispellings)
		- dump to disk (addendum 03DEC2010: added this via SQLite, for a code sample at Arc90)
		
	NOTE BENE: 
		This was written *AT HOME*, is not a *CERTIFIED PROJECT*, and if you, for some crazy reason, want to use it
		in a project, please check with <REDACTED> before hand. Also, this code is pretty dirty.
	"""
import re
from math import log
from os import walk
from os.path import join

import sqlite3 # Addenudum 03DEC2010: added this for Arc90 demo

global_tok_id = 0
corpus = []
stopwords = open('stopwords.dat').read().split()
class TokenStore:
	def __init__(self):
		self.token_list = []
		self.token_count = 0
	def token_exists_p(self,token,did):
		""" semi-pred: returns document index on true 
        (that token is in token list), returns false otherwise """
		for t in range(0,len(self.token_list)):
			if self.token_list[t]['tok'] == token and self.token_list[t]['doc_id'] == did:
				return t
		return False
	def add(self,token,did):
		global global_tok_id
		idx = self.token_exists_p(token,did)
		if idx:
			self.token_list[idx]['tok_len'] = self.token_list[idx]['tok_len'] + 1
		else:
			self.token_list[len(self.token_list):] = [{
                                                       'tok': token,
                                                       'tok_len': 1,
                                                       'tok_id': global_tok_id,
                                                       'doc_id': did,
                                                       'tf_idf': 0.0}]
			global_tok_id = global_tok_id + 1
	def build_index(self):
		global corpus
		doc_count = float(len(corpus))
		for did in range(0,len(corpus)):
			filtre_list = filter(lambda x: x['doc_id'] == did, self.token_list)
			filtre_count = float(len(filtre_list))
			for tok in filtre_list:
				tf = float(tok['tok_len']) / filtre_count
				ifreq = log(doc_count / float(tok['tok_len']))
				tf_idf = tf * ifreq
				tok['tf_idf'] = tf_idf
		return True
	def doc_search(self,terms):
		"""Dead simple document search"""
		return_list = []
		for term in terms:
			return_list[len(return_list):] = [map(lambda x: (x['doc_id'],x['tf_idf']),
                                                 filter(lambda x: x['tok'] == term,self.token_list))]
		return return_list
	def dump_database(self,file):
		""" Addendum 03DEC2010: added database dump. Given the time, I would also clean up the globals I used :X"""
		global corpus
		sqlcon = sqlite3.connect(file)
		cur = sqlcon.cursor()
		for doc in corpus: # not the most efficient method, but going with the overall theme
			cur.execute("INSERT INTO docs (document) VALUES ('%s')" % doc)
		for token in self.token_list:
			cur.execute("INSERT INTO tokens VALUES (%d,\"%s\",%d,%d,%f)" % (token['tok_id'],
                                                                            token['tok'],
                                                                            token['tok_len'],
                                                                            token['doc_id'],
                                                                            token['tf_idf']))
		sqlcon.commit()
		cur.close()
def tokenize_file(n):
	""" Break apart a file, remove surperflous markings and return a token list. Should filter stopwords, but not currently"""
	global stopwords
    # should probably compile this
	return [t for t in re.sub('[^a-zA-Z0-9 \']',' ',open(n).read()).lower().split()]

for root,dirs,files in walk('programming'):
	corpus[len(corpus):] = [join(root,file) for file in files]
del(corpus[50:]) # only index the first 50 files for now, so I don't die of old age before this is done
ts = TokenStore()
for x in range(0,len(corpus)):
	f = corpus[x]
	print "Processing",f,"..."
	tokens = tokenize_file(f)
	for tok in tokens:
		ts.add(tok,x)
print "Building index..."
ts.build_index()
ts.dump_database("./index_test.db")
print "Completed..."
print "Number of documents in corpus:",len(corpus)
print "Number of tokens in TokStor:",len(ts.token_list)
#print "Search for [\"limited\",\"field\"]",ts.doc_search(["limited","field"])
