import requests
import pickle
import codecs
import json

URL_SERVER = ""

def text_seach(text: str, k: int):
    headers = {
        "ngrok-skip-browser-warning": "69420",
    }
    params = {
        "text": text,
        "k": k
    }
    response = requests.get(URL_SERVER+'/text/', headers=headers, params=params)
    encoded = response.text
    pickled = json.loads(encoded)   
    unpickled = pickle.loads(codecs.decode(pickled.encode(), "base64"))    
    idx, scores = unpickled
    return idx, scores

def index_search(idx: int, k: int):
    headers = {
        "ngrok-skip-browser-warning": "69420",
    }
    params = {
        "idx": idx,
        "k": k
    }
    response = requests.get(URL_SERVER+'/idx/', headers=headers, params=params)
    encoded = response.text
    pickled = json.loads(encoded)   
    unpickled = pickle.loads(codecs.decode(pickled.encode(), "base64"))    
    idx, scores = unpickled
    return idx, scores