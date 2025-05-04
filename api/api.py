from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import os
import json
import uvicorn
import threading

from util_io import get_temp_path



class FileList(BaseModel):
    files: Dict[str, List[str]]


class Status(BaseModel):
    status: Dict[str, Any]


def get_files_in_dir(path: str) -> Dict[str, List[str]]:
    result = {}
    for root, _, files in os.walk(path):
        relative_path = os.path.relpath(root, path)
        if relative_path == '.':
            relative_path = ''
        result[relative_path] = files
    return result



app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/files", response_model=FileList)
async def list_files():
    temp_path = get_temp_path()
    return FileList(files=get_files_in_dir(temp_path))


@app.get("/status", response_model=Status)
async def get_status():
    status_path = os.path.join(get_temp_path(), "status", "status.json")
    with open(status_path, "r") as f:
        status_data = json.load(f)
    return Status(status=status_data)


def run_server():
    uvicorn.run(app, host="0.0.0.0", port=8080)


def start_api():
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    print("API Started")

