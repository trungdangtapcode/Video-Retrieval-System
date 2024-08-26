import requests
import pickle
import codecs
import json


EMBEDDING_SERVER = ""

def text_feature(text: str):
    pickled = json.loads(requests.get(EMBEDDING_SERVER+'/text_ALIGN/'+text).text)
    unpickled = pickle.loads(codecs.decode(pickled.encode(), "base64"))
    return unpickled

def image_feature_file(file):
    formdata = {'image': file}
    url = EMBEDDING_SERVER+'/image_ALIGN'
    r = requests.post(url, files=formdata)
    pickled = json.loads(r.text)
    unpickled = pickle.loads(codecs.decode(pickled.encode(), "base64"))
    return unpickled

def image_feature_url(url_img):
    url = EMBEDDING_SERVER+'/image_url_ALIGN'
    r = requests.get(url,params={'url':url_img})
    pickled = json.loads(r.text)
    unpickled = pickle.loads(codecs.decode(pickled.encode(), "base64"))
    return unpickled