from pathlib import Path

from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import FileResponse

from graph_extractor import GraphExtractor

app = FastAPI()

jsons = Path('.')
frontend = Path('dist/')
extractor = GraphExtractor()


@app.get("/")
async def root():
    return FileResponse(frontend / 'index.html')


@app.get("/main.js")
async def js():
    return FileResponse(frontend / 'main.js')


@app.get("/main.css")
async def css():
    return FileResponse(frontend / 'main.css')


@app.post("/upload")
async def upload_data(file: UploadFile = File(...), language: str = Form(...)):
    code = b''
    while content := await file.read(1024):  # async read chunk
        code += content  # async write chunk

    data = extractor.extract_pipeline(code, language)
    # print(data)
    return {
        "type": "graph",
        "error": None,
        "values": {
            "code": code.decode('utf-8'),
            "nodes": data["nodes"],
            "edges": data["edges"],
        }
    }


@app.post("/update")
async def update_code(code: str = Form(...), language: str = Form(...)):
    data = extractor.extract_pipeline(code, language)
    # print(data)
    return {
        "type": "graph",
        "error": None,
        "values": {
            "code": code,
            "nodes": data["nodes"],
            "edges": data["edges"],
        }
    }
