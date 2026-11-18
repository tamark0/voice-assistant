"""Copy one WLASL clip per word from the Kaggle zip into assets/signs/.
Usage:
  uv run python scripts/build_assets.py            # build from starter_glosses.txt
  uv run python scripts/build_assets.py search th  # list glosses containing "th"
"""
import json
import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ZIP = ROOT / "data" / "wlasl-processed.zip"
OUT = ROOT / "assets" / "signs"
WORDS = ROOT / "data" / "starter_glosses.txt"
OUT.mkdir(parents=True, exist_ok=True)

with zipfile.ZipFile(ZIP) as z:
    names = z.namelist()
    meta_name = next(n for n in names if n.endswith("WLASL_v0.3.json"))
    videos = {Path(n).stem: n for n in names if n.lower().endswith(".mp4")}
    meta = json.loads(z.read(meta_name))
    by_gloss = {e["gloss"].lower(): e["instances"] for e in meta}

    if len(sys.argv) > 2 and sys.argv[1] == "search":
        q = sys.argv[2].lower()
        print([g for g in sorted(by_gloss) if q in g])
        sys.exit()

    missing = []
    for word in WORDS.read_text().splitlines():
        word = word.strip().lower()
        if not word:
            continue
        # first instance of this word whose video is actually in the zip
        vid = next((i["video_id"] for i in by_gloss.get(word, [])
                    if i["video_id"] in videos), None)
        if vid is None:
            missing.append(word)
            print(f"MISSING  {word}")
            continue
        dst = OUT / f"{word.upper().replace(' ', '_')}.mp4"
        with z.open(videos[vid]) as src, open(dst, "wb") as f:
            shutil.copyfileobj(src, f)
        print(f"ok       {word} -> {dst.name}")

print("\nMissing:", missing or "none")