"""Entry for make.fun news-image-01: write the picture of 13 November 2026's news.

The image is drawn ahead of time by art/draw.py and committed as entry.png;
at run time (no network, standard library only) this copies its bytes to /output.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = "/output"


def main():
    with open(os.path.join(HERE, "entry.png"), "rb") as f:
        data = f.read()
    if not data.startswith(b"\x89PNG\r\n\x1a\n") or len(data) > 1048576:
        sys.exit("entry.png is not a PNG within 1 MiB")
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "entry.png"), "wb") as f:
        f.write(data)


if __name__ == "__main__":
    main()
