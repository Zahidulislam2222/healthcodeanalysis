"""Loopback-only preview server with real 404s and no directory listings."""

from __future__ import annotations

import re
from functools import partial
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import TYPE_CHECKING, AnyStr, BinaryIO

if TYPE_CHECKING:
    from os import PathLike

    from _typeshed import SupportsRead, SupportsWrite

from frontend_settings import FrontendSettings


class PreviewHandler(SimpleHTTPRequestHandler):
    def send_head(self) -> BinaryIO | None:
        self.range_remaining: int | None = None
        requested = self.headers.get("Range", "")
        path = Path(self.translate_path(self.path))
        # Unsupported/multipart/conditional ranges use the normal full response.
        match = re.fullmatch(r"bytes=(\d*)-(\d*)", requested)
        if self.command != "GET" or not match or self.headers.get("If-Range") or not path.is_file():
            return super().send_head()
        if not path.resolve().is_relative_to(Path(self.directory).resolve()):
            self.send_error(HTTPStatus.NOT_FOUND)
            return None
        stream = path.open("rb")
        size = path.stat().st_size
        first, last = match.groups()
        start = int(first) if first else max(0, size - int(last or "0"))
        end = min(int(last), size - 1) if first and last else size - 1
        if start > end or start >= size or (not first and not int(last or "0")):
            stream.close()
            self.send_response(HTTPStatus.REQUESTED_RANGE_NOT_SATISFIABLE)
            self.send_header("Content-Range", f"bytes */{size}")
            self.send_header("Content-Length", "0")
            self.end_headers()
            return None
        stream.seek(start)
        self.range_remaining = end - start + 1
        self.send_response(HTTPStatus.PARTIAL_CONTENT)
        self.send_header("Content-Type", self.guess_type(str(path)))
        self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.send_header("Content-Length", str(self.range_remaining))
        self.end_headers()
        return stream

    def copyfile(self, source: SupportsRead[AnyStr], outputfile: SupportsWrite[AnyStr]) -> None:
        if self.range_remaining is None:
            super().copyfile(source, outputfile)
            return
        while self.range_remaining:
            chunk = source.read(min(self.range_remaining, 64 * 1024))
            if not chunk:
                break
            outputfile.write(chunk)
            self.range_remaining -= len(chunk)

    def list_directory(self, path: str | PathLike[str]) -> None:
        self.send_error(HTTPStatus.NOT_FOUND)

    def send_error(self, code: int, message: str | None = None, explain: str | None = None) -> None:
        page = Path(self.directory) / "404.html"
        if code == HTTPStatus.NOT_FOUND and page.is_file():
            data = page.read_bytes()
            self.send_response(code)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            if self.command != "HEAD":
                self.wfile.write(data)
        else:
            super().send_error(code, message, explain)

    def end_headers(self) -> None:
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "strict-origin-when-cross-origin")
        self.send_header("Cache-Control", "no-cache")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; img-src 'self' blob: data:; "
            "script-src 'self'; style-src 'self' 'unsafe-inline'; "
            "object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'none'",
        )
        super().end_headers()


if __name__ == "__main__":
    settings = FrontendSettings.load()
    handler = partial(PreviewHandler, directory=str(settings.output))
    with ThreadingHTTPServer((settings.preview_host, settings.preview_port), handler) as server:
        print(f"HealthCode preview: http://{settings.preview_host}:{settings.preview_port}/", flush=True)
        server.serve_forever()
