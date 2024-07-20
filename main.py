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
db = utils.myfaiss.FaissDB("index.bin")

with open('img_path.json') as json_file: #tam thoi
    json_dict = json.load(json_file)
imgidx2path = {}
for key, value in json_dict.items():
   imgidx2path[int(key)] = value

app.mount("/palette", StaticFiles(directory="static/palette"), name="home")
app.mount("/concac", StaticFiles(directory="static"), name="static")
app.mount("/img", StaticFiles(directory="static/img"), name="img")

@app.get("/")
async def root():
    return "hello"

@app.get("/home", response_class=HTMLResponse)
async def home(request: Request, scene_description: str|None = None):
    if (scene_description != None):
        img_idx = db.text_search(scene_description,10)
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
        request=request, name="home.html", context={"id": id}, data = "con cac"
    )

@app.get("/thumbnail_template/{img_idx}", response_class=HTMLResponse)
async def thumbnail_template(request: Request, img_idx: int):
    path = ""
    if (img_idx in imgidx2path):
        path = imgidx2path[img_idx]
    return templates.TemplateResponse(
        request=request, name="thumbnail_box.html", context={"thumbnail_path": path}, data = "con cac"
    )

templates = Jinja2Templates(directory="templates")
@app.get("/items/{id}", response_class=HTMLResponse)
async def read_item(request: Request, id: str):
    return templates.TemplateResponse(
        request=request, name="item.html", context={"id": id}
    )