#!/usr/bin/env python
# @(#) create_db.py creates the sqlite3 database for Daedalus to use.
# @(#) 2010 ok sedwards@lojikil 

import sqlite3
import sys
try:
    sqlcon = sqlite3.connect("./index_test.db")
    cur = sqlcon.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS docs (doc_id INTEGER PRIMARY KEY ASC, document TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS tokens (tok_id INTEGER, tok TEXT, tok_count INTEGER, doc_id INTEGER, tf_idf REAL)")
    sqlcon.commit()
    cur.close()
except:
    print sys.exc_info()
    pass

