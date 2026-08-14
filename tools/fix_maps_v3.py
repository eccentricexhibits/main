#!/usr/bin/env python3
"""Build v3 event maps from the ORIGINAL sheets: my Level-3-alignment
corrections plus the venue's (Alicia Black) mark-up.

Venue mark-up applied:
  L3  NW stair : "Down to Trading Floor" struck  -> "Staff only" (keeps Fire exit)
  L3  NE stair : "Fire exit" struck              -> "Down to Trading Floor"
  L3  centre   : "Down to 222 Bay only"          -> "No Guest Access"
  L3  boardroom / west corridor                  -> STAFF ONLY zone labels
  L2  SW stair : "Up to the Gallery" struck      -> "Staff only"
  L2  NW stair area / room south of kitchen      -> STAFF ONLY zone labels
  L1  staff offices                              -> STAFF ONLY zone label
"""
import pymupdf as fitz

UP = "/root/.claude/uploads/8646fd97-4ad3-5951-b0bc-d4bea048f46f"
OUT = "/tmp/claude-0/-home-user-main/8646fd97-4ad3-5951-b0bc-d4bea048f46f/scratchpad"
ORIG = {1: f"{UP}/6f7c3232-Claude_Code__Event_Map__Level_1__Lobby.pdf",
        2: f"{UP}/9d36448f-Claude_Code__Event_Map__Level_2__Trading_Floor.pdf",
        3: f"{UP}/3f0fd844-Claude_Code__Event_Map__Level_3__Gallery.pdf"}
DST = {1: f"{OUT}/Event_Map_Level_1_Lobby_v3.pdf",
       2: f"{OUT}/Event_Map_Level_2_Trading_Floor_v3.pdf",
       3: f"{OUT}/Event_Map_Level_3_Gallery_v3.pdf"}
REG, SB = "/home/user/main/Karbon-Regular.otf", "/home/user/main/Karbon-Semibold.otf"
freg, fsb = fitz.Font(fontfile=REG), fitz.Font(fontfile=SB)

DARK = (0x14/255,)*3
GRAY = (0x5f/255, 0x5c/255, 0x5c/255)
WHITE = (1, 1, 1)
BORDER = (0.85, 0.84, 0.84)
PINK = (0xEB/255, 0x08/255, 0x8A/255)
PILL_H, PAD, TSIZE = 18.7, 13.7, 11.2

def wl(f, s, sz): return f.text_length(s, fontsize=sz)
# tracking ratio derived from the sheets' own "STAFF ONLY" zone label
ZTRACK = (65.9 - wl(freg, "STAFF ONLY", 11.2)) / (9 * 11.2)

class Editor:
    def __init__(self, path):
        self.doc = fitz.open(path)
        self.page = self.doc[0]
        self.reds, self.post = [], []

    def redact(self, rect): self.reds.append(fitz.Rect(rect))

    def _txt(self, x, y, s, font, size, color):
        self.page.insert_text((x, y), s, fontsize=size,
                              fontname="KSB" if font is fsb else "KRG",
                              fontfile=SB if font is fsb else REG, color=color)

    def text(self, x, y, s, font, size, color):
        self.post.append(lambda: self._txt(x, y, s, font, size, color))

    def replace(self, bbox, s, font, size, color, pad=1.2, center=False):
        self.redact((bbox[0]-pad, bbox[1]-pad, bbox[2]+pad, bbox[3]+pad))
        base = bbox[3] + freg.descender * size * 0.9
        x = (bbox[0]+bbox[2])/2 - wl(font, s, size)/2 if center else bbox[0]
        self.text(x, base, s, font, size, color)

    def pill(self, x0, y0, s, size=TSIZE, h=PILL_H, w=None):
        w = w if w else wl(fsb, s, size) + 2*PAD
        r = fitz.Rect(x0, y0, x0+w, y0+h)
        def draw():
            sh = self.page.new_shape()
            sh.draw_rect(r, radius=0.5)
            sh.finish(color=BORDER, fill=WHITE, width=0.9)
            sh.commit()
            self._txt(r.x0 + (w - wl(fsb, s, size))/2,
                      r.y0 + (h + size*0.66)/2 - 0.5, s, fsb, size, DARK)
        self.post.append(draw)
        return r

    def zone(self, cx, baseline, s, size=11.2):
        """Letter-spaced caps zone label with the sheets' white halo."""
        tr = ZTRACK * size
        total = wl(freg, s, size) + tr*(len(s)-1)
        def draw():
            for dy, col in ((-0.7, WHITE), (0, GRAY)):
                x = cx - total/2
                for ch in s:
                    self._txt(x, baseline+dy, ch, freg, size, col)
                    x += wl(freg, ch, size) + tr
        self.post.append(draw)

    def save(self, out):
        for r in self.reds: self.page.add_redact_annot(r)
        if self.reds:
            self.page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE,
                                       graphics=fitz.PDF_REDACT_LINE_ART_NONE)
        for fn in self.post: fn()
        self.doc.save(out, garbage=3, deflate=True)
        self.doc.close()
        print("wrote", out)

def find(page, s, nth=0):
    hits = page.search_for(s)
    return hits[nth] if hits else None

# ------------------------------------------------ LEVEL 1
e = Editor(ORIG[1])
b = find(e.page, "Two locations · serve every level")
e.replace((b.x0, b.y0, b.x1, b.y1),
          "South bank serves all levels · north-east serves 1–2", freg, 9.8, GRAY)
off = find(e.page, "OFFICES")
print("L1 OFFICES", off)
e.zone((off.x0+off.x1)/2, off.y1 + 15, "STAFF ONLY", 9.6)
e.save(DST[1])

# ------------------------------------------------ LEVEL 2
e = Editor(ORIG[2])
e.replace((991.5, 293.1, 1142.4, 302.9),
          "South-west corner · staff only, not a guest route", freg, 9.8, GRAY)
e.replace((991.5, 278.3, 1090.6, 290.7), "Staff stair", fsb, 12.4, DARK)
e.replace((991.5, 321.6, 1111.8, 331.4),
          "South bank serves all levels · north-east serves 1–2", freg, 9.8, GRAY)
e.replace((991.5, 492.6, 1181.0, 502.4),
          "Above the hall · mid-hall stair up · own projector mask", freg, 9.8, GRAY)
# mid-hall stair -> bridge access
e.redact((630.9, 471.8, 638.1, 485.7))
def badge(ed, cx, cy, num, r=8.3, size=11.9):
    def draw():
        sh = ed.page.new_shape()
        sh.draw_circle((cx, cy), r+1.6); sh.finish(fill=WHITE, color=None)
        sh.draw_circle((cx, cy), r);     sh.finish(fill=PINK, color=None)
        sh.commit()
        ed._txt(cx - wl(fsb, num, size)/2, cy + size*0.66/2, num, fsb, size, WHITE)
    ed.post.append(draw)
badge(e, 634.5, 478.7, "10", size=10.2)
e.replace((580.1, 522.2, 657.3, 533.4), "Up to the bridge", fsb, TSIZE, DARK, center=True)
# SW stair: staff only (venue struck "Up to the Gallery")
badge(e, 179.4, 711.4, "3")
e.pill(187.0, 713.2, "Staff only")
# venue STAFF ONLY zone labels
e.zone(168.6, 266.0, "STAFF ONLY", 9.6)
e.zone(373.7, 682.0, "STAFF ONLY", 9.6)
# washrooms sidebar
e.replace((913.5, 740.7, 1124.1, 751.6),
          "level up in the Gallery — guests take the elevators;", freg, 10.9, DARK)
e.replace((913.5, 756.5, 1057.5, 767.3),
          "the south-west stair is staff only.", freg, 10.9, DARK)
e.save(DST[2])

# ------------------------------------------------ LEVEL 3
e = Editor(ORIG[3])
e.replace((991.5, 335.3, 1102.6, 347.7), "Stairs to 222 Bay", fsb, 12.4, DARK)
e.replace((991.5, 350.1, 1095.9, 359.9),
          "Centre stair into 222 Bay · no guest access", freg, 9.8, GRAY)
e.replace((991.5, 392.3, 1061.9, 404.7), "North stairs", fsb, 12.4, DARK)
e.replace((991.5, 407.1, 1107.1, 416.9),
          "West — fire exit, staff only · East — down to Level 2", freg, 9.8, GRAY)
e.replace((991.5, 264.6, 1159.9, 274.4),
          "Patty Watt Room · 35'-9\" × 22'-10\" · staff only", freg, 9.8, GRAY)
# centre stair pill -> No Guest Access
e.redact((444.9, 517.3, 500.5, 530.6))
w = wl(fsb, "No Guest Access", TSIZE) + 2*PAD
e.pill(507.5 - w, 513.9, "No Guest Access")
# NW stair: staff only (venue struck "Down to Trading Floor")
e.pill(161.2, 245.0, "Staff only")
# NE stair: Fire exit -> Down to Trading Floor (new pill covers the old one)
e.redact((716.5, 215.8, 757.2, 231.1))
w = wl(fsb, "Down to Trading Floor", TSIZE) + 2*PAD
e.pill(769.4 - w, 213.0, "Down to Trading Floor", h=20.0)
# venue STAFF ONLY zone labels
e.zone(156.9, 490.0, "STAFF ONLY", 9.6)      # Gallery Boardroom
e.zone(263.3, 344.0, "STAFF ONLY", 7.6)      # west corridor (narrow)
# sidebar
e.replace((913.5, 776.0, 1116.9, 786.8),
          "Go down by the north-east stair or the elevators;", freg, 10.9, DARK)
e.replace((913.5, 791.7, 1041.1, 802.6),
          "the centre stair is 222 Bay only — no guest access.", freg, 10.9, DARK)
e.replace((913.5, 744.5, 1126.7, 755.3),
          "This level sits mostly over 222 Bay next door — only", freg, 10.9, DARK)
e.replace((913.5, 760.2, 1142.6, 771.1),
          "the service core overlaps the Trading Floor below.", freg, 10.9, DARK)
# footnote
e.text(287.2, 800.0,
       "This floor sits mostly over 222 Bay next door — only the service core is above the Trading Floor.",
       freg, 11.2, GRAY)
e.save(DST[3])
print("done")
