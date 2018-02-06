===========
NLP Project
===========

Setting up Solar
================

    1. Install solr 7.1 and add solar/bin to PATH
    #. to create core named *nlp*, 
    
        .. code::
        
            solar create_core -c nlp
            
            to get help:
                solar create -help
                solar create_core -help
                solar create_collection -help
                
            instanceDir will be create in <solr_install>/server/solr/nlp
                
    #. 