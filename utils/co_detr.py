import bm25s
import Stemmer  # optional: for stemming
import numpy as np
stemmer = Stemmer.Stemmer("english")

bm25_mapping = list(range(106589)) + list(range(298000,298000+94657))

DIRECTORY_INDEX = ''
retriever = None
ids = None
def init():
    global retriever, ids
    retriever = bm25s.BM25.load(DIRECTORY_INDEX, load_corpus=True)
    ids = list(range(len(retriever.corpus)))

def get_top_k(query: str, k: int):
    # print(query)
    query_tokens = bm25s.tokenize(query, stemmer=stemmer)
    results, scores = retriever.retrieve(query_tokens, corpus = ids, k=k)
    value, _ = retriever.retrieve(query_tokens, corpus = retriever.corpus, k=k)
    # print(value)
    return np.array([bm25_mapping[x] for x in results[0]]), np.array(scores[0])