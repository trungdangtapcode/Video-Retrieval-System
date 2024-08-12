from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import utils.myfaiss
import json
import numpy as np

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
# db = utils.myfaiss.FaissDB("index.bin")

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

app.mount("/palette", StaticFiles(directory="static/palette"), name="home")
app.mount("/concac", StaticFiles(directory="static"), name="static")
app.mount("/img", StaticFiles(directory="static/img"), name="img")

@app.get("/")
async def root():
    return "hello"

@app.get("/home", response_class=HTMLResponse)
async def home(request: Request, scene_description: str|None = None, num_clip_query: int = 24):
    return
    if (scene_description != None):
        img_idx = db.text_search(scene_description,num_clip_query)
        # print(img_idx)
        data = []
        for idx in img_idx:
            if (idx not in imgidx2path):
                continue
            data.append({'frame_index':idx, 'path': imgidx2path[idx]})
        # print(scene_description, data)
        with open('static/reponse/data.json', 'w') as f:
            json.dump(data, f, cls=NpEncoder)

    return templates.TemplateResponse(
        request=request, name="home.html", context={"id": id, "scene_description":scene_description}, data = "con cac"
    )

@app.get("/thumbnail_template/{img_idx}", response_class=HTMLResponse)
async def thumbnail_template(request: Request, img_idx: int):
    path = ""
    if (img_idx in imgidx2path):
        path = imgidx2path[img_idx]
    return templates.TemplateResponse(
        request=request, name="thumbnail_box.html", context={"thumbnail_path": path, "img_idx":img_idx}, data = "con cac"
    )

templates = Jinja2Templates(directory="templates")
@app.get("/items/{id}", response_class=HTMLResponse)
async def read_item(request: Request, id: str):
    return templates.TemplateResponse(
        request=request, name="item.html", context={"id": id}
    )


@app.get("/test", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse(
        request=request, name="test.html", context={"id": id, "scene_description":"nam mo"}, data = "con cac"
    )