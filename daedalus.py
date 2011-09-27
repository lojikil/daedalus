from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template
from logging import Formatter 

app = Flask(__name__)

@app.errorhandler(500)
def handle500(e):
    return "<html><body><p>%s</p></body></html>" % str(e), 500

@app.before_request
def before_req():
    g.db = sqlite3.connect('./index_test.db')

@app.after_request
def after_req(response):
    g.db.close()
    return response

@app.route("/")
def daedalus_index():
    return render_template("show_index.html")

@app.route("/search", methods = ["GET","POST"])
def daedalus_search():
    entries = []
    if request.method == "POST":
        if request.form['query']:
            cur = g.db.execute("select docs.document, tokens.tf_idf"
                               "from tokens left outer join docs"
                               "on tokens.doc_id = docs.doc_id"
                               "where (tokens.tok = ?) order by tokens.tf_idf desc",[request.form['query']])
            entries = [dict(document = row[0],score = row[1]) for row in cur.fetchall()]
    return render_template("list.html",entries=entries)

if __name__ == "__main__":
    app.run()
