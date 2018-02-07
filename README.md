# nlpsearch
Search engine utilizing Solr to index and search articles
=======================================
NLP - project run-time instructions
=======================================
List of source code files:
bin:
 - download_nltk_data.py (Might be needed to download corpus)
 - search.py - Command line search client
 - task_2.py - Create Solr Core, parse and load documents for task 2
 - task_3.py - Create Solr Core, parse and load documents for task 3
 - task_4.py - Create Solr Core, parse and load documents for task 4
lib:
 - solr.py - Solr utilities for Core creation
 - utilities.py - text processing functions

 ************************************************************************
- To start Solr:
C:\opt\Solr\solr-7.1.0\bin\solr.cmd start

- To check if SOLR is running:
http://localhost:8983/solr/

-- Information on Solr Core creation:
C:\opt\Solr\solr-7.1.0\bin\solr.cmd create_core -help


NLTK resources:
http://www.nltk.org/howto/corpus.html#overview

SpaCy Installation and configuration instructions:
====================================================
1) Install: pip install spacy
2) Load model - must be run with Admin permissions (open terminal with admin rights):
python -m spacy download en

Loading documents into Solr - total of 10,751 articles will be loaded into each Core:
=====================================================================================
- Each of the tasks 1, 2 and 3 using its own Solr "Core"
- In order to load documents, run following commands from the command line from ../nlpsearch/bin/
python task_2.py
python task_3.py
python task_4.py

- Following Cores will be created: task02, task03 and task04

Validation of the number documents in Solr:
http://localhost:8983/solr/task02/select?q=*&stats=true&rows=0&stats.field=article_id&stats.calcdistinct=true
http://localhost:8983/solr/task02/select?q=*&stats=true&rows=0&stats.field=words

-- Replace task02 with task03 and task04 to validate Tasks 3 and 4
http://localhost:8983/solr/task03/select?q=*&stats=true&rows=0&stats.field=article_id&stats.calcdistinct=true
http://localhost:8983/solr/task03/select?q=*&stats=true&rows=0&stats.field=words
http://localhost:8983/solr/task04/select?q=*&stats=true&rows=0&stats.field=article_id&stats.calcdistinct=true
http://localhost:8983/solr/task04/select?q=*&stats=true&rows=0&stats.field=words

**************************************************************************************************************
Search command options:
nlpsearch\bin>python search.py -h
usage: search.py [-h] [--type {0,1,2}] [--results_cnt Q_CNT] [--verbose]
                 search_pattern [search_pattern ...]

search Search words in article database. Example: search --type 1 table chair

positional arguments:
  search_pattern        One or more words to search.

optional arguments:
  -h, --help            show this help message and exit
  --type {0,1,2}, -t {0,1,2}
                        Search type: 0: basic, 1: advanced, and 2: expert.
  --results_cnt Q_CNT, -c Q_CNT
                        Limit number of results from SOLR query
  --verbose, -v         Sets verbose mode. Prints input and generated Solr query
  --art_title, -a       Set to skip article title print
  *************************************************************************************************************
  
Example search runs:
======================================================
- Run search with "-t" flog equals to {"0":task-2, "1":task-3, "2":task-4}. From command line:
   * python search.py -t 0  compensation losses earned
   * python search.py -t 1  compensation losses earned
   * python search.py -t 2  compensation losses earned
   
   * python search.py -t 1 political crisis in Africa will cause unrest   
   * python search.py -t 1 Iran Iraq war impact on oil prices
   * python search.py -t 1 river bank needed repair
   * python search.py -t 1 Boeing and airbus deals
   * python search.py -t 1 africa development and expansion project
