import json
from pathlib import Path
from datetime import datetime

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent
STORAGE_PATH = BASE_DIR / "storage" / "data.json"

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/message", response_class=HTMLResponse)
async def message_form(request: Request):
    return templates.TemplateResponse("message.html", {"request": request})

@app.post("/message")
async def save_message(username: str = Form(...), message: str = Form(...)):
    data = {}
    if STORAGE_PATH.exists():
        with open(STORAGE_PATH, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = {}

    timestamp = str(datetime.now())
    data[timestamp] = {"username": username, "message": message}

    with open(STORAGE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return RedirectResponse(url="/read", status_code=303)

@app.get("/read", response_class=HTMLResponse)
async def read_messages(request: Request):
    data = {}
    if STORAGE_PATH.exists():
        with open(STORAGE_PATH, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = {}

    return templates.TemplateResponse("read.html", {"request": request, "messages": data})
    
@app.exception_handler(404)
async def not_found(request: Request, exc):
    return templates.TemplateResponse("error.html", {"request": request}, status_code=404)

