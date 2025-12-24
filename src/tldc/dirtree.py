from pathlib import Path
from hashlib import md5
import os
from .constants import DIRTREE_EXCLUDE
from .constants import DIRTREE_EXCLUDE_ANYWHERE
from .db import DB
from .logger import logger

class DirTree:
    def __init__(self, cwd, db: DB):
        self.cwd = os.path.abspath(cwd)
        self.db = db

    def _to_relative(self, fullp: str) -> str:
        return str(Path(fullp).relative_to(self.cwd))

    def _from_relative(self, rel: str) -> str:
        return str(Path(f"{self.cwd}/{rel}").resolve())

    def read_file(self, p: str):
        fullp = self._from_relative(p)
        pp = Path(fullp)
        if fullp.startswith(f"{self.cwd}/") and ".git" not in fullp[len(self.cwd):]:
            if pp.exists():
                if pp.is_file():
                    logger(f"Reading {p}")
                    with open(fullp, "r") as file:
                        data = file.read()
                    return data
                else:
                    logger(f"AI tried to read {p}, is a directory", "warn")
                    return f"Trying to read {p}: is a directory"
            else:
                logger(f"AI tried to read {p}, no such file or directory", "warn")
                return f"Trying to read {p}: no such file or directory"
        else:
            logger(f"AI tried to read {p}, access denied", "warn")
            return f"Trying to read {p}: access denied"

    def write_file(self, p: str, search: str, replace: str):
        fullp = self._from_relative(p)
        if fullp.startswith(f"{self.cwd}/") and ".git" not in fullp[len(self.cwd):]:
            pp = Path(fullp)
            dirp = pp.parent
            os.makedirs(str(dirp), exist_ok=True)
            if pp.exists() and pp.is_file():
                with open(fullp, "r") as file:
                    data = file.read()
            elif search != "":
                logger(f"AI tried to update {p}, no such file", "warn")
                return f"Trying to update {p}: no such file"
            if search == "":
                logger(f"Creating {p}")
                data = replace
            else:
                logger(f"Updating {p}")
                if data.count(search) != 1:
                    search = search.replace(r'\"', '"')
                    if data.count(search) != 1:
                        logger(f"AI tried to update {p}, search matches != 1", "warn")
                        return f"Trying to update {p}: search matches != 1"
                    else:
                        data = data.replace(search, replace)
                else:
                    data = data.replace(search, replace)
            with open(fullp, "w") as file:
                file.write(data)
            return "OK"
        else:
            logger(f"AI tried to write {p}, access denied", "warn")
            return f"Trying to write {p}: access denied"

    def list_current_dir(self):
        return self._list_dir_entries(".")

    def list_dir(self, relpath: str):
        fullp = self._from_relative(relpath)
        pp = Path(fullp)
        if not fullp.startswith(f"{self.cwd}/"):
            logger(f"AI tried to list {relpath}, access denied", "warn")
            return f"Trying to list {relpath}: access denied"
        if not pp.is_dir():
            logger(f"AI tried to list {relpath}, not a directory", "warn")
            return f"Trying to list {relpath}: not a directory"
        return self._list_dir_entries(relpath)

    def _list_dir_entries(self, relpath: str):
        fullp = self._from_relative(relpath)
        logger(f"Listing {relpath}")
        dirp = Path(fullp)
        entries = []
        for child in sorted(dirp.iterdir(), key=lambda c: c.name):
            if self.check_path(child):
                child_full = str(child.resolve())
                child_rel = self._to_relative(child_full)
                entries.append({
                    "path": child_rel,
                    "is_dir": child.is_dir(),
                })
        return entries

    def check_path(self, p: Path):
        rel_start = len(self.cwd) + 1
        rel = str(p)[rel_start:]
        if rel in DIRTREE_EXCLUDE:
            return False
        parts = str(p).split("/")
        for part in parts:
            basename = part[part.rfind("/") + 1:]
            if basename in DIRTREE_EXCLUDE_ANYWHERE:
                return False
        return True
