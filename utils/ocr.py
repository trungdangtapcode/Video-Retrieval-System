from whoosh.index import create_in, open_dir
from whoosh.fields import Schema, TEXT
from whoosh.qparser import QueryParser
from whoosh.query import Phrase
import os
import numpy as np

OCR_WHOOSH_PATH = ''
# Define the schema: A single text field named "content"
schema = Schema(content=TEXT(stored=True))
whoosh_mapping = list(range(106589)) + list(range(298000,298000+94657))

ix = None
def init():
    global ix
    ix = open_dir(OCR_WHOOSH_PATH)

def get_ocr(query_str, limit):
    query_str = query_str.lower()
    # Search the index
    results = []
    
    with ix.searcher() as searcher:
        query = Phrase("content", query_str.split(' '))
        results = searcher.search(query, limit=limit)        
        ids = [result.docnum for result in results]
        for result in results:
            print(" -OCR: ",result['content'])

        query = QueryParser("content", ix.schema).parse(query_str)
        # query = Phrase("content", query_str.split(' '))
        results2 = searcher.search(query, limit=limit)
        for result in results2:
            if result.docnum not in ids:
                ids.append(result.docnum)
                print(" -OCR: ",result['content'])
        # Print results
        # for result in results:
        #     print(" -OCR: ",result['content'])
    # return np.array([x.docnum for x in results])
    ids = [whoosh_mapping[x] for x in ids]
    return np.array(ids)