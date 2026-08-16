#!/usr/bin/env python3
"""Guest-facing maps: simplified, filled-in redraw of the three DX event
maps. Rooms are solid colour blocks (geometry taken from the registered
event maps), staff space is a flat grey mass, and only guest-relevant
wayfinding is shown. One 3-page PDF, brand style."""
import pymupdf as fitz

SP = "/tmp/claude-0/-home-user-main/8646fd97-4ad3-5951-b0bc-d4bea048f46f/scratchpad"
REGOTF = "/home/user/main/Karbon-Regular.otf"
SBOTF = "/home/user/main/Karbon-Semibold.otf"
freg, fsb = fitz.Font(fontfile=REGOTF), fitz.Font(fontfile=SBOTF)
import json
KREG = json.load(open(f"{SP}/registration.json"))

W, H = 1728, 1152
AREA = fitz.Rect(60, 195, 1005, 1075)

# palette
DARK = (0.08, 0.08, 0.08)
GRAY = (0x5f/255, 0x5c/255, 0x5c/255)
PINK = (0.92, 0.03, 0.54)
BLUE = (0x31/255, 0x3C/255, 0xFF/255)
FIELD = (0.945, 0.937, 0.925)
WALL = (0.38, 0.36, 0.35)
Z_PINK = ((0.985, 0.845, 0.915), (0.93, 0.45, 0.70))
Z_PURP = ((0.905, 0.845, 0.965), (0.63, 0.44, 0.82))
Z_BLUEW = ((0.795, 0.915, 0.955), (0.30, 0.62, 0.72))
Z_GREEN = ((0.915, 0.955, 0.745), (0.62, 0.70, 0.35))
Z_ORNG = ((0.995, 0.905, 0.775), (0.90, 0.62, 0.20))
Z_STAFF = ((0.885, 0.878, 0.870), (0.74, 0.73, 0.72))
T_PURP = (0.54, 0.15, 0.79)
T_BLUE = (0.19, 0.24, 1.0)
T_CYAN = (0.28, 0.75, 0.85)
T_ORNG = (0.97, 0.62, 0.03)
T_PINK = (0.92, 0.03, 0.54)
BOXBG = (248/255, 248/255, 247/255)

def wl(f, s, sz): return f.text_length(s, fontsize=sz)

class Page:
    def __init__(self, doc, lvl, name, sub, srcbox, kreg):
        self.pg = doc.new_page(width=W, height=H)
        self.lvl = lvl
        sb = fitz.Rect(srcbox)
        self.K = min(AREA.width/sb.width, AREA.height/sb.height)
        self.ox = AREA.x0 + (AREA.width - sb.width*self.K)/2 - sb.x0*self.K
        self.oy = AREA.y0 + (AREA.height - sb.height*self.K)/2 - sb.y0*self.K
        self.ftpt = kreg * self.K          # page pt per foot
        self.header(name, sub)

    def T(self, x, y): return (x*self.K + self.ox, y*self.K + self.oy)
    def TR(self, r):
        a, b = self.T(r[0], r[1]); c, d = self.T(r[2], r[3])
        return fitz.Rect(a, b, c, d)

    def txt(self, x, y, s, font, sz, col):
        self.pg.insert_text((x, y), s, fontsize=sz,
                            fontname="KSB" if font is fsb else "KRG",
                            fontfile=SBOTF if font is fsb else REGOTF, color=col)

    def tracked(self, x, y, s, font, sz, col, tr):
        for ch in s:
            self.txt(x, y, ch, font, sz, col)
            x += wl(font, ch, sz) + tr

    def caps(self, cx, y, s, sz, col, halo=True, font=freg):
        tr = 0.16 * sz
        total = wl(font, s, sz) + tr*(len(s)-1)
        if halo:
            for dx, dy in ((-0.9,0),(0.9,0),(0,-0.9),(0,0.9)):
                self.tracked(cx-total/2+dx, y+dy, s, font, sz, (1,1,1), tr)
        self.tracked(cx-total/2, y, s, font, sz, col, tr)

    def header(self, name, sub):
        pg = self.pg
        pg.draw_rect(fitz.Rect(0, 0, W, 140), fill=(0,0,0), color=None)
        n = 80
        for j in range(n):
            c = [PINK[m] + (BLUE[m]-PINK[m])*j/(n-1) for m in range(3)]
            pg.draw_rect(fitz.Rect(W*j/n, 140, W*(j+1)/n + .5, 147), fill=c, color=None)
        self.tracked(186, 55, "VECTOR INSTITUTE AT DESIGN EXCHANGE — GUEST MAP",
                     fsb, 12.5, PINK, 3.2)
        self.txt(184, 100, name, fsb, 39, (1,1,1))
        self.txt(200 + wl(fsb, name, 39), 96, sub, freg, 16.5, (0.85,0.85,0.85))
        r = fitz.Rect(1343, 30, 1443, 124)
        pg.draw_rect(r, fill=PINK, color=None, radius=0.12)
        self.tracked(r.x0 + (r.width-(wl(fsb,"LEVEL",11.2)+4*2.4))/2, 58,
                     "LEVEL", fsb, 11.2, (1,1,1), 2.4)
        nw = wl(fsb, str(self.lvl), 39)
        self.txt(r.x0+(r.width-nw)/2, 105, str(self.lvl), fsb, 39, (1,1,1))

    def plate(self, r):
        rr = self.TR(r)
        self.pg.draw_rect(rr, fill=FIELD, color=WALL, width=2.6, radius=0.012)
        return rr

    def zone(self, r, style, radius=None):
        rr = self.TR(r)
        frac = radius if radius is not None else min(0.5, 5.5/min(rr.width, rr.height))
        self.pg.draw_rect(rr, fill=style[0], color=style[1], width=1.1, radius=frac)
        return rr

    def tile(self, cx, cy, col, glyph, s=33):
        cx, cy = self.T(cx, cy)
        r = fitz.Rect(cx-s/2, cy-s/2, cx+s/2, cy+s/2)
        self.pg.draw_rect(fitz.Rect(r.x0-2.5, r.y0-2.5, r.x1+2.5, r.y1+2.5),
                          fill=(1,1,1), color=None, radius=0.3)
        self.pg.draw_rect(r, fill=col, color=None, radius=0.28)
        g = self.pg.new_shape()
        if glyph == "stairs":
            pts = [(-8,7),(-3,7),(-3,2),(2,2),(2,-3),(7,-3),(7,-8)]
            g.draw_polyline([(cx+a, cy+b) for a, b in pts])
            g.finish(color=(1,1,1), width=2.8, lineJoin=1, lineCap=1, closePath=False)
        elif glyph == "elev":
            g.draw_rect(fitz.Rect(cx-8, cy-10, cx+8, cy+10), radius=0.25)
            g.finish(color=(1,1,1), width=2.0)
            g.draw_polyline([(cx-3.8,cy-2.5),(cx,cy-7),(cx+3.8,cy-2.5),(cx-3.8,cy-2.5)])
            g.finish(fill=(1,1,1), color=None, closePath=True)
            g.draw_polyline([(cx-3.8,cy+2.5),(cx,cy+7),(cx+3.8,cy+2.5),(cx-3.8,cy+2.5)])
            g.finish(fill=(1,1,1), color=None, closePath=True)
        elif glyph == "esc":
            pts = [(-8,8),(-2,8),(6,-6),(8,-6)]
            g.draw_polyline([(cx+a, cy+b) for a, b in pts])
            g.finish(color=(1,1,1), width=2.8, lineCap=1, lineJoin=1, closePath=False)
            g.draw_line((cx-8, cy+3.5), (cx-3.5, cy+3.5))
            g.finish(color=(1,1,1), width=2.0, lineCap=1)
        elif glyph == "coat":
            g.draw_circle((cx, cy-6.5), 2.6)
            g.finish(color=(1,1,1), width=2.0)
            g.draw_polyline([(cx-9,cy+6.5),(cx+9,cy+6.5),(cx,cy-2.2),(cx-9,cy+6.5)])
            g.finish(color=(1,1,1), width=2.0, closePath=True, lineJoin=1)
        elif glyph == "door":
            g.draw_line((cx-8, cy), (cx+3, cy))
            g.finish(color=(1,1,1), width=2.6, lineCap=1)
            g.draw_polyline([(cx-1,cy-4.5),(cx+3.5,cy),(cx-1,cy+4.5)])
            g.finish(color=(1,1,1), width=2.6, lineJoin=1, lineCap=1, closePath=False)
            g.draw_line((cx+7.5, cy-8), (cx+7.5, cy+8))
            g.finish(color=(1,1,1), width=2.6, lineCap=1)
        g.commit()
        if glyph == "wc":
            t = "WC"
            self.txt(cx - wl(fsb, t, 13)/2, cy + 13*0.66/2, t, fsb, 13, (1,1,1))
        if glyph == "info":
            self.txt(cx - wl(fsb, "i", 19)/2, cy + 19*0.66/2 - 1, "i", fsb, 19, (1,1,1))

    def pill(self, cx, y0, s, sz=11.2):
        w = wl(fsb, s, sz) + 24
        cx, y0 = self.T(cx, y0)
        r = fitz.Rect(cx-w/2, y0, cx+w/2, y0+19.5)
        self.pg.draw_rect(r, fill=(1,1,1), color=(0.82,0.81,0.80), width=0.9, radius=0.5)
        self.txt(r.x0+12, r.y0+(19.5+sz*0.66)/2-0.5, s, fsb, sz, (0.08,0.08,0.08))

    def note(self, cx, y0, s, sz=10.5):
        w = wl(freg, s, sz) + 22
        cx, y0 = self.T(cx, y0)
        r = fitz.Rect(cx-w/2, y0, cx+w/2, y0+18)
        self.pg.draw_rect(r, fill=(1,1,1), color=(0.85,0.84,0.83), width=0.8, radius=0.5)
        self.txt(r.x0+11, r.y0+(18+sz*0.66)/2-0.5, s, freg, sz, GRAY)

    def route(self, pts):
        g = self.pg.new_shape()
        g.draw_polyline([self.T(x, y) for x, y in pts])
        g.finish(color=(0.42,0.47,1.0), width=2.2, dashes="[6 5] 0", lineJoin=1, lineCap=1, closePath=False)
        g.commit()

    def sidebar(self, items, around):
        pg = self.pg
        x0, x1 = 1060, 1462
        self.tracked(x0, 218, "ON THIS LEVEL", fsb, 12.0, GRAY, 2.6)
        y = 246
        for col, label, sub in items:
            pg.draw_rect(fitz.Rect(x0, y-11, x0+13, y+2), fill=col,
                         color=None, radius=0.25)
            self.txt(x0+24, y, label, fsb, 12.4, (0.08,0.08,0.08))
            if sub:
                self.txt(x0+24+wl(fsb,label,12.4)+9, y, sub, freg, 10.9, GRAY)
            y += 26
        y0 = y + 22
        h = 62 + len(around)*15.7
        pg.draw_rect(fitz.Rect(x0, y0, x1, y0+h), fill=BOXBG, color=None, radius=8/h)
        pg.draw_rect(fitz.Rect(x0, y0, x0+4, y0+h), fill=PINK, color=None)
        self.tracked(x0+22, y0+30, "GETTING AROUND", fsb, 12.8, PINK, 1.6)
        yy = y0 + 55
        for ln in around:
            self.txt(x0+22, yy, ln, freg, 10.9, (0.08,0.08,0.08))
            yy += 15.7
    def footer(self, name):
        pg = self.pg
        pg.draw_line((46.5, 1096), (1462, 1096), color=(0.88,0.88,0.88), width=0.8)
        self.txt(46.5, 1088, f"Guest map · Level {self.lvl} — {name} · page {self.lvl} of 3",
                 freg, 11.2, GRAY)
        fr = "Design Exchange · 234 Bay Street, Toronto"
        self.txt(1462 - wl(freg, fr, 11.2), 1088, fr, freg, 11.2, GRAY)
        # scale bar + north arrow
        bx, by = 60, 1112
        ft20 = 20 * self.ftpt
        for j in range(4):
            f = (0,0,0) if j % 2 == 0 else (1,1,1)
            pg.draw_rect(fitz.Rect(bx+j*ft20/4, by, bx+(j+1)*ft20/4, by+7),
                         fill=f, color=(0,0,0), width=0.7)
        self.txt(bx-3, by-6, "0", freg, 9.8, GRAY)
        self.txt(bx+ft20-8, by-6, "20 ft", freg, 9.8, GRAY)
        ax = bx + ft20 + 55
        g = pg.new_shape()
        g.draw_polyline([(ax,by+8),(ax+6,by-10),(ax+12,by+8),(ax+6,by+4),(ax,by+8)])
        g.finish(fill=(0.08,)*3, color=None, closePath=True)
        g.commit()
        self.txt(ax+18, by+6, "N", fsb, 14.2, DARK)
        self.txt(ax+44, by+6, "North is up · staff-only areas shown in grey",
                 freg, 11.2, GRAY)

doc = fitz.open()

# ============================================================ LEVEL 1
p = Page(doc, 1, "Lobby", "Arrive, check in, drop your coat",
         (108, 181, 801, 753), KREG["1"]["k_event_pt_per_ft"])
p.plate((108, 181, 801, 753))
p.zone((190, 187, 727, 610), Z_PINK)                       # lobby
p.zone((150, 245, 310, 412), Z_STAFF)                      # staff offices
p.zone((384, 189, 498, 287), Z_GREEN)                      # Teknion lounge
p.zone((589, 184, 655, 228), Z_BLUEW)                      # universal washroom
p.zone((658, 318, 801, 396), Z_ORNG)                       # coat check
p.zone((378, 593, 558, 683), Z_BLUEW)                      # washrooms
p.zone((251, 602, 317, 730), Z_PURP)                       # escalators
p.zone((638, 621, 801, 724), Z_PURP)                       # grand staircase
# labels
cx, cy = 458, 470
x, y = p.T(cx, cy)
p.caps(x, y, "LOBBY", 26, DARK)
p.txt(x - wl(freg, "Arrival & check-in", 13.5)/2, y+22, "Arrival & check-in", freg, 13.5, GRAY)
x, y = p.T(441, 243); p.caps(x, y, "TEKNION LOUNGE", 10.5, (0.42,0.48,0.16))
x, y = p.T(230, 332); p.caps(x, y, "STAFF ONLY", 9.6, GRAY)
x, y = p.T(712, 382); p.caps(x, y, "COAT CHECK", 10.5, (0.62,0.40,0.08))
x, y = p.T(468, 642); p.caps(x, y, "WASHROOMS", 10.5, (0.16,0.42,0.52))
# route: entrance -> check-in
p.route([(792, 432), (548, 432), (548, 545)])
# icons + pills
p.tile(520, 566, T_ORNG, "info"); p.pill(520, 522, "Check-in")
p.tile(468, 613, T_CYAN, "wc")
p.tile(622, 206, T_CYAN, "wc"); p.pill(622, 232, "All-gender washroom")
p.tile(770, 338, T_ORNG, "coat")
p.tile(284, 655, T_PURP, "esc"); p.pill(284, 728, "Escalators — down to the PATH")
p.tile(719, 672, T_PURP, "stairs"); p.pill(719, 730, "Grand Staircase — up to Trading Floor")
p.tile(585, 704, T_BLUE, "elev"); p.pill(585, 728, "Elevator — all levels")
p.tile(770, 206, T_BLUE, "elev"); p.pill(718, 258, "Elevator — Levels 1 & 2")
p.tile(801, 430, T_PINK, "door"); p.pill(750, 452, "Entrance — Bay Street")
p.tile(801, 680, T_PINK, "door")
p.sidebar([(Z_PINK[0], "Lobby", "check-in & security"),
           ((0.97,0.62,0.03), "Coat check", "east side"),
           (Z_BLUEW[0], "Washrooms", "incl. all-gender"),
           (Z_GREEN[0], "Teknion Lounge", None),
           (Z_PURP[0], "Grand Staircase", "up to Level 2"),
           (Z_PURP[0], "Escalators", "down to the PATH")],
          ["Come in from Bay Street and check in at the desk in",
           "the middle of the Lobby. Coat check is on the east",
           "side. When you're ready, take the Grand Staircase",
           "or an elevator up to the Trading Floor."])
p.footer("Lobby")

# ============================================================ LEVEL 2
p = Page(doc, 2, "Trading Floor", "The immersive theatre — 350 seats",
         (117, 178, 793, 753), KREG["2"]["k_event_pt_per_ft"])
p.plate((117, 178, 793, 753))
p.zone((162, 289, 770, 617), Z_PINK)                       # the hall
# seating: two banks of rows
for x0, x1 in ((205, 385), (415, 585)):
    yy = 372
    while yy < 592:
        p.pg.draw_rect(p.TR((x0, yy, x1, yy+5.2)), fill=(0.80,0.62,0.72),
                       color=None, radius=0.5)
        yy += 14.5
# bridge band (dashed, above)
bb = p.TR((648, 289, 701, 617))
g = p.pg.new_shape(); g.draw_rect(bb)
g.finish(color=(0.55,0.53,0.52), width=1.0, dashes="[5 4] 0"); g.commit()
bx, by = p.T(680, 490)
p.pg.insert_text((bx, by), "BRIDGE ABOVE", fontsize=9.4, fontname="KRG",
                 fontfile=REGOTF, color=GRAY, rotate=90)
p.zone((601, 448, 637, 539), Z_PURP)                       # mid-hall stair
p.zone((686, 628, 786, 723), Z_PURP)                       # grand staircase
p.zone((370, 622, 545, 690), Z_STAFF)                      # kitchen strip
x, y = p.T(457, 660); p.caps(x, y, "STAFF ONLY", 9.6, GRAY)
x, y = p.T(400, 326)
p.caps(x, y, "TRADING FLOOR", 26, DARK)
p.txt(x - wl(freg, "Immersive theatre · 350 seats", 13.5)/2, y+22,
      "Immersive theatre · 350 seats", freg, 13.5, GRAY)
p.tile(619, 478, T_PURP, "stairs"); p.pill(619, 549, "Up to the Gallery & bridge")
p.tile(735, 668, T_PURP, "stairs"); p.pill(700, 730, "Grand Staircase — down to Lobby")
p.tile(522, 697, T_BLUE, "elev"); p.pill(560, 725, "Elevator — all levels")
p.tile(661, 200, T_BLUE, "elev"); p.pill(627, 226, "Elevator — Levels 1 & 2")
p.note(300, 700, "No washrooms on this level — use the Lobby or the Gallery")
p.sidebar([(Z_PINK[0], "Trading Floor", "350 seats, theatre style"),
           (Z_PURP[0], "Stairs to the Gallery", "mid-hall, also to the bridge"),
           (Z_PURP[0], "Grand Staircase", "down to the Lobby"),
           ((0.75,0.75,0.75), "Bridge", "crosses above the hall")],
          ["The show happens here. The Grand Staircase in the",
           "south-east corner returns to the Lobby; the stair in",
           "the middle of the hall goes up to the Gallery and the",
           "bridge. No washrooms on this level — the nearest",
           "are one level down (Lobby) or up (Gallery)."])
p.footer("Trading Floor")

# ============================================================ LEVEL 3
p = Page(doc, 3, "Gallery", "Exhibition hall, vendors and washrooms",
         (74.8, 190.8, 838.6, 740.4), KREG["3"]["k_event_pt_per_ft"])
p.plate((74.8, 190.8, 838.6, 740.4))
p.zone((74.8, 275.7, 838.6, 740.4), Z_PINK)                # hall (full width)
# carve corridors + core back to field
p.pg.draw_rect(p.TR((233.4, 275.7, 660.5, 564)), fill=FIELD, color=None)
p.zone((80.4, 295.2, 233.4, 556.7), Z_STAFF)               # boardroom (private)
p.zone((296, 214.5, 612, 564), Z_STAFF)                    # service core
p.zone((196, 193.6, 520, 272), Z_STAFF)                    # north staff band
p.zone((296, 357.8, 612, 427.3), Z_BLUEW)                  # washrooms
p.zone((749.6, 193.6, 835.8, 252), Z_PURP)                 # NE stair down
# vendor tables
for i in range(8):
    p.pg.draw_rect(p.TR((745, 300+i*33, 787, 318+i*33)), fill=(0.72,0.70,0.69),
                   color=None, radius=0.2)
for i in range(7):
    p.pg.draw_rect(p.TR((300+i*58, 630, 342+i*58, 648)), fill=(0.72,0.70,0.69),
                   color=None, radius=0.2)
for i in range(3):
    p.pg.draw_rect(p.TR((92, 585+i*44, 134, 603+i*44)), fill=(0.72,0.70,0.69),
                   color=None, radius=0.2)
x, y = p.T(156.9, 425); p.caps(x, y, "GALLERY BOARDROOM", 10.5, GRAY)
x, y = p.T(156.9, 442); p.caps(x, y, "PRIVATE", 8.6, GRAY)
x, y = p.T(454, 505); p.caps(x, y, "STAFF ONLY", 9.6, GRAY)
x, y = p.T(358, 246); p.caps(x, y, "STAFF ONLY", 9.6, GRAY)
x, y = p.T(378, 421); p.caps(x, y, "MEN'S", 8.6, (0.16,0.42,0.52))
x, y = p.T(538, 421); p.caps(x, y, "WOMEN'S", 8.6, (0.16,0.42,0.52))
x, y = p.T(450, 668)
p.caps(x, y, "EXHIBITION HALL", 26, DARK)
p.txt(x - wl(freg, "The Gallery · vendor tables", 13.5)/2, y+22,
      "The Gallery · vendor tables", freg, 13.5, GRAY)
xx, yy = p.T(766, 460)
p.pg.insert_text((xx-5, yy+60), "VENDOR TABLES", fontsize=9.6, fontname="KRG",
                 fontfile=REGOTF, color=GRAY, rotate=90)
p.tile(378, 392, T_CYAN, "wc")
p.tile(538, 392, T_CYAN, "wc")
p.pill(454, 434, "Washrooms — via either corridor")
p.tile(792, 222, T_PURP, "stairs"); p.pill(738, 260, "Stairs — down to Trading Floor")
p.tile(636, 232, T_BLUE, "elev"); p.pill(636, 203, "Elevator — all levels")
p.sidebar([(Z_PINK[0], "Exhibition Hall", "wraps the centre of the floor"),
           ((0.72,0.70,0.69), "Vendor tables", "east & south"),
           (Z_BLUEW[0], "Washrooms", "centre of the floor"),
           (Z_PURP[0], "Stairs", "down to the Trading Floor"),
           (Z_STAFF[0], "Boardroom", "private event space")],
          ["The hall wraps around the middle of the floor —",
           "follow it round for the vendor tables. Washrooms",
           "are in the centre, reached from the corridor on",
           "either side. To get back down, use the stair in the",
           "north-east corner or the elevator."])
p.footer("Gallery")

doc.set_metadata({"title": "DX Guest Maps — Levels 1–3",
                  "author": "Vector Institute event team"})
doc.save(f"{SP}/DX_Guest_Maps.pdf", garbage=3, deflate=True)
print("saved DX_Guest_Maps.pdf")
