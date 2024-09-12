import os
from fastapi import FastAPI, File, Form, Header, Request, UploadFile, status, Response
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import utils.myfaiss
import utils.embeddingserver
import utils.ocr
import utils.co_detr
import utils.translate
import json
import numpy as np
import validators
from urllib.request import urlopen
def check_valid_url(url):
    if (validators.url(url)==False):
        print('URL validation failed, trying urlopen...')
    try:
        u = urlopen(url)
        u.close()
        return True
    except:
        print('URL invalid')
        return False


EMBEDDING_SERVER = "http://26.48.117.115/"
BIN_ALIGN_PATH = "../preprocess/normalizedALIGN.index"
BIN_CLIP_PATH = "../preprocess/normalizedCLIP.index"
BIN_DINOV2_PATH = "../preprocess/dinov2_index.bin"
KEYFRAMES_JSON = "keyframes_path.json"
DATA_PATH = "../data"
KEYFRAMES_PATH = DATA_PATH+"/keyframes"
RESIZED_PATH = DATA_PATH+"/keyframes_resized"
OCR_WHOOSH_PATH = "../preprocess/whooshdir"
CODETR_DIRECTORY = "../preprocess/codetr/index_bm25_corpus_2"
KEYFRAMES_MAPPING_PATH = "../preprocess/map-keyframes.json"
CHUNK_SIZE = 1024 * 1024

utils.embeddingserver.EMBEDDING_SERVER = EMBEDDING_SERVER
utils.ocr.OCR_WHOOSH_PATH = OCR_WHOOSH_PATH
utils.ocr.init()
utils.co_detr.DIRECTORY_INDEX = CODETR_DIRECTORY
utils.co_detr.init()

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)

app = FastAPI()
db = utils.myfaiss.FaissDB(BIN_ALIGN_PATH,BIN_CLIP_PATH,BIN_DINOV2_PATH)

with open('thumbnail_path.json') as json_file: #tam thoi
    json_dict = json.load(json_file)
imgidx2path = {}
imgidx2thumbnailidx = {}
thumbnailidx2imgidx =  {}
thumbnailidx2path = {}
for key, value in json_dict.items():
    imgidx2path[int(key)] = value
    imgidx2thumbnailidx[int(key)] = int(key)
    thumbnailidx2imgidx[int(key)] = [int(key)]
thumbnailidx2path = imgidx2path

keyframes_path = json.load(open(KEYFRAMES_JSON))
keyframes_mapping = json.load(open(KEYFRAMES_MAPPING_PATH))

app.mount("/palette", StaticFiles(directory="static/palette"), name="home")
app.mount("/concac", StaticFiles(directory="static"), name="static")
app.mount("/img", StaticFiles(directory="static/img"), name="img")
app.mount("/data", StaticFiles(directory=DATA_PATH), name="data")

@app.get("/")
async def root():
    return "hello"

@app.get("/home", response_class=HTMLResponse)
async def home(request: Request, scene_description: str|None = '',
            num_clip_query: int = 60, url_query: str|None = '',
            query_type: str|None = '', idx_query: int|None = -1,
            num_show_query: int = 20, od_query: str|None = '',
            next_scene_description: str|None = '',
            last_displayStyle: str|None = 'grid',
            model_name: str|None = 'CLIP', string_query: str|None = ''):
    img_idx = None
    global uploaded_img
    if (query_type=='image' and uploaded_img != None):
        img_idx, scores = db.vec_search(uploaded_img_feature, num_clip_query, model_name)
    if (query_type=='url' and check_valid_url(url_query)):
        img_idx, scores = db.url_search(url_query, num_clip_query, model_name)
    if (query_type=='text' and scene_description != None and scene_description != ''):
        img_idx, scores = db.text_search(scene_description,num_clip_query, model_name)
    if (query_type=='idx' and idx_query != None):
        img_idx, scores = db.idx_search(idx_query,num_clip_query, model_name)
    if (query_type=='dinov2' and idx_query != None):
        img_idx, scores = db.idx_dinov2_search(idx_query,num_clip_query)
    if (query_type=='ocr' and string_query != ''):
        img_idx = utils.ocr.get_ocr(string_query, num_clip_query)
        scores = list(range(len(img_idx),0,-1))
    if (query_type=='od' and od_query != ''):
        img_idx, scores = utils.co_detr.get_top_k(od_query, num_clip_query)    
    if (query_type=='texttext' and 
        scene_description != None and scene_description != '' and
        next_scene_description != None and next_scene_description != ''):
        # k = min(num_clip_query, 1000)
        k1 = 800
        k2 = 500
        assert k1*k2 >= num_show_query
        img_idx1, scores1 = db.text_search(scene_description, k1, model_name)
        img_idx2, scores2 = db.text_search(next_scene_description, k2, model_name)
        img_idx, scores = utils.metric_2_ids(img_idx1, scores1, img_idx2, scores2, num_clip_query)
    data = []
    if (not img_idx is None):
        for idx, score in zip(img_idx,scores):
            # if (idx not in imgidx2path):
            #     continue
            data.append({'frame_index':idx, 
                'path': 'data/keyframes/'+keyframes_path[idx],
                'video': utils.get_video_keyframe_path(keyframes_path[idx]), 
                'score': score})

        # print(scene_description, data)
        with open('static/reponse/data.json', 'w') as f:
            print('WRITED')
            json.dump(data, f, cls=NpEncoder)
        print(data)

    return templates.TemplateResponse(
        request=request, name="home.html", 
        context={"id": id, "scene_description":scene_description,
                "num_clip_query": num_clip_query, "url_query": url_query,
                "query_type": query_type, 
                "idx_query": idx_query,
                "model_name": model_name,
                "string_query": string_query,
                "num_show_query": num_show_query,
                "next_scene_description": next_scene_description,
                "last_displayStyle": last_displayStyle,
                "data_response": json.dumps(data, cls=NpEncoder)}
        , data = "con cac"
    )

@app.get("/thumbnail_template/{img_idx}", response_class=HTMLResponse)
async def thumbnail_template(request: Request, img_idx: int):
    path = ""
    # if (img_idx in imgidx2path):
    #     path = imgidx2path[img_idx]
    print('thumbnail queried index: ',img_idx)
    path = 'keyframes_resized/'+keyframes_path[img_idx]
    return templates.TemplateResponse(
        request=request, name="thumbnail_box.html", 
            context={"thumbnail_path": path, 
                    "img_idx":img_idx,
                    "title": str(keyframes_mapping[img_idx]['frame']),
                    "video": utils.get_video_keyframe_path(keyframes_path[img_idx]), 
                    "keyframe_path": 'keyframes/'+keyframes_path[img_idx]}
                    , data = "con cac"
    )

templates = Jinja2Templates(directory="templates")
@app.get("/items/{id}", response_class=HTMLResponse)
async def read_item(request: Request, id: str):
    return templates.TemplateResponse(
        request=request, name="item.html", context={"id": id}
    )


uploaded_img = None
uploaded_img_feature = None
@app.post("/upload_image")
async def image_query_upload(
            model_name: str = Form(...), 
            image: UploadFile = File(...)):
    print('model_name_upload: ', model_name)
    global uploaded_img, uploaded_img_feature
    uploaded_img = image.file
    uploaded_img_feature = utils.embeddingserver.image_feature_file(uploaded_img, model_name)
    print(uploaded_img_feature)
    return {"filename": image.filename}

@app.get("/credits", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse(
        request=request, name="credits.html", context={}, data = "con cac"
    )

@app.get("/slide", response_class=HTMLResponse)
async def root(request: Request,
               id: int|None = 12):
    video = utils.get_video_keyframe_path(keyframes_path[id])
    current_index = utils.get_frame_number_in_video(keyframes_path[id])
    video_keyframes_path = []
    video_resized_keyframes_path = []
    video_keyframes_id = []
    for idx, frame in enumerate((os.listdir(KEYFRAMES_PATH+'/'+video))):
        video_keyframes_path.append('data/keyframes/'+video+'/'+frame)
        video_resized_keyframes_path.append('data/keyframes_resized/'+video+'/'+frame)
        video_keyframes_id.append(id-current_index+idx)
        
    return templates.TemplateResponse(
        request=request, name="slide.html", context={
            "id": current_index, 
            "video_keyframes_path": video_keyframes_path,
            "video_resized_keyframes_path": video_resized_keyframes_path,
            "video_keyframes_id": video_keyframes_id
            }, data = "con cac"
    )


@app.get("/showvideo")
async def home(request: Request, id: int|None = 12):
    video = keyframes_mapping[id]['video']
    timestamp = keyframes_mapping[id]['timestamp']
    fps = keyframes_mapping[id]['fps']
    return templates.TemplateResponse(
        "video.html", context={
            "request": request, 
            "title": video, 
            "timestamp": timestamp,
            "fps": fps,
            "video_path": DATA_PATH+'/video/'+video}
    )
from pathlib import Path
@app.get("/video_streaming")
async def video_endpoint(range: str = Header(None), video_path: str|None = 'L01_V001.mp4'):
    start, end = range.replace("bytes=", "").split("-")
    # start, end = 0, None
    start = int(start)
    # start = max(start-CHUNK_SIZE//16, 0)
    end = int(end) if end else start + CHUNK_SIZE

    #THIS IS FUCKING IMPORTANT (A network error caused the media download to fail part-way.)
    end = min(end, Path(video_path).stat().st_size-1)
    print('streaming ',start,'..',end,' ', video_path)

    with open(video_path, "rb") as video:
        video.seek(start)
        data = video.read(end - start+1)
        assert Path(video_path).stat().st_size, os.path.getsize(video_path)
        filesize = str(Path(video_path).stat().st_size)
        headers = {
            'Content-Range': f'bytes {str(start)}-{str(end)}/{filesize}',
            'Accept-Ranges': 'bytes',
            'Content-Length': str(end - start+1)  # Specify correct content length
        }
        return Response(data, status_code=206, headers=headers, media_type="video/mp4")

@app.post("/submit")
async def submit(request: Request, idx: int, isKeyframe: bool, video: str|None = None):
    with open('static/reponse/submit.txt', "r+") as f:
        f.read()
        if (isKeyframe):
            video = keyframes_mapping[idx]['video']
            idx = keyframes_mapping[idx]['frame']
        else:
            assert(video != None)
        data = video[:-4] +',' + str(idx)+'\n'
        f.write(data)
    return 'submit ok'

@app.get("/translate")
async def translate(request: Request, text: str, dest: str = 'en', src = 'vi'):
    return utils.translate.translate(text, dest, src)


@app.get("/test", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse(
        request=request, name="home.html", context={"id": id, "scene_description":"nam mo"}, data = "con cac"
    )

@app.get("/test_embedding")
async def test_embedding():
    vec = utils.embeddingserver.text_feature("I love you baby")
    return json.dumps(vec, cls=NpEncoder)

