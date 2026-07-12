from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "healthcodeanalysis-com-20260408-134414-6x2yr0zixkut.wpress"
TARGET = Path("/tmp/hca-wp-content/wp-content")
HEADER_SIZE = 4377


def read_field(header: bytes, start: int, length: int, encoding: str = "utf-8") -> str:
    return header[start : start + length].split(b"\0", 1)[0].decode(encoding, "replace")


def main() -> None:
    offset = 0
    total = ARCHIVE.stat().st_size
    restored = 0
    skipped = 0

    TARGET.mkdir(parents=True, exist_ok=True)

    with ARCHIVE.open("rb") as src:
        while offset < total:
            src.seek(offset)
            header = src.read(HEADER_SIZE)
            if len(header) < HEADER_SIZE:
                break

            name = read_field(header, 0, 255)
            size_raw = read_field(header, 255, 14, "ascii")
            relative_dir = read_field(header, 281, 255)

            if not name or not size_raw:
                break

            size = int(size_raw)
            data_offset = offset + HEADER_SIZE
            offset = data_offset + size

            if not (
                relative_dir == "plugins"
                or relative_dir == "themes"
                or relative_dir == "uploads"
                or relative_dir.startswith(("plugins/", "themes/", "uploads/"))
            ):
                skipped += 1
                continue

            target = TARGET / relative_dir / name
            target.parent.mkdir(parents=True, exist_ok=True)
            src.seek(data_offset)
            target.write_bytes(src.read(size))
            restored += 1

    print(f"Restored {restored} wp-content files to {TARGET}")
    print(f"Skipped {skipped} non wp-content files")


if __name__ == "__main__":
    main()
