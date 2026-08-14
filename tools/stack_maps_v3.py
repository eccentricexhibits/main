#!/usr/bin/env python3
"""Compose the 3-page stacked-plan PDF: every page shares one world frame
(feet, north up, origin at the big passenger-elevator shaft), so flipping
pages shows true vertical relationships."""
import pymupdf as fitz, json

SP = "/tmp/claude-0/-home-user-main/8646fd97-4ad3-5951-b0bc-d4bea048f46f/scratchpad"
REGF = json.load(open(f"{SP}/registration.json"))
EVENT = {1: f"{SP}/Event_Map_Level_1_Lobby_v3.pdf",
         2: f"{SP}/Event_Map_Level_2_Trading_Floor_v3.pdf",
         3: f"{SP}/Event_Map_Level_3_Gallery_v3.pdf"}
NAMES = {1: ("Lobby", "Arrival, check-in and coat check"),
         2: ("Trading Floor", "The immersive projection theatre"),
         3: ("Gallery", "Exhibition hall and boardroom — sits mostly over 222 Bay")}
REG = "/home/user/main/Karbon-Regular.otf"
SB = "/home/user/main/Karbon-Semibold.otf"
freg, fsb = fitz.Font(fontfile=REG), fitz.Font(fontfile=SB)

DARK = (0x14/255,)*3
GRAY = (0x5f/255, 0x5c/255, 0x5c/255)
LGRAY = (0.72, 0.71, 0.71)
PINK = (0xEB/255, 0x08/255, 0x8A/255)
BLUE = (0x31/255, 0x3C/255, 0xFF/255)
BOXBG = (248/255, 248/255, 247/255)
W, H = 1728, 1152

def wl(f, s, sz): return f.text_length(s, fontsize=sz)

# ---------- per-floor clip + world rect ----------
docs, clips, world = {}, {}, {}
for lvl in (1, 2, 3):
    d = fitz.open(EVENT[lvl]); docs[lvl] = d
    p = d[0]
    lab = p.search_for("20 ft")[0]
    ylim = lab.y0 - 14
    bb = None
    for dr in p.get_drawings():
        r = dr["rect"]
        if r.y0 > 160 and r.x0 < 885 and r.width < 900 and r.y1 < ylim:
            bb = r if bb is None else bb | r
    clips[lvl] = bb
    i = REGF[str(lvl)]
    k, (bx, by) = i["k_event_pt_per_ft"], i["bigx_event"]
    world[lvl] = fitz.Rect((bb.x0-bx)/k, (bb.y0-by)/k, (bb.x1-bx)/k, (bb.y1-by)/k)
    pw, ph = p.rect.width, p.rect.height
    for band in [(0,0,bb.x0,ph), (bb.x1,0,pw,ph), (0,0,pw,bb.y0), (0,bb.y1,pw,ph)]:
        p.add_redact_annot(fitz.Rect(band))
    p.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE,
                       graphics=fitz.PDF_REDACT_LINE_ART_NONE)
    print(f"L{lvl} clip={bb}  world_ft={world[lvl]}")

U = fitz.Rect(min(w.x0 for w in world.values()), min(w.y0 for w in world.values()),
              max(w.x1 for w in world.values()), max(w.y1 for w in world.values()))
AREA = fitz.Rect(70, 200, 1010, 1070)
K = min(AREA.width/U.width, AREA.height/U.height)
ox = AREA.x0 + (AREA.width - U.width*K)/2 - U.x0*K
oy = AREA.y0 + (AREA.height - U.height*K)/2 - U.y0*K
def out(wx, wy): return (wx*K + ox, wy*K + oy)
print(f"world union {U.width:.0f} x {U.height:.0f} ft; K={K:.3f} pt/ft")

def text(pg, x, y, s, font, sz, color, ffile=None):
    pg.insert_text((x, y), s, fontsize=sz,
                   fontname="KSB" if font is fsb else "KRG",
                   fontfile=SB if font is fsb else REG, color=color)

def tracked(pg, x, y, s, font, sz, color, track):
    for ch in s:
        text(pg, x, y, ch, font, sz, color)
        x += wl(font, ch, sz) + track

outdoc = fitz.open()
for lvl in (1, 2, 3):
    pg = outdoc.new_page(width=W, height=H)
    # header
    pg.draw_rect(fitz.Rect(0, 0, W, 140), fill=(0, 0, 0), color=None)
    n = 80
    for j in range(n):
        c = [PINK[m] + (BLUE[m]-PINK[m])*j/(n-1) for m in range(3)]
        pg.draw_rect(fitz.Rect(W*j/n, 140, W*(j+1)/n + 0.5, 147), fill=c, color=None)
    tracked(pg, 186, 55, "VECTOR INSTITUTE AT DESIGN EXCHANGE — STACKED PLANS",
            fsb, 12.5, PINK, 3.2)
    name, sub = NAMES[lvl]
    text(pg, 184, 100, name, fsb, 39, (1, 1, 1))
    text(pg, 200 + wl(fsb, name, 39), 96, sub, freg, 16.5, (0.85, 0.85, 0.85))
    r = fitz.Rect(1343, 30, 1443, 124)
    pg.draw_rect(r, fill=PINK, color=None, radius=0.12)
    tracked(pg, r.x0 + (r.width - (wl(fsb,"LEVEL",11.2)+4*2.4))/2, 58,
            "LEVEL", fsb, 11.2, (1,1,1), 2.4)
    nw = wl(fsb, str(lvl), 39)
    text(pg, r.x0 + (r.width-nw)/2, 105, str(lvl), fsb, 39, (1, 1, 1))

    # the floor itself, placed in the world frame
    tw = world[lvl]
    tgt = fitz.Rect(*out(tw.x0, tw.y0), *out(tw.x1, tw.y1))
    pg.show_pdf_page(tgt, docs[lvl], 0, clip=clips[lvl])

    # other floors' extents (dashed, on top)
    corners = {1: "tl", 2: "tr", 3: "bl"}
    for o in (1, 2, 3):
        if o == lvl: continue
        wo = world[o]
        ro = fitz.Rect(*out(wo.x0, wo.y0), *out(wo.x1, wo.y1))
        sh = pg.new_shape()
        sh.draw_rect(ro)
        sh.finish(color=LGRAY, width=1.1, dashes="[5 4] 0")
        sh.commit()
        lab = f"LEVEL {o} MAP EXTENT"
        lw = wl(fsb, lab, 8.5) + 2.4*len(lab)
        if corners[o] == "tl": lx, ly = ro.x0 + 8, ro.y0 - 7
        elif corners[o] == "tr": lx, ly = ro.x1 - lw - 8, ro.y0 + 13
        else: lx, ly = ro.x0 + 8, ro.y1 - 7
        tracked(pg, lx, ly, lab, fsb, 8.5, LGRAY, 2.4)

    # elevator-core crosshair at world origin
    cx, cy = out(0, 0)
    sh = pg.new_shape()
    sh.draw_circle((cx, cy), 7)
    sh.finish(color=PINK, width=1.6)
    sh.draw_line((cx-13, cy), (cx+13, cy)); sh.finish(color=PINK, width=1.1)
    sh.draw_line((cx, cy-13), (cx, cy+13)); sh.finish(color=PINK, width=1.1)
    sh.commit()

    # scale bar + north arrow
    bx, by = 70, 1112
    ft20 = 20*K
    for j in range(4):
        f = (0,0,0) if j % 2 == 0 else (1,1,1)
        pg.draw_rect(fitz.Rect(bx+j*ft20/4, by, bx+(j+1)*ft20/4, by+7),
                     fill=f, color=(0,0,0), width=0.7)
    text(pg, bx-3, by-6, "0", freg, 9.8, GRAY)
    text(pg, bx+ft20-8, by-6, "20 ft", freg, 9.8, GRAY)
    ax = bx + ft20 + 60
    sh = pg.new_shape()
    sh.draw_polyline([(ax, by+8), (ax+6, by-10), (ax+12, by+8), (ax+6, by+4), (ax, by+8)])
    sh.finish(fill=(0.08,)*3, color=None, closePath=True)
    sh.commit()
    text(pg, ax+18, by+6, "N", fsb, 14.2, DARK)
    text(pg, ax+44, by+6,
         "Common frame · all three pages share this scale and position · "
         "crosshair = elevator core, identical on every page", freg, 11.2, GRAY)

    # right column boxes
    def box(y0, h, barcolor, title, lines, title_col):
        bx0, bx1 = 1060, 1460
        pg.draw_rect(fitz.Rect(bx0, y0, bx1, y0+h), fill=BOXBG, color=None, radius=8/h)
        pg.draw_rect(fitz.Rect(bx0, y0, bx0+4, y0+h), fill=barcolor, color=None)
        tracked(pg, bx0+22, y0+30, title, fsb, 12.8, title_col, 1.6)
        yy = y0 + 55
        for ln in lines:
            text(pg, bx0+22, yy, ln, freg, 10.9, DARK)
            yy += 15.7
    box(200, 165, PINK, "SAME FRAME, EVERY PAGE", [
        "All three pages are drawn at one scale, in one",
        "position, north up. A feature at the same spot on",
        "two pages is directly above / below itself. The pink",
        "crosshair marks the passenger-elevator shaft —",
        "the core that connects every level.",
    ], PINK)
    box(385, 180, BLUE, "WHY THE FLOORS DON'T STACK", [
        "Levels 1–2 fill the 234 Bay footprint. Level 3 sits",
        "mostly over 222 Bay next door — only the service",
        "core overlaps the floors below. The Trading Floor",
        "hall is double-height, so nothing sits above it;",
        "dashed outlines show the other levels' extents.",
    ], BLUE)
    # level list
    yy = 610
    tracked(pg, 1060, yy, "IN THIS SET", fsb, 11.2, GRAY, 2.4)
    yy += 26
    for o in (1, 2, 3):
        cur = o == lvl
        col = PINK if cur else GRAY
        f = fsb if cur else freg
        text(pg, 1060, yy, f"Level {o} — {NAMES[o][0]}", f, 12.4, col)
        if cur:
            text(pg, 1060 + wl(f, f'Level {o} — {NAMES[o][0]}', 12.4) + 10, yy,
                 "(this page)", freg, 10.9, GRAY)
        yy += 21

    # footer
    pg.draw_line((46.5, 1096), (1460, 1096), color=(0.88, 0.88, 0.88), width=0.8)
    text(pg, 46.5, 1088, f"Stacked plans · common frame · page {lvl} of 3",
         freg, 11.2, GRAY)
    fr = "Design Exchange · 234 Bay Street, Toronto"
    text(pg, 1460 - wl(freg, fr, 11.2), 1088, fr, freg, 11.2, GRAY)

outdoc.set_metadata({"title": "DX Stacked Plans — common frame",
                     "author": "Vector Institute event team"})
outdoc.save(f"{SP}/Event_Maps_Stacked_Common_Frame_v3.pdf", garbage=3, deflate=True)
print("saved Event_Maps_Stacked_Common_Frame_v3.pdf")
