import requests
import pickle
import codecs
import json


EMBEDDING_SERVER = ""
EMBEDDING_SERVER_INTERNVIDEO = ""

def text_feature(text: str, model_name: str):
    pickled = json.loads(requests.get(EMBEDDING_SERVER+f'/text_{model_name}/'+text).text)
    unpickled = pickle.loads(codecs.decode(pickled.encode(), "base64"))
    return unpickled

def image_feature_file(file, model_name: str):
    formdata = {'image': file}
    url = EMBEDDING_SERVER+f'/image_{model_name}'
    r = requests.post(url, files=formdata)
    pickled = json.loads(r.text)
    unpickled = pickle.loads(codecs.decode(pickled.encode(), "base64"))
    return unpickled

def image_feature_url(url_img, model_name: str):
    url = EMBEDDING_SERVER+f'/image_url_{model_name}'
    r = requests.get(url,params={'url':url_img})
    pickled = json.loads(r.text)
    unpickled = pickle.loads(codecs.decode(pickled.encode(), "base64"))
    return unpickled