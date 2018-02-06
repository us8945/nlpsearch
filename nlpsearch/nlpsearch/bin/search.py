#!/usr/bin/env python
'''
Created on Nov 19, 2017

@author: Uri
'''
import os
import sys
''' To allow for comand line run'''
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

import logging
import pysolr
#from nlpsearch.lib import utilities 
#from lib import *
from nlpsearch.lib.utilities import tokenize,doc_selection,extract_title,stem_tokens,lemmatize_tokens,pos_words_tag,spacy_tokenizer_parser, extract_synonyms_meaning,extract_synonyms_meaning_advanced

logger=logging.getLevelName(__name__)


def cmdargs():
    import argparse
    import os

    filename = os.path.basename(__file__)
    progname = filename.rpartition('.')[0]

    parser = argparse.ArgumentParser(description="""
{progname} Search words in article database.

Example: 

    {progname} --type 1 table chair
""".format(progname=progname))
    parser.add_argument('--type', '-t', type=int, dest='search_type', choices=[0, 1, 2], required=False, default=0,
                        help="""Search type: 0: basic, 1: advanced, and 2: expert.""")
    parser.add_argument('--results_cnt', '-c', type=int, dest='q_cnt', required=False, default=10,
                        help="""Limit number of results from SOLR query""")
    parser.add_argument('--verbose', '-v', action="store_true", dest='verbose',required=False, default=False,
                        help="""Sets verbose mode. Prints input and generated Solr query""")
    parser.add_argument('--art_title', '-a', action="store_true", dest='article_title',required=False, default=False,
                        help="""Set to skip article title print""")
    parser.add_argument('search_pattern', type=str, nargs='+',
                        help="""One or more words to search.""")
    args = parser.parse_args()
    argsd=vars(args)
    return argsd

def parse_pattern_to_solr(pattern,search_type=0):
    '''
    Parse search tokens to the SOLR format
    q=type:furniture AND location:office
    '''
    search_pattern=''
    result='words:('
    
    if search_type==0:
        for word_ind,word in enumerate(pattern):
            if word_ind!=0:
                result=result+' OR '
            result=result+word
        result=result+')'
        
    elif search_type==1:
        stems=stem_tokens(pattern)
        lemmas=lemmatize_tokens(pattern)
        pos_tags = pos_words_tag(pattern)
        head_words, phrases=spacy_tokenizer_parser(' '.join(pattern))
        hypernyms,hyponyms,part_meronyms,part_holonyms= extract_synonyms_meaning(lemmas)
        field_types=[(stems,'stems'),(lemmas,'lemmas'),(pos_tags,'words_pos_tags'),(head_words,'head_words'),(hypernyms,'hypernyms'),(hyponyms,'hyponyms'),
                     (part_meronyms,'part_meronyms'),(part_holonyms,'part_holonyms')]
        for word_ind,word in enumerate(pattern):
            if word_ind!=0:
                result=result+' OR '
            result=result+word
        result=result+')'
        
        for field_type,field_name in field_types:
            if len(field_type)>0:
                result=result+' OR '+field_name+':('
                for word_ind,word in enumerate(field_type):
                    if word_ind!=0:
                        result=result+' OR '
                    result=result+word
                result=result+')'
    
    elif search_type==2:
        stems=stem_tokens(pattern)
        lemmas=lemmatize_tokens(pattern)
        pos_tags = pos_words_tag(pattern)
        head_words, phrases=spacy_tokenizer_parser(' '.join(pattern))
        hypernyms,hyponyms,part_meronyms,part_holonyms= extract_synonyms_meaning(lemmas)
        synsets,hypernyms,hyponyms,part_meronyms,part_holonyms = extract_synonyms_meaning_advanced(pattern,' '.join(pattern))
        field_types=[(stems,'stems'),(lemmas,'lemmas'),(pos_tags,'words_pos_tags'),(head_words,'head_words'),(hypernyms,'hypernyms'),(hyponyms,'hyponyms'),(synsets,'synsets'),
                     (part_meronyms,'part_meronyms'),(part_holonyms,'part_holonyms')]
        for word_ind,word in enumerate(pattern):
            if word_ind!=0:
                result=result+' OR '
            result=result+word
        result=result+')'
        
        for field_type,field_name in field_types:
            if len(field_type)>0:
                result=result+' OR '+field_name+':('
                for word_ind,word in enumerate(field_type):
                    if word_ind!=0:
                        result=result+' OR '
                    result=result+word
                result=result+')'
    return result
        
    

def search_for_pattern(pattern,solar_instance,search_type=0,q_limit=10,verbose=False,article_title_skip=False):
    print('\n')
    print('*****************************************************************************')
    if verbose:
        print('Input parameters',pattern,solar_instance)
    solr = pysolr.Solr('http://localhost:8983/solr/'+solar_instance+'/', timeout=10)
    search_pattern=parse_pattern_to_solr(pattern,search_type)
    if verbose:
        print('Look for pattern:',search_pattern)
    #results = solr.search(q='words:(acquire OR company OR conditions OR managerial OR role)', rows=10)
    results = solr.search(q=search_pattern, rows=q_limit)
    #total_results = solr.search(q=search_pattern, rows=1000000000)
    for result in results:
        if not article_title_skip:
            print('Article title:',result['article_title'][0])
        print(result['full_sentence'][0])
        print('')
    
    #print("Showing top: ",len(results), 'result(s) out of total:',len(total_results))
    print("Showing top: ",len(results))
    return results

if __name__=='__main__':
    args = cmdargs()
    #print(args)
    search_type=args['search_type']
    if search_type==0:
        solar_instance='task02'
    elif search_type==1:
        solar_instance='task03'
    elif search_type==2:
        solar_instance='task04'
    results=search_for_pattern(args['search_pattern'],solar_instance,search_type,args['q_cnt'],args['verbose'],args['article_title'])
    # search(**args)
