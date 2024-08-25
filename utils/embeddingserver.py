import requests
import pickle
import codecs
import json


EMBEDDING_SERVER = ""

def text_feature(text: str):
    pickled = json.loads(requests.get(EMBEDDING_SERVER+'/text_CLIP/'+text).text)
    unpickled = pickle.loads(codecs.decode(pickled.encode(), "base64"))
    return unpickled