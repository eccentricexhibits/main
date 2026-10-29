"""Build per-step ZIP packages from kit_content_cow (adapted from the slipper build_kit.py).
python3 -I build_kit_cow.py <refs_dir> <out_dir>"""
import sys, os, shutil, zipfile, html, json
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kit_content_cow as K

REFS, OUT = sys.argv[1], sys.argv[2]
KIT = os.path.join(OUT, "kit")
WEB = os.path.join(OUT, "web")
shutil.rmtree(KIT, ignore_errors=True); shutil.rmtree(WEB, ignore_errors=True)
os.makedirs(KIT); os.makedirs(os.path.join(WEB, "img"))

def is_users(name):
    return "approved" in name

def wrap_list(items, bullet="- "):
    return "\n".join(bullet + i for i in items)

# ---------- per-step packages ----------
zips = []
for n, st in enumerate(K.STEPS, 1):
    folder = os.path.join(KIT, st["zip"])
    os.makedirs(folder)
    lines = [f"STEP {n} OF {len(K.STEPS)} — {st['title'].upper()}", "=" * 60, "", st["goal"], "", "WHERE: " + st["where"], "",
             "ATTACH THESE, IN THIS ORDER:"]
    for i, (fn, desc) in enumerate(st["attach"], 1):
        if is_users(fn):
            lines.append(f"  {i}. {fn}  <- YOUR approved image from an earlier step (not in this folder)")
        else:
            out = f"{i}_{fn}"
            shutil.copy(os.path.join(REFS, fn), os.path.join(folder, out))
            lines.append(f"  {i}. {out}  ({desc})")
    lines += ["", "THEN PASTE THIS PROMPT (everything between the lines):", "-" * 60, K.fill(st["prompt"]), "-" * 60, "",
              "BEFORE YOU APPROVE IT, CHECK:", wrap_list(st["check"], "  [ ] "), ""]
    if st["save"]:
        lines += ["SAVE THE APPROVED IMAGE AS: " + st["save"], ""]
    lines += ["NEXT: " + st["after"], "",
              "Something wrong? Open the FIX_UP_PROMPTS package and paste the matching fix."]
    with open(os.path.join(folder, "PROMPT.txt"), "w") as f:
        f.write("\n".join(lines) + "\n")
    if n == 1:
        readme = [K.TITLE, "=" * 60, "",
                  K.GOAL,
                  "Work through STEP_1 to STEP_5 in order. Each package has a PROMPT.txt and the images to attach, numbered in attach order.",
                  "Works in ChatGPT image generation. Use the same chat throughout unless told otherwise.", "",
                  "GROUND RULES:", wrap_list(K.TIPS, "  - "), "",
                  "DESIGN_KEY_check_every_view_against_this.png is your checklist for every result."]
        with open(os.path.join(folder, "README_START_HERE.txt"), "w") as f:
            f.write("\n".join(readme) + "\n")
    if n == len(K.STEPS):
        t = ["UPLOADING TO TRIPO (multiview)", "=" * 60, ""]
        t += [f"  {slot:<6} <- {fn}" for slot, fn in K.TRIPO]
        t += ["", wrap_list(K.TRIPO_NOTES, "  - ")]
        with open(os.path.join(folder, "TRIPO_UPLOAD.txt"), "w") as f:
            f.write("\n".join(t) + "\n")
    zips.append((folder, st["zip"]))

# fix-up package
folder = os.path.join(KIT, "FIX_UP_PROMPTS")
os.makedirs(folder)
lines = ["FIX-UP PROMPTS", "=" * 60, "",
         "Paste the matching fix in the same chat. Attach the detail image noted beside the fix if the model needs reminding.",
         "In ChatGPT, brush over just the wrong area with the Select tool first, so only that part is redrawn.", ""]
for i, (fn, desc) in enumerate(K.FIX_ATTACH, 1):
    out = fn
    shutil.copy(os.path.join(REFS, fn), os.path.join(folder, out))
for code, when, text in K.FIXES:
    lines += [f"{code} — {when}", "-" * 60, text, ""]
lines += ["Detail images in this folder:"] + [f"  - {fn}  ({desc})" for fn, desc in K.FIX_ATTACH]
lines += ["", "If two fixes in a row make it worse: start a new chat, run Step 1 again, attach your approved images, continue."]
with open(os.path.join(folder, "FIX_PROMPTS.txt"), "w") as f:
    f.write("\n".join(lines) + "\n")
zips.append((folder, "FIX_UP_PROMPTS"))

zip_paths = []
for folder, name in zips:
    zp = os.path.join(KIT, name + ".zip")
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
        for fn in sorted(os.listdir(folder)):
            z.write(os.path.join(folder, fn), arcname=f"{name}/{fn}")
    zip_paths.append(zp)

print("\n".join(zip_paths))
