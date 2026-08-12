"""
Shared drawing style for the event-map sheets.

Colour is semantic and constant across every floor, so a guest who reads the
key on one sign can read all of them. Room floors are light tints; the same
hue at full strength carries the pins and rules.
"""

PT_PER_FT = 4.5                               # 1/16" = 1'-0" on every DX sheet

BRAND = {
    "magenta":   "#EB088A",
    "cobalt":    "#313CFF",
    "violet":    "#8A25C9",
    "turquoise": "#48C0D9",
    "tangerine": "#FF9E00",
    "lime":      "#CFF933",
}

INK      = "#141414"
INK_SOFT = "#5F5C5C"
PAPER    = "#FFFFFF"

# Big-area fills, light enough that INK body text clears 4.5:1 on all of them.
FILL = {
    "hall":     "#FBDCEC",     # the headline event space
    "board":    "#F2C2DE",     # a second event room
    "washroom": "#DDF1F7",
    "stair":    "#EBDDF8",
    "elevator": "#E0E2FF",
    "lounge":   "#F0FAC9",
    "service":  "#FFEBCB",     # coat check, bar, food
    "corridor": "#F3F2F0",
    "staff":    "#F4F2F1",
    "plant":    "#D9D6D5",     # freight, risers, anything crew-only
}

ACCENT = {
    "hall":     BRAND["magenta"],
    "board":    BRAND["magenta"],
    "washroom": BRAND["turquoise"],
    "stair":    BRAND["violet"],
    "elevator": BRAND["cobalt"],
    "lounge":   "#6F8F00",     # lime is too pale to outline or take a glyph
    "service":  BRAND["tangerine"],
    "staff":    "#8C8988",
    "plant":    "#8C8988",
}

# Glyph colour that clears 4.5:1 on each accent.
GLYPH_ON = {
    BRAND["magenta"]:   "#FFFFFF",
    BRAND["cobalt"]:    "#FFFFFF",
    BRAND["violet"]:    "#FFFFFF",
    BRAND["turquoise"]: INK,
    BRAND["tangerine"]: INK,
    "#6F8F00":          "#FFFFFF",
    "#8C8988":          "#FFFFFF",
}

# Base plan. Thin walls read near-white with a defined edge so the coloured
# floors stay loudest; the blueprints also fill service cores and adjoining
# structures as poche, and anything that big is toned as floor instead.
WALL_FILL  = "#F1EFEE"
WALL_EDGE  = "#7E7B7A"
MASS_FILL  = "#DEDCDB"
WALL_DARK  = "#8E8B8A"
GLAZE_FILL = "#E9E7E6"
DETAIL_INK = "#969392"

PLATE_EDGE = "#232323"
TABLE_FILL = "#8E8A89"
ROUTE      = BRAND["cobalt"]


def rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
