'''
Created on Nov 5, 2017

@author: Uri Smashnov
'''
from nltk import word_tokenize
import re
from nltk.corpus import stopwords
from nltk.corpus import reuters 
from email._header_value_parser import Phrase
cachedStopWords = stopwords.words("english")
from nltk.stem.snowball import SnowballStemmer
from nltk.stem import WordNetLemmatizer
from nltk import pos_tag
import spacy
from nltk.corpus import wordnet as wn
nlp = spacy.load('en')


def SimplifiedLesk(word,sentence):
    synsets = wn.synsets(word)
    max_overlap = 0 
    if synsets == []:
        #print ('Sence not found:',word)
        return None
    best_sence = synsets[0]
    default_sence=synsets[0].definition()
    context = calc_context(word,sentence)
    word_overlap_tot=[]
    #print('Context:',context)
    for sence in synsets:
        signature=sence.definition()
        for example in sence.examples():
            signature=signature+' '+example
        #print('Sence',sence,' Signature:',signature)
        overlap,word_overlap = ComputeOverlap(signature,context)
        word_overlap_tot.append((sence,word_overlap))
        if overlap > max_overlap:
            max_overlap = overlap
            best_sence = sence
    return best_sence

def calc_context(word,sentence):
    words = tokenize_remove_stop(sentence)
    context=[]
    for w in words:
        if w!=word:
            context.append((word,w))
    return context

def ComputeOverlap(signature,context):
    overlap=0
    word_overlap=[]
    for cont in context:
        overlap=overlap+signature.count(cont[1])
        if cont[1] in signature:
            word_overlap.append(cont[1])
    
    #print('Signature:',signature)
    #print('Context:',context)
    #print('Overlap:',overlap)
    #print('Word overlap:', word_overlap)
    return overlap,word_overlap

def tokenize_remove_stop(text):
    '''
    Adopted from
    https://miguelmalvarez.com/2015/03/20/classifying-reuters-21578-collection-with-python-representing-the-data/
    '''
    words = map(lambda word: word.lower(), word_tokenize(text));
    words = [word for word in words
                  if word not in cachedStopWords]
    return words


def doc_selection(num_articles=100000,num_words=110000):
    '''
    Include both training and testing categories.
    Filter out articles with less than 50 words.
    '''
    train_docs = []
    test_docs = []
    number_of_articles=0
    number_of_words=0
 
    for doc_id in reuters.fileids():
        if doc_id.startswith("train") or doc_id.startswith("test"):
            if len(reuters.raw(doc_id))>50:
                train_docs.append((doc_id,reuters.raw(doc_id)))
                number_of_articles+=1
                number_of_words+=len(reuters.raw(doc_id))
            
            if number_of_articles>num_articles and number_of_words>num_words:
                return train_docs,number_of_articles,number_of_words
    
    return train_docs,number_of_articles,number_of_words

def extract_title(text):
    '''
    Title of the article is from the start of raw text till the first EOL
    '''
    p = re.compile('\n');
    first_new_line=p.search(text)
    if first_new_line is None:
        print('Did not find match for title')
        print(text[:100])
        #return 'No title',text
    first_new_line=first_new_line.span()[0]
    title=text[:first_new_line]
    text=text[first_new_line+1:]
    text = text.replace('\n','')
    return title,text

def tokenize(text):
    '''
    Author
    https://miguelmalvarez.com/2015/03/20/classifying-reuters-21578-collection-with-python-representing-the-data/
    '''
    min_length = 3
    words = map(lambda word: word.lower(), word_tokenize(text));
    words = [word for word in words
                  if word not in cachedStopWords]
    p = re.compile('[a-zA-Z]+');
    filtered_tokens = list(filter(lambda token:p.match(token) and len(token)>=min_length,words));
    return filtered_tokens
    
def spacy_tokenizer_parser(text):
    '''
    Utilize spaCy library to extract:
       - sentence head words 
       - phrases
    '''
    doc=nlp(text)
    lemmas=[] #Not returned
    phrases=[]
    head_words=[]
    for token in doc:
        if len(token.lemma_.strip()) !=0:
            lemmas.append(token.lemma_)
        if token.dep_=='ROOT':
            head_words.append(token.lemma_)
    
    for chunk in doc.noun_chunks:
        if chunk.text != chunk.root.text:
            phrases.append(chunk.text)
    
    return head_words,phrases
    
def stem_tokens(words):
    '''
    Input: array of words/tokens
    Output: array of stems
    '''
    stemmer = SnowballStemmer("english")
    tokens =(list(map(lambda token: stemmer.stem(token), words)));
    return tokens

def lemmatize_tokens(words):
    '''
    Input: array of words/tokens
    Output: array of stems
    '''
    wordnet_lemmatizer = WordNetLemmatizer()
    tokens =(list(map(lambda token: wordnet_lemmatizer.lemmatize(token), words)));
    return tokens

def pos_words_tag(words):
    '''
    Input: array of words/tokens
    Output: array of "token_tag"
    '''
    tagged = pos_tag(words)
    tokens=[]
    for tag in tagged:
        tokens.append(tag[0]+'_'+tag[1])
    return tokens

def extract_synonyms_meaning_advanced(words,sentence):
    '''
    Extract and return follwong information:
     - hypernymns
     - hyponyms
     - meronyms
     - holonyms
    '''
    hypernyms=[]
    hyponyms=[]
    synsets=[]
    part_meronyms=[]
    part_holonyms=[]
    for word in words:
        best_sence=SimplifiedLesk(word, sentence)
        if best_sence is None:
            pass
        else:
            synsets.append(best_sence.name())
            try:
                for hypernym in best_sence.hypernyms():
                    hypernyms.append(hypernym.name())
            except:
                pass
            
            try:
                for hyponym in best_sence.hyponyms():
                    hyponyms.append(hyponym.name())
            except:
                pass
            
            try:
                for meronym in best_sence.part_meronyms():
                    part_meronyms.append(meronym.name())
            except:
                pass
            
            try:
                for holonym in best_sence.part_holonyms():
                    part_holonyms.append(holonym.name())
            except:
                pass
            
    return synsets,hypernyms,hyponyms,part_meronyms,part_holonyms

def extract_synonyms_meaning(words):
    '''
    Extract and return follwong information:
     - hypernymns
     - hyponyms
     - meronyms
     - holonyms
    '''
    hypernyms=[]
    hyponyms=[]
    part_meronyms=[]
    part_holonyms=[]
    for word in words:
        syn_set=wn.synsets(word)
        if syn_set==[]:
            pass
        else:
            default_synset=syn_set[0]    
            try:
                for hypernym in default_synset.hypernyms():
                    hypernyms.append(hypernym.name())
            except:
                pass
            
            try:
                for hyponym in default_synset.hyponyms():
                    hyponyms.append(hyponym.name())
            except:
                pass
            
            try:
                for meronym in default_synset.part_meronyms():
                    part_meronyms.append(meronym.name())
            except:
                pass
            
            try:
                for holonym in default_synset.part_holonyms():
                    part_holonyms.append(holonym.name())
            except:
                pass
        
    return hypernyms,hyponyms,part_meronyms,part_holonyms
        

if __name__ == '__main__':
    train_docs,number_of_articles,number_of_words = doc_selection(10,10)
    print('Number of articles:', number_of_articles)
    print('Number of words:',number_of_words)
    print(train_docs[0][1])
    #print(reuters.words(train_docs[0][0]))
    from nltk import sent_tokenize, word_tokenize
    title,text=extract_title(train_docs[0][1])
    sentences = sent_tokenize(text)
    words=tokenize(sentences[1])
    print('words:',words)
    stems=stem_tokens(words)
    print('stems:',stems)
    lemmas=lemmatize_tokens(words)
    print('Lemmas:',lemmas) 
    pos_tags = pos_words_tag(words)
    print('POS tags:',pos_tags)
    
    head_words, phrases=spacy_tokenizer_parser(sentences[1])
    print('Heads:',head_words)
    print('Pharases:', phrases)
    hypernyms,hyponyms,part_meronyms,part_holonyms= extract_synonyms_meaning(lemmas)
    print('Hypernyms:',hypernyms)
    print('hyponyms:',hyponyms)
    print('part_meronyms',part_meronyms)
    print('part_holonyms',part_holonyms)
