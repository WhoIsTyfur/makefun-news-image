# One picture of Friday 13 November 2026

Entry for the make.fun bounty [news-image-01](https://make.fun/bounty/news-image-01):
"Sum up 13 November's world news in one image."

## What it does

`main.py` (Python 3.13, standard library only) copies the committed `entry.png`, a 1024x1024 PNG
under 1 MiB, to `/output/entry.png`. The program runs with no network and writes the same bytes every time.

The picture is drawn ahead of time by `art/draw.py` (Pillow), as a front page: the date as the
masthead, one lead story drawn large and smaller labeled panels for the day's other major stories
across regions and fields, each with a drawn scene and a short factual label. Every story is
sourced to 13 November 2026 in [`research/sources-2026-11-13.md`](research/sources-2026-11-13.md),
with at least two independent outlets each.

## How it is scored

A gate checks that the file is a whole PNG or JPEG within 1 MiB and 1024x1024. Valid entries are
then judged in pairs by an AI picture editor, both orders per pair, on: (1) the specific news of
that day, (2) the most consequential stories across regions and fields, (3) reads at a glance with
nothing false, (4) faithful without hype, (5) clean craft legible at about 300 px. Entries rank by
win rate.

## Run it locally

```
python art/draw.py            # redraw entry.png (needs Pillow; Windows fonts)
mkdir -p /output && python main.py
```
