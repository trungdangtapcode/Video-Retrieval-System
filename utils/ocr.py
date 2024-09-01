from whoosh.index import create_in, open_dir
from whoosh.fields import Schema, TEXT
from whoosh.qparser import QueryParser
from whoosh.query import Phrase
import os
import numpy as np

OCR_WHOOSH_PATH = ''
# Define the schema: A single text field named "content"
schema = Schema(content=TEXT(stored=True))

ix = None
def init():
    global ix
    ix = open_dir(OCR_WHOOSH_PATH)

def get_ocr(query_str, limit):
    query_str = query_str.lower()
    # Search the index
    results = []
    with ix.searcher() as searcher:
        # query = QueryParser("content", ix.schema).parse(query_str)
        query = Phrase("content", query_str.split(' '))
        results = searcher.search(query, limit=limit)
        
        # Print results
        for result in results:
            print(" -OCR: ",result['content'])
    return np.array([x.docnum for x in results])