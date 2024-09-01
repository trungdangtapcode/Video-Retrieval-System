from utils import bm25
import json
OCR_PATH = ''

index = None
def init():
    global index
    ocr_file = open(OCR_PATH)
    corpus  = json.load(ocr_file)
    index = bm25.get_bm25_index(corpus)

def get_scores(query: str):
    token = query.lower().split(" ")
    return index.get_scores(token)

def get_sorted_idx(query: str, n: int):
    scores = get_scores(query)
    idx = scores.argsort()[::-1]
    return idx[:n]