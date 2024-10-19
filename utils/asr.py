from whoosh.index import create_in, open_dir
from whoosh.fields import Schema, TEXT
from whoosh.qparser import QueryParser
from whoosh.query import Phrase
import os
import numpy as np
import bm25s
import Stemmer  # optional: for stemming
import json
stemmer = Stemmer.Stemmer("english")

ASR_WHOOSH_PATH = ''
ASR_MAPPING_PATH = ''
# Define the schema: A single text field named "content"
schema = Schema(content=TEXT(stored=True))
whoosh_mapping = None
ix = None
def init():
    global ix, whoosh_mapping
    ix = open_dir(ASR_WHOOSH_PATH)
    whoosh_mapping = json.load(open(ASR_MAPPING_PATH))

def get_ocr(query_str, limit):
    query_str = query_str.lower()
    # Search the index
    results = []
    
    with ix.searcher() as searcher:
        query = Phrase("content", query_str.split(' '))
        results = searcher.search(query, limit=limit)        
        ids = [result.docnum for result in results]
        for result in results:
            print(" -ASR: ",result['content'])

        query = QueryParser("content", ix.schema).parse(query_str)
        # query = Phrase("content", query_str.split(' '))
        results2 = searcher.search(query, limit=limit)
        for result in results2:
            if result.docnum not in ids:
                ids.append(result.docnum)
                print(" -ASR: ",result['content'])
        # Print results
        # for result in results:
        #     print(" -ASR: ",result['content'])
    # return np.array([x.docnum for x in results])
    print(max(ids))
    ids = [whoosh_mapping[x] for x in ids]
    return np.array(ids)        
