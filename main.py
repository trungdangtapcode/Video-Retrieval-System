from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
# import utils.myfaiss

app = FastAPI()



@app.get("/")
async def root():
    return "hello"

app.mount("/palette", StaticFiles(directory="static/palette"), name="palette")
@app.get("/home", response_class=HTMLResponse)
async def home(request: Request, id: int = 0):
    return templates.TemplateResponse(
        request=request, name="item.html", context={"id": id}
    )



app.mount("/concac", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
@app.get("/items/{id}", response_class=HTMLResponse)
async def read_item(request: Request, id: str):
    return templates.TemplateResponse(
        request=request, name="item.html", context={"id": id}
    )