'''
Created on Nov 6, 2017

@author: Uri Smashnov
Manually delete Core in case of erro 500:
C:\opt\Solr\solr-7.1.0\bin\solr.cmd delete -c "example01"
'''

from nlpsearch.lib.solr import Solr
import pysolr
from nltk import sent_tokenize, word_tokenize
from nltk.corpus import gutenberg
from nlpsearch.lib.utilities import tokenize
from nlpsearch.lib.utilities import doc_selection

core = 'example01'
#SOLR_BIN = '/apps/solr/solr-7.1.0/bin/solr'
SOLR_BIN="C:\opt\Solr\solr-7.1.0\\bin\solr.cmd"
SOLR_URL = 'http://localhost:8983/solr'
MAX_ADD_DOCS = 5


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

    s.add_field(name="word",
                type="strings", indexed=True, stored=False, multiValued=True)
    s.add_field(name="sentence",
                type="string", indexed=False, stored=True, multiValued=True)
    s.add_field(name="title",
                type="string", indexed=False, stored=True, multiValued=True)

    print("Schema created.")


def load_article(id_, text):
    solr = pysolr.Solr(SOLR_URL + '/{}/'.format(core), timeout=10)
    sentences = sent_tokenize(text)
    print('Loading documents.')
    transaction_size = 5
    sentence_count = 0
    dot_count = 0
    transaction = list()
    for sentence in sentences:
        words = tokenize(sentence)
        sentence_count += 1
        if sentence_count % 100 == 0:
            dot_count += 1
            end = '' if dot_count % 80 else '\n'
            print('*', end=end, flush=True)
            sentence_count = 0
        transaction += [{
                #"id": id_,
                "word": words,
                "sentence": sentence,
                "title": id_,
            }]
        if len(transaction) >= transaction_size:
            result = solr.add(transaction)
            transaction = list()

    if len(transaction) > 0:
        result = solr.add(transaction)

    print(''); print(' loaded.')


if __name__ == '__main__':
    create_core_schema()
    train_docs,number_of_articles,number_of_words = doc_selection()
    full = gutenberg.fileids()
    for id_ in full[:1]:
        text = gutenberg.raw(id_)
        load_article(id_, text)
