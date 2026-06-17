from __future__ import annotations
from typing import Type
from pydantic import BaseModel, Field
from xai_sdk.chat import tool
from ddgs import DDGS
from .db import DB
from .dirtree import DirTree
from .websearch import WebSearch

_registry: dict[str, Type['Assistant']] = {}

class ReadFileRequest(BaseModel):
    path: str = Field(description="Path to the file, relative to the working directory.")

class WriteFileRequest(BaseModel):
    path: str = Field(description="Path to the file, relative to the working directory.")
    content: str = Field(description="Text to write to the file. Perfectly formatted, with correct indentation, as it's supposed to look like in the file.")

class ListDirRequest(BaseModel):
    path: str = Field(description="Relative path to the directory whose contents to list.")

class WebSearchRequest(BaseModel):
    query: str = Field(description="Search query for web search. Maximum 3 results will be returned.")

class WebFetchRequest(BaseModel):
    url: str = Field(description="Url to fetch. Content will be returned as markdown.")

class Assistant:
    def __init__(self, model, provider, settings, db: DB, dirtree: DirTree):
        self.model = model
        self.provider = provider
        self.settings = settings
        self.db = db
        self.dirtree = dirtree
        self.websearch = WebSearch()

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
            name="list_dir",
            description="Returns json list of direct child entries (files and directories) in the given relative directory path. Paths are relative to cwd. Each entry has 'path' and 'is_dir' (boolean).",
            parameters=ListDirRequest.model_json_schema(),
        ),
        tool(
            name="web_search",
            description="Searches the web and returns up to 3 results with URLs, titles, and snippets.",
            parameters=WebSearchRequest.model_json_schema(),
        ),
        tool(
            name="web_fetch",
            description="Fetches url contents as markdown.",
            parameters=WebFetchRequest.model_json_schema(),
        ),
    ]

    request_classes = {
        "read_file": ReadFileRequest,
        "write_file": WriteFileRequest,
        "list_dir": ListDirRequest,
        "web_search": WebSearchRequest,
        "web_fetch": WebFetchRequest
    }

    def read_file(self, request: ReadFileRequest):
        return self.dirtree.read_file(request.path)

    def write_file(self, request: WriteFileRequest):
        return self.dirtree.write_file(request.path, request.content)

    def list_dir(self, request: ListDirRequest):
        return self.dirtree.list_dir(request.path)

    def web_search(self, request: WebSearchRequest):
        return self.websearch.search(request.query)

    def web_fetch(self, request: WebFetchRequest):
        return self.websearch.fetch_content(request.url)

    tools_map = {
        "read_file": read_file,
        "write_file": write_file,
        "list_dir": list_dir,
        "web_search": web_search,
        "web_fetch": web_fetch
    }

    def prompt(self, prompt):
        pass

    def reset(self):
        self.db.reset_response_id(self.dirtree.cwd)
        self.db.del_history(self.dirtree.cwd)

    @classmethod
    def create(cls, model, provider, settings, db: DB, dirtree: DirTree) -> 'Assistant':
        sub_cls: Type['Assistant'] = _registry.get(provider)
        if sub_cls is None:
            raise ValueError(f"Provider not implemented: {provider}")
        return sub_cls(model, provider, settings, db, dirtree)

def register(provider, cls: Type['Assistant']):
    _registry[provider] = cls
