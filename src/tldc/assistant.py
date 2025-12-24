from __future__ import annotations
from typing import Type
from pydantic import BaseModel, Field
from xai_sdk.chat import tool
from .db import DB
from .dirtree import DirTree

_registry: dict[str, Type['Assistant']] = {}

class ReadFileRequest(BaseModel):
    path: str = Field(description="Path to the file, relative to the working directory.")

class WriteFileRequest(BaseModel):
    path: str = Field(description="Path to the file, relative to the working directory.")
    search: str = Field(description="Part of the file to replace. Exactly as it appears in the file, no extra escape codes. When only adding new code, search for surrounding lines and include them in the replacement. There should be only one match. If empty, entire file will be rewritten.")
    replace: str = Field(description="Text to replace search with. Perfectly formatted, with correct indentation, as it's supposed to look like in the file.")

class ListCurrentDirRequest(BaseModel):
    pass

class ListDirRequest(BaseModel):
    path: str = Field(description="Relative path to the directory whose contents to list.")

class Assistant:
    def __init__(self, model, provider, settings, db: DB, dirtree: DirTree):
        self.model = model
        self.provider = provider
        self.db = db
        self.dirtree = dirtree

    tool_definitions = [
        tool(
            name="read_file",
            description="Returns file contents from given path or an error message.",
            parameters=ReadFileRequest.model_json_schema(),
        ),
        tool(
            name="write_file",
            description="Writes file contents to given path. Returns OK or an error message.",
            parameters=WriteFileRequest.model_json_schema(),
        ),
        tool(
            name="list_current_dir",
            description="Returns json list of direct child entries (files and directories) in the current working directory. Paths are relative to cwd (basenames). Each entry has 'path' and 'is_dir' (boolean).",
            parameters=ListCurrentDirRequest.model_json_schema(),
        ),
        tool(
            name="list_dir",
            description="Returns json list of direct child entries (files and directories) in the given relative directory path. Paths are relative to cwd. Each entry has 'path' and 'is_dir' (boolean).",
            parameters=ListDirRequest.model_json_schema(),
        ),
    ]

    request_classes = {
        "read_file": ReadFileRequest,
        "write_file": WriteFileRequest,
        "list_current_dir": ListCurrentDirRequest,
        "list_dir": ListDirRequest,
    }

    def read_file(self, request: ReadFileRequest):
        return self.dirtree.read_file(request.path)

    def write_file(self, request: WriteFileRequest):
        return self.dirtree.write_file(request.path, request.search, request.replace)

    def list_current_dir(self, request: ListCurrentDirRequest):
        return self.dirtree.list_current_dir()

    def list_dir(self, request: ListDirRequest):
        return self.dirtree.list_dir(request.path)

    tools_map = {
        "read_file": read_file,
        "write_file": write_file,
        "list_current_dir": list_current_dir,
        "list_dir": list_dir,
    }

    def prompt(self, prompt):
        pass

    def reset(self):
        self.db.reset_response_id(self.dirtree.cwd)
        self.db.del_history(self.dirtree.cwd)
        self.dirtree.reset()

    @classmethod
    def create(cls, model, provider, settings, db: DB, dirtree: DirTree) -> 'Assistant':
        sub_cls: Type['Assistant'] = _registry.get(provider)
        if sub_cls is None:
            raise ValueError(f"Provider not implemented: {provider}")
        return sub_cls(model, provider, settings, db, dirtree)

def register(provider, cls: Type['Assistant']):
    _registry[provider] = cls
