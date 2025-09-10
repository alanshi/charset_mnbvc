from __future__ import annotations
import sys
import subprocess
import platform
from typing import Optional, Tuple


"""
跨平台 libmagic wrapper
- 尝试使用: python-magic (libmagic)
- Windows fallback: python-magic-bin / python-libmagic
- 若都不可用: 尝试调用 `file --mime-type` (如果系统有 file)
- 最后回退到 pure-python filetype (若用户安装了 filetype 包)
"""

# try import libmagic-backed python bindings
_magic = None
_magic_name = None
for candidate in ("magic", "libmagic", "python_magic"):
    try:
        _mod = __import__(candidate)
        # python-magic exposes Magic class in module named 'magic'
        _magic = _mod
        _magic_name = candidate
        break
    except Exception:
        continue

# try python-magic-bin style import if not found (usually same name 'magic')
# nothing extra: we already attempted "magic"

# optional pure-python fallback
try:
    import filetype as _filetype  # pip install filetype
except Exception:
    _filetype = None

def _call_file_cmd(path: str) -> Optional[Tuple[str, str]]:
    """Call system `file --mime-type -b` if available."""
    try:
        p = subprocess.run(["file", "--mime-type", "-b", path],
                           capture_output=True, text=True, check=True)
        mime = p.stdout.strip()
        # also get human readable file output
        p2 = subprocess.run(["file", "-b", path], capture_output=True, text=True, check=True)
        desc = p2.stdout.strip()
        return mime, desc
    except Exception:
        return None

class CrossMagic:
    def __init__(self):
        self.backend = None
        if _magic is not None:
            try:
                # python-magic: magic.Magic(mime=True) or magic.from_buffer
                # try to create an instance
                if hasattr(_magic, "Magic"):
                    self.backend = ("python-magic", _magic.Magic(mime=True))
                else:
                    # some variants export functions directly
                    self.backend = ("magic-module", _magic)
            except Exception:
                self.backend = None

    def from_file(self, path: str) -> dict:
        """
        Return a dict like {'mime':..., 'description':..., 'source': 'libmagic'/'file'/'filetype'}
        """
        # try libmagic-based
        if self.backend and self.backend[0].startswith("python"):
            try:
                inst = self.backend[1]
                mime = inst.from_file(path) if hasattr(inst, "from_file") else None
                desc = None
                # if mime may include trailing data, keep safe
                if mime:
                    return {"mime": mime, "description": None, "source": "libmagic"}
            except Exception:
                pass

        # try module-level function fallback
        if _magic is not None:
            try:
                # many bindings provide magic.from_file()
                if hasattr(_magic, "from_file"):
                    out = _magic.from_file(path, mime=True)
                    if out:
                        return {"mime": out, "description": None, "source": f"{_magic_name}"}
            except Exception:
                pass

        # try system 'file'
        res = _call_file_cmd(path)
        if res:
            mime, desc = res
            return {"mime": mime, "description": desc, "source": "file-cmd"}

        # try pure-python filetype
        if _filetype is not None:
            try:
                with open(path, "rb") as f:
                    head = f.read(4096)
                kind = _filetype.guess(head)
                if kind:
                    return {"mime": kind.mime, "description": kind.extension, "source": "filetype-py"}
            except Exception:
                pass

        return {"mime": None, "description": None, "source": "unknown"}

    def from_buffer(self, buf: bytes) -> dict:
        """Detect from bytes buffer."""
        # libmagic
        if self.backend and self.backend[0].startswith("python"):
            try:
                inst = self.backend[1]
                if hasattr(inst, "from_buffer"):
                    mime = inst.from_buffer(buf)
                    return {"mime": mime, "description": None, "source": "libmagic"}
            except Exception:
                pass

        if _magic is not None and hasattr(_magic, "from_buffer"):
            try:
                mime = _magic.from_buffer(buf, mime=True)
                return {"mime": mime, "description": None, "source": f"{_magic_name}"}
            except Exception:
                pass

        # filetype fallback
        if _filetype is not None:
            kind = _filetype.guess(buf)
            if kind:
                return {"mime": kind.mime, "description": kind.extension, "source": "filetype-py"}

        return {"mime": None, "description": None, "source": "unknown"}


# convenience funcs
_default = CrossMagic()

def detect_file(path: str) -> dict:
    return _default.from_file(path)

def detect_bytes(b: bytes) -> dict:
    return _default.from_buffer(b)


if __name__ == "__main__":
    import argparse, json
    p = argparse.ArgumentParser()
    p.add_argument("path", help="file path to detect")
    args = p.parse_args()
    out = detect_file(args.path)
    print(json.dumps(out, ensure_ascii=False, indent=2))


