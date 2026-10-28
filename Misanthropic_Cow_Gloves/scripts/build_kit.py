"""Build per-step ZIP packages and the guide page from kit_content."""
import sys, os, shutil, zipfile, html, json
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kit_content as K

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
    NS = len(K.STEPS)
    lines = [f"STEP {n} OF {NS} — {st['title'].upper()}", "=" * 60, "", st["goal"], "", "WHERE: " + st["where"], ""]
    if st["attach"]:
        lines.append("ATTACH THESE, IN THIS ORDER:")
    for i, (fn, desc) in enumerate(st["attach"], 1):
        if is_users(fn):
            lines.append(f"  {i}. {fn}  <- YOUR approved image from an earlier step (not in this folder)")
        else:
            out = f"{i}_{fn}"
            shutil.copy(os.path.join(REFS, fn), os.path.join(folder, out))
            lines.append(f"  {i}. {out}  ({desc})")
    head = "THEN PASTE THIS PROMPT (everything between the lines):" if st["attach"] else "DO THIS:"
    lines += ["", head, "-" * 60, K.fill(st["prompt"]), "-" * 60, "",
              "BEFORE YOU APPROVE IT, CHECK:", wrap_list(st["check"], "  [ ] "), ""]
    if st["save"]:
        lines += ["SAVE THE APPROVED IMAGE AS: " + st["save"], ""]
    lines += ["NEXT: " + st["after"], "",
              "Something wrong? Open the FIX_UP_PROMPTS package and paste the matching fix."]
    with open(os.path.join(folder, "PROMPT.txt"), "w") as f:
        f.write("\n".join(lines) + "\n")
    if n == 1:
        readme = [K.KIT_TITLE, "=" * 60, "",
                  K.KIT_GOAL,
                  f"Work through STEP_1 to STEP_{NS} in order. Each package has a PROMPT.txt and the images to attach, numbered in attach order.",
                  "Works in ChatGPT image generation or Gemini. Use the same chat throughout unless told otherwise.", "",
                  "GROUND RULES:", wrap_list(K.TIPS, "  - "), "",
                  K.KEY_FILE + " is your checklist for every result."]
        with open(os.path.join(folder, "README_START_HERE.txt"), "w") as f:
            f.write("\n".join(readme) + "\n")
    if n == NS:
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

# ---------- web thumbnails ----------
def thumb(fn, size=520):
    src = os.path.join(REFS, fn)
    im = Image.open(src).convert("RGB")
    im.thumbnail((size, size), Image.LANCZOS)
    out = fn.rsplit(".", 1)[0] + ".jpg"
    im.save(os.path.join(WEB, "img", out), quality=84, optimize=True)
    return "img/" + out

allref = set(fn for st in K.STEPS for fn, _ in st["attach"] if not is_users(fn)) | set(fn for fn, _ in K.FIX_ATTACH)
thumbs = {fn: thumb(fn) for fn in sorted(allref)}
key_im = Image.open(os.path.join(REFS, K.KEY_FILE)).convert("RGB")
key_im.thumbnail((1600, 1600), Image.LANCZOS)
key_im.save(os.path.join(WEB, "img", "design_key_large.jpg"), quality=86, optimize=True)

json.dump({"zips": zip_paths, "thumbs": thumbs}, open(os.path.join(OUT, "manifest.json"), "w"), indent=1)
print("\n".join(zip_paths))
print(len(thumbs), "thumbs")
