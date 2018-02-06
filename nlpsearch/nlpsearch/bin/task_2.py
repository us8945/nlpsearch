'''
Created on Nov 7, 2017

@author: uri
Manually delete Core in case of error 500:
C:\opt\Solr\solr-7.1.0\bin\solr.cmd delete -c "example01"
'''

''' To allow for comand line run'''
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from nlpsearch.lib.solr import Solr
import pysolr
from nltk import sent_tokenize, word_tokenize
from nltk.corpus import gutenberg
from nlpsearch.lib.utilities import tokenize
from nlpsearch.lib.utilities import doc_selection
from nlpsearch.lib.utilities import extract_title
import re

core = 'task02'
#SOLR_BIN = '/apps/solr/solr-7.1.0/bin/solr'
SOLR_BIN="C:\opt\Solr\solr-7.1.0\\bin\solr.cmd"
SOLR_URL = 'http://localhost:8983/solr'
MAX_ADD_DOCS = 100


def create_core_schema():
    s = Solr(solr=SOLR_BIN,verbose=True)
    
    print('Before re-start')
    s.restart()
    print('After re-start')
    if s.is_core(core):
        print('Core {} already exist. Deleting.'.format(core))
        s.delete_core(core)

    s.create_core(core)
    print('Core {} created.'.format(core))

    s.add_field(name="words",
                type="strings", indexed=True, stored=False, multiValued=True)
    s.add_field(name="full_sentence",
                type="string", indexed=False, stored=True, multiValued=True)
    s.add_field(name="article_title",
                type="string", indexed=False, stored=True, multiValued=True)
    s.add_field(name="article_id",
                type="string", indexed=False, stored=True, multiValued=True)

    print("Schema created.")


def load_article(id_, text):
    solr = pysolr.Solr(SOLR_URL + '/{}/'.format(core), timeout=10)
    title,text=extract_title(text)
    sentences = sent_tokenize(text)
    #print('Loading documents.')
    transaction_size = 5
    transaction = list()
    for sentence in sentences:
        words = tokenize(sentence)
        transaction += [{
                #"id": id_,
                "words": words,
                "full_sentence": sentence,
                "article_title": title,
                "article_id":id_
            }]
        if len(transaction) >= transaction_size:
            result = solr.add(transaction)
            transaction = list()

    if len(transaction) > 0:
        result = solr.add(transaction)

    #print(' loaded.')


if __name__ == '__main__':
    create_core_schema()    
    RUN_TYPE='FULL'
    if RUN_TYPE=='FULL':
        create_core_schema()
        #train_docs,number_of_articles,number_of_words = doc_selection(10,1000)
        ''' Load all Reuters articles '''
        document_count = 0
        dot_count = 0
        total_loaded=0
        train_docs,number_of_articles,number_of_words = doc_selection()
        for id_,text in train_docs:
            load_article(id_, text)
            document_count += 1
            total_loaded += 1
            if document_count % 5 == 0:
                dot_count += 1
                end = '' if dot_count % 100 else '\n'
                print('*', end=end, flush=True)
                document_count = 0
        print('Load completed. Total documents loaded:',total_loaded)
