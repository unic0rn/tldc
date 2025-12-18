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
        self.path = Path(self.cwd)
        self.root = str(self.path)
        self.files = []
        self.dirs = [self.root]
        for p in self.path.iterdir():
            if self.check_path(p):
                fstr = str(p)
                if p.is_file():
                    self.files.append(fstr)
                else:
                    self.dirs.append(fstr)
                if p.is_dir():
                    self._collect_recursive(p)
        self.statuses = {}
        for fullp in self.files + self.dirs:
            self.refresh(fullp)

    def _collect_recursive(self, dirp):
        for subp in dirp.iterdir():
            if self.check_path(subp):
                fstr = str(subp)
                if subp.is_file():
                    self.files.append(fstr)
                else:
                    self.dirs.append(fstr)
                if subp.is_dir():
                    self._collect_recursive(subp)

    def get_checksum(self, fullp: str) -> str:
        p = Path(fullp)
        if p.is_file():
            with open(fullp, "rb") as f:
                return md5(f.read()).hexdigest()
        if not p.is_dir():
            return md5(f"{fullp} is not a file or directory").hexdigest()
        children_str = []
        for child in sorted(p.iterdir(), key=lambda c: c.name):
            if self.check_path(child):
                try:
                    mtime = int(child.stat().st_mtime)
                except OSError:
                    mtime = 0
                children_str.append(f"{child.name}:{mtime}")
        content = "\n".join(children_str).encode()
        if not content:
            content = b""
        return md5(content).hexdigest()

    def refresh(self, fullp: str):
        current_checksum = self.get_checksum(fullp)
        status = self.db.get_status(fullp)
        is_synced = 1 if status and status["checksum"] == current_checksum and status["is_synced"] == 1 else 0
        self.db.set_status(fullp, current_checksum, is_synced)
        self.statuses[fullp] = is_synced

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
                    self.mark_synced(p)
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

    def write_file(self, p: str, data: str):
        fullp = self._from_relative(p)
        if fullp.startswith(f"{self.cwd}/") and ".git" not in fullp[len(self.cwd):]:
            pp = Path(fullp)
            dirp = pp.parent
            os.makedirs(str(dirp), exist_ok=True)
            logger(f"Writing {p}")
            with open(fullp, "w") as file:
                file.write(data)
            self.mark_synced(p)
            current_dir = str(pp.parent)
            while True:
                self.statuses[current_dir] = 0
                self.db.reset_status(current_dir)
                if current_dir == self.root:
                    break
                current_dir = str(Path(current_dir).parent)
            return "OK"
        else:
            logger(f"AI tried to write {p}, access denied", "warn")
            return f"Trying to write {p}: access denied"

    def mark_synced(self, relp: str):
        fullp = self._from_relative(relp)
        checksum = self.get_checksum(fullp)
        self.db.set_status(fullp, checksum, 1)
        self.statuses[fullp] = 1

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
                    "is_synced": self.statuses.get(child_full, 0)
                })
        self.mark_synced(relpath)
        return entries

    def reset(self):
        self.db.reset_statuses(self.cwd)
        self.statuses = {p: 0 for p in self.statuses}

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
