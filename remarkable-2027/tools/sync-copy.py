from pathlib import Path
import json
root = Path(__file__).resolve().parents[1]
c = json.loads((root / "dist/content/copy.json").read_text())
(root / "dist/content/copy.js").write_text("/* Generated from copy.json. Run python3 tools/sync-copy.py after copy changes. */\nwindow.REMARKABLE_COPY = " + json.dumps(c, ensure_ascii=False, indent=2) + ";\n")
print("Offline content synchronized.")
