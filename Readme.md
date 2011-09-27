### Overview ###

Daedalus is a dead simple TF-IDF system; I wrote it quite some time ago when I wanted to demo 
how the new search system would work at a former workplace. I cleaned it up (code is still
ugly, I&apos;ll work on that) and used it as a demo when I was applying to work at Arc90.

### Demo ###

The initial version of Daedalus was meant to run against the programming archive from
text-files.com; I&apos; like to make that configurable:

* index a directory:

`$ daedalus.py index dir`

* serve that index:

`$ daedalus.py serve`

### Requirements ###

* Flask
* SQLite
* Patience
