from whoosh.index import create_in, open_dir
from whoosh.fields import Schema, TEXT
from whoosh.qparser import QueryParser
from whoosh.query import Phrase
import os
import numpy as np
import bm25s
import Stemmer  # optional: for stemming
stemmer = Stemmer.Stemmer("english")

OCR_WHOOSH_PATH = ''
# Define the schema: A single text field named "content"
schema = Schema(content=TEXT(stored=True))
whoosh_mapping = list(range(106589)) + list(range(298000,298000+94657)) +\
    list(range(765106,765106+151318))
bm25_mapping = list(range(106589)) + list(range(298000,298000+94657)) +\
    list(range(765106,765106+151318))
ix = None
def init():
    global ix
    ix = open_dir(OCR_WHOOSH_PATH)

    # global retriever, ids
    # retriever = bm25s.BM25.load(DIRECTORY_INDEX, load_corpus=True)
    # ids = list(range(len(retriever.corpus)))

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


DIRECTORY_INDEX = ''
retriever = None
ids = None
def get_ocr_bm25(query_str):
    pass