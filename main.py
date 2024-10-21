import os
from fastapi import FastAPI, File, Form, Header, Request, UploadFile, status, Response
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import utils.asr
import utils.myfaiss
import utils.embeddingserver
import utils.ocr
import utils.co_detr
import utils.translate
import utils.dres_submit
import utils.asr
import utils.beit
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


EMBEDDING_SERVER = "http://26.48.117.115:80/"
EMBEDDING_SERVER_INTERNVIDEO = 'http://192.168.195.190:8000/'
BIN_ALIGN_PATH = "../preprocess/normalizedALIGN.index"
BIN_CLIP_PATH = "../preprocess/embed_batch3/clip_all.index"
BIN_CLIP_PATH_OLDKEYFRAME = "../preprocess/clip12_oldonly.index"
BIN_DINOV2_PATH = "../preprocess/embed_batch3/dino_all.index"
# BIN_INTERVIDEO_SPACE_PATH = "../preprocess/intern_batch3/intern_4scenes_all.index"
# BIN_INTERVIDEO_TIME_PATH = "../preprocess/intern_batch3/intern_1scene_all.index"
BIN_INTERVIDEO_SPACE_PATH = "../preprocess/intern_batch2/space_batch12.index"
BIN_INTERVIDEO_TIME_PATH = "../preprocess/intern_batch2/time_batch2.index"
KEYFRAMES_JSON = "../preprocess/keyframespath_batch3.json"
DATA_PATH = "../data"
KEYFRAMES_PATH = DATA_PATH+"/keyframes"
RESIZED_PATH = DATA_PATH+"/keyframes_resized"
OCR_WHOOSH_PATH = "../preprocess/ocr_batch3/whoosh_dir"
OCR_CORPUS_PATH = "../preprocess/ocr_batch3/OCR_combined_all.json"
ASR_WHOOSH_PATH = "../preprocess/ytb/whooshdir4"
CODETR_DIRECTORY = "../preprocess/codetr/index_bm25_corpus_3"
CODETR_COPUS_DIRECTORY = "../preprocess/codetr/Co-DETR_mscoco.json"
KEYFRAMES_MAPPING_PATH = "../preprocess/mapping3/map-keyframes.json"
# INTERNVIDEO_SPACE_MAP_PATH = "../preprocess/intern_batch3/intern_4scenes_mapping_all.json"
# INTERNVIDEO_TIME_MAP_PATH = "../preprocess/intern_batch3/intern_1scene_mapping_all.json"
INTERNVIDEO_SPACE_MAP_PATH = "../preprocess/intern_batch2/internSpace2_to_index.json"
INTERNVIDEO_TIME_MAP_PATH = "../preprocess/intern_batch2/internTime2_to_index.json"
CHUNK_SIZE = 1024 * 1024
EVAL_ID = "a5103664-cf48-4705-9536-3dbd84a81620"
SESSION_ID = "u1K-_oNPFliQ_4Pi5wVd37pErWZR-54k"
ASR_MAPPING_PATH = '../preprocess/ytb/asr_mapping.json'
BEIT_URL_SERVER = 'https://f39a-34-127-60-122.ngrok-free.app'

utils.beit.URL_SERVER = BEIT_URL_SERVER
utils.embeddingserver.EMBEDDING_SERVER = EMBEDDING_SERVER
utils.embeddingserver.EMBEDDING_SERVER_INTERNVIDEO = EMBEDDING_SERVER_INTERNVIDEO
utils.ocr.OCR_WHOOSH_PATH = OCR_WHOOSH_PATH
utils.ocr.init()
utils.co_detr.DIRECTORY_INDEX = CODETR_DIRECTORY
utils.co_detr.init()

utils.dres_submit.evaluationID = EVAL_ID
utils.dres_submit.sessionID = SESSION_ID

utils.asr.ASR_WHOOSH_PATH = ASR_WHOOSH_PATH
utils.asr.ASR_MAPPING_PATH = ASR_MAPPING_PATH
utils.asr.init()

od_corpus = json.load(open(CODETR_COPUS_DIRECTORY))
ocr_corpus = json.load(open(OCR_CORPUS_PATH))

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
db = utils.myfaiss.FaissDB(BIN_ALIGN_PATH,BIN_CLIP_PATH,BIN_DINOV2_PATH, 
    BIN_INTERVIDEO_SPACE_PATH, BIN_INTERVIDEO_TIME_PATH,BIN_CLIP_PATH_OLDKEYFRAME)

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
internvideo_space_map_index = json.load(open(INTERNVIDEO_SPACE_MAP_PATH))
internvideo_time_map_index = json.load(open(INTERNVIDEO_TIME_MAP_PATH))
# I, _ = db.text_search_internvideo_space('his photograph shows a man in a blue uniform, who appears to be a prisoner or suspect, sitting at a table signing papers. Sitting across from him is a police officer, dressed in a green uniform, who is instructing or supervising the signing process. The scene looks like an office or police facility, with a barred window and a wooden wall with many small holes behind it. The scene suggests that this may be an interrogation or deposition in an official investigation.',15,internvideo_space_map_index)
# for idx in I:
#     num = utils.get_frame_number_in_video(keyframes_path[idx])
#     video = utils.get_video_keyframe_path(keyframes_path[idx])
#     print(num, video)

app.mount("/palette", StaticFiles(directory="static/palette"), name="home")
app.mount("/concac", StaticFiles(directory="static"), name="static")
app.mount("/img", StaticFiles(directory="static/img"), name="img")
app.mount("/data", StaticFiles(directory=DATA_PATH), name="data")

@app.get("/")
async def root():
    return "hello"

tmp = json.load(open('../preprocess/ocr_batch2/combined.json'))
whoosh_mapping = list(range(106589)) + list(range(298000,298000+94657))
@app.get("/home", response_class=HTMLResponse)
async def home(request: Request, scene_description: str|None = '',
            num_clip_query: int = 60, url_query: str|None = '',
            query_type: str|None = '', idx_query: int|None = -1,
            num_show_query: int = 20, od_query: str|None = '',
            next_scene_description: str|None = '',
            last_displayStyle: str|None = 'grid',
            last_newold: str|None = 'newold',
            model_name: str|None = 'CLIP', 
            ocr_query: str|None = '',
            asr_query: str|None = '',
            intern_query: str|None = ''):
    img_idx = None
    global uploaded_img
    if (query_type=='image' and uploaded_img != None):
        img_idx, scores = db.vec_search(uploaded_img_feature, num_clip_query, model_name)
    if (query_type=='url' and check_valid_url(url_query)):
        img_idx, scores = db.url_search(url_query, num_clip_query, model_name)
    if (query_type=='text' and scene_description != None and scene_description != ''):
        img_idx, scores = db.text_search(scene_description,num_clip_query, model_name)
        # for i in range(len(img_idx)):
        #     print(len(tmp),img_idx[i],img_idx[i] if img_idx[i] < 106589 else img_idx[i]-298000)
        #     if (img_idx[i] not in whoosh_mapping or img_idx[i] < 106589):
        #         img_idx[i] = 0
        #         continue
        #     if ("70" not in tmp[img_idx[i] if img_idx[i] < 106589 else img_idx[i]-298000]):
        #         img_idx[i] = 0
    if (query_type=='idx' and idx_query != None):
        img_idx, scores = db.idx_search(idx_query,num_clip_query, model_name)
    if (query_type=='dinov2' and idx_query != None):
        img_idx, scores = db.idx_dinov2_search(idx_query,num_clip_query)
    if (query_type=='ocr' and ocr_query != ''):
        img_idx = utils.ocr.get_ocr(ocr_query, num_clip_query)
        scores = list(range(len(img_idx),0,-1))
    if (query_type=='od' and od_query != ''):
        img_idx, scores = utils.co_detr.get_top_k(od_query, num_clip_query)    
    if (query_type=='texttext' and 
        scene_description != None and scene_description != '' and
        next_scene_description != None and next_scene_description != ''):
        # k = min(num_clip_query, 1000)
        k1 = 1800
        k2 = 1500
        assert k1*k2 >= num_show_query
        img_idx1, scores1 = db.text_search(scene_description, k1, model_name)
        img_idx2, scores2 = db.text_search(next_scene_description, k2, model_name)
        img_idx, scores = utils.metric_2_ids(img_idx1, scores1, img_idx2, scores2, 
                            num_clip_query, keyframes_mapping)
    if (query_type=='text_ivs' and scene_description != None and scene_description != ''):
        img_idx, scores = db.text_search_internvideo_space(scene_description, num_clip_query, internvideo_space_map_index)
        # img_idx, scores = db.text_search_internvideo_space_p(intern_query, num_clip_query, internvideo_space_map_index)
    if (query_type=='text_ivt' and scene_description != None and scene_description != ''):
        # img_idx, scores = db.text_search_internvideo_time(scene_description, num_clip_query, internvideo_time_map_index)
        img_idx, scores = db.text_search_internvideo_time_p(intern_query, num_clip_query, internvideo_time_map_index)
    if (query_type=='texttext_ivt' and 
        scene_description != None and scene_description != '' and
        next_scene_description != None and next_scene_description != ''):
        # k = min(num_clip_query, 1000)
        k1 = 1800
        k2 = 1500
        assert k1*k2 >= num_show_query
        # img_idx1, scores1 = db.text_search_internvideo_time(scene_description, k1, internvideo_time_map_index)
        # img_idx2, scores2 = db.text_search_internvideo_time(next_scene_description, k2, internvideo_time_map_index)
        img_idx1, scores1 = db.text_search_internvideo_time(scene_description, k1, internvideo_time_map_index)
        img_idx2, scores2 = db.text_search_internvideo_time(next_scene_description, k2, internvideo_time_map_index)
        print("QUERY OK.. start compare (intern)")
        img_idx, scores = utils.metric_2_ids(img_idx1, scores1, img_idx2, scores2, 
                            num_clip_query, keyframes_mapping)
    if (query_type=='text_od' and scene_description != None and scene_description != ''
        ):
        k1 = 3000
        # k2 = 10000
        img_idx1, scores1 = db.text_search_oldkeyframe(scene_description, k1)
        # img_idx2, scores2 = utils.co_detr.get_top_k(od_query, k2)
        print("QUERY OK.. start compare (od)", scene_description, od_query)
        # print(img_idx1[:10], img_idx2[:10])
        img_idx, scores = utils.metric_2_ids_text_od(img_idx1, od_query, od_corpus , num_clip_query)
    if (query_type=='asr' and asr_query != ''):
        img_idx = utils.asr.get_ocr(asr_query, num_clip_query)
        scores = list(range(len(img_idx),0,-1))
    if (query_type=='beit' and scene_description != None and scene_description != ''):
        img_idx, scores = utils.beit.text_seach(scene_description, num_clip_query)
    if (query_type=='beitbeit' and
        scene_description != None and scene_description != '' and
        next_scene_description != None and next_scene_description != ''):
        k1 = 1800
        k2 = 1500
        assert k1*k2 >= num_show_query
        img_idx1, scores1 = utils.beit.text_seach(scene_description, k1)
        img_idx2, scores2 = utils.beit.text_seach(next_scene_description, k2)
        print("QUERY OK.. start compare (intern)")
        img_idx, scores = utils.metric_2_ids(img_idx1, scores1, img_idx2, scores2, 
                            num_clip_query, keyframes_mapping)
    if (query_type=='beit_idx' and idx_query != None):
        img_idx, scores = utils.beit.index_search(idx_query,num_clip_query)
    # if (query_type=='text_ocr' and scene_description != None and scene_description != ''):
    #     k1 = 3000
    #     img_idx1, scores1 = utils.beit.text_seach(scene_description, k1)
    #     print("QUERY OK.. start compare (ocr)", scene_description, ocr_query)
    #     img_idx, scores = utils.metric_2_ids_text_od(img_idx1, ocr_query, ocr_corpus , num_clip_query)


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
                "asr_query": asr_query,
                "ocr_query": ocr_query,
                "num_show_query": num_show_query,
                "next_scene_description": next_scene_description,
                "last_displayStyle": last_displayStyle,
                "last_newold": last_newold,
                "intern_url": EMBEDDING_SERVER_INTERNVIDEO,
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
                    "keyframe_path": 'keyframes/'+keyframes_path[img_idx],
                    "newold": utils.get_newold_from_path(keyframes_path[img_idx])}
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
    ##>500 => window not sort
    print(video)
    sorted_frames = sorted(
        os.listdir(KEYFRAMES_PATH+'/'+video), 
        key = lambda x: int(x.split('.')[0]))
    for idx, frame in enumerate(sorted_frames):
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


import cv2
@app.get("/showvideo")
async def home(request: Request, id: int|None = 12,
               video_inp: str|None = None,
               frame_idx_inp: int|None = None):
    if (video_inp!=None and frame_idx_inp!=None):
        video = video_inp
        fps = cv2.VideoCapture(DATA_PATH+'/video/'+video).get(cv2.CAP_PROP_FPS)
        timestamp = frame_idx_inp/fps
    else:    
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

@app.post("/submit_dres_kis")
async def submit(request: Request, idx: int, isKeyframe: bool, video: str|None = None):
    if (isKeyframe):
        video = keyframes_mapping[idx]['video']
        idx = keyframes_mapping[idx]['timestamp']*1000
    else:
        assert(video != None)
    return utils.dres_submit.submit_kis(video[:-4], idx)

@app.post("/submit_dres_qa")
async def submit(request: Request, idx: int, isKeyframe: bool, qa: str, video: str|None = None):
    if (isKeyframe):
        video = keyframes_mapping[idx]['video']
        idx = keyframes_mapping[idx]['timestamp']*1000
    else:
        assert(video != None)
    answer_qa = str(qa)+'-'+str(video[:-4])+'-'+str(idx)
    return utils.dres_submit.submit_qa(answer_qa)

@app.get("/translate")
async def translate(request: Request, text: str, dest: str = 'en', src = 'vi'):
    return utils.translate.translate(text, dest, src)

@app.get("/checkvar")
async def checkvar(request: Request):
    return templates.TemplateResponse(
        request=request, name="checkvar.html", context={
        }, data = "con cac"
    )

@app.get("/checkvar2")
async def checkvar(request: Request):
    return templates.TemplateResponse(
        request=request, name="checkvar2.html", context={
        }, data = "con cac"
    )

@app.get("/get_frame")
async def get_frame(request: Request, idx: int, video: str):
    if (video[-4:] != '.mp4'): video += '.mp4'
    cam = cv2.VideoCapture(DATA_PATH+'/video/'+video)
    cam.set(cv2.CAP_PROP_POS_FRAMES, idx)
    ret, frame = cam.read()
    ret, value = cv2.imencode(".jpg", frame)
    img_bytes = value.tobytes()
    return Response(content=img_bytes, media_type="image/jpg")

@app.post("/get_file_local")
async def get_file_local(request: Request, file: UploadFile = File(...)):
    path = '../file_local'
    try:
        contents = file.file.read()
        with open(path+'/'+file.filename, 'wb') as f:
            f.write(contents)
    except Exception:
        return {"message": "There was an error uploading the file"}
    finally:
        file.file.close()
    return "ok"

@app.get("/test", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse(
        request=request, name="home.html", context={"id": id, "scene_description":"nam mo"}, data = "con cac"
    )

@app.get("/test_embedding")
async def test_embedding():
    vec = utils.embeddingserver.text_feature("I love you baby")
    return json.dumps(vec, cls=NpEncoder)

@app.get("/update_id")
async def update_id(eval: str,  session: str):
    EVAL_ID = eval
    SESSION_ID = session
    utils.dres_submit.evaluationID = EVAL_ID
    utils.dres_submit.sessionID = SESSION_ID
    return 'ok'

@app.get("/update_url")
async def update_url(url: str):
    BEIT_URL_SERVER = url 
    utils.beit.URL_SERVER = BEIT_URL_SERVER