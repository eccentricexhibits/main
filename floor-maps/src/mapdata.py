"""
Content model for the Design Exchange event floor maps.

All coordinates are in the source blueprint's PDF point space, shared with
geometry/f*.json (extracted wall poche). Scale is fixed by the blueprints:

    4.5 pt = 1 ft-0 in   (drawings are 1/16" = 1'-0")

Room positions were read off the DX blueprints; names follow the venue's own
labels where they exist ("Trading Floor", "Gallery Boardroom" / "Patty Watt
Room", "Grand Staircase to Trading Floor").
"""

PT_PER_FT = 4.5

# ---------------------------------------------------------------- palette --
# Vector Institute brand colours (BrandGuidelines_QuickReference, p.6)
BRAND = {
    "magenta":   "#EB088A",
    "cobalt":    "#313CFF",
    "violet":    "#8A25C9",
    "turquoise": "#48C0D9",
    "tangerine": "#FF9E00",
    "lime":      "#CFF933",
    "grey":      "#E9E8E8",
    "black":     "#000000",
}

INK        = "#141414"
INK_SOFT   = "#5C5A5A"
PAPER      = "#FFFFFF"
WALL_FILL  = "#C6C4C4"
WALL_EDGE  = "#979494"
BOH_FILL   = "#F4F3F3"

# Semantic colour assignment, held constant across all three levels so the
# legend only has to be learned once.
ROLE = {
    "event":     BRAND["magenta"],    # the headline event space on each level
    "elevator":  BRAND["cobalt"],
    "stair":     BRAND["violet"],
    "washroom":  BRAND["turquoise"],
    "service":   BRAND["tangerine"],  # coat check, bar, kitchen
    "lounge":    BRAND["lime"],
    "boh":       "#B9B6B6",           # staff only
}

# Glyph colour that clears 4.5:1 against each role colour.
GLYPH_ON = {
    BRAND["magenta"]: "#FFFFFF",
    BRAND["cobalt"]: "#FFFFFF",
    BRAND["violet"]: "#FFFFFF",
    BRAND["turquoise"]: INK,
    BRAND["tangerine"]: INK,
    BRAND["lime"]: INK,
    ROLE["boh"]: INK,
}


def rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


# ------------------------------------------------------------------ LEVEL 1 --
L1 = dict(
    key="level-1-lobby",
    level="1",
    name="Lobby",
    tagline="Arrival, check-in and coat check",
    geometry="f1.json",
    bbox=(74, 172, 540, 706),
    zones=[
        # West edge follows the lobby's angled glass wall, (250.6,306.2)-(184.8,541.9).
        dict(role="event", label="LOBBY", sub="Reception & welcome",
             label_at=(330, 468), size="xl", label_anchor="middle",
             pts=[(184.8, 541.9), (250.6, 306.2), (250.6, 292), (345, 292),
                  (345, 330), (390, 330), (390, 376), (432, 376), (432, 690),
                  (205, 690), (205, 570)]),
        dict(role="stair", label="Grand Staircase", sub="up to Trading Floor",
             label_at=(152, 604), size="s", label_anchor="middle",
             pts=rect(105, 578, 200, 700)),
        dict(role="washroom", label="Washrooms", sub="women's / men's",
             label_at=(170, 552), size="s", label_anchor="middle",
             pts=rect(125, 380, 215, 522)),
        dict(role="washroom", label="", pts=rect(452, 548, 506, 592)),
        dict(role="elevator", label="", pts=rect(95, 388, 145, 432)),
        dict(role="elevator", label="", pts=rect(95, 492, 145, 537)),
        dict(role="elevator", label="", pts=rect(478, 590, 508, 630)),
        dict(role="stair", label="", pts=rect(88, 285, 200, 342)),      # escalators
        dict(role="stair", label="", pts=rect(466, 190, 532, 275)),     # NE stair
        dict(role="stair", label="", pts=rect(425, 648, 502, 700)),     # SE stair
        dict(role="service", label="Coat Check", sub="", label_at=(468, 516),
             size="s", label_anchor="middle", pts=rect(430, 478, 506, 548)),
        dict(role="service", label="", pts=rect(396, 534, 430, 562)),
        dict(role="lounge", label="Teknion Lounge", sub="", label_at=(469, 432),
             size="xs", label_anchor="middle", pts=rect(432, 380, 506, 478)),
    ],
    pins=[
        dict(icon="info", role="event", at=(272, 428), label="Check-in",
             note="Front desk", side="right", show_label=True),
        dict(icon="escalator", role="stair", at=(144, 313), label="Escalators",
             note="down to TD Concourse", side="right", show_label=True),
        dict(icon="stairs", role="stair", at=(152, 662)),
        dict(icon="washroom", role="washroom", at=(170, 450)),
        dict(icon="accessible", role="washroom", at=(479, 570)),
        dict(icon="elevator", role="elevator", at=(120, 410)),
        dict(icon="elevator", role="elevator", at=(120, 514)),
        dict(icon="elevator", role="elevator", at=(493, 610)),
        dict(icon="stairs", role="stair", at=(499, 232)),
        dict(icon="stairs", role="stair", at=(463, 674)),
        dict(icon="coat", role="service", at=(413, 548)),
        dict(icon="entrance", role="event", at=(392, 205), label="Entrance",
             note="Bay St. & TD Concourse", side="left", show_label=True),
    ],
    callouts=[],
    connections="Guests arrive from Bay Street or up the escalators from the TD "
                "Concourse (PATH), check in at the front desk, and leave coats at "
                "the east wall. The Grand Staircase in the south-west corner is the "
                "main route up to the Trading Floor; elevators and four corner "
                "stairwells serve every level.",
)

# ------------------------------------------------------------------ LEVEL 2 --
L2 = dict(
    key="level-2-trading-floor",
    level="2",
    name="Trading Floor",
    tagline="The immersive theatre — main projection space",
    geometry="f2.json",
    bbox=(66, 180, 542, 714),
    zones=[
        dict(role="event", label="TRADING FLOOR", sub="Immersive projection theatre",
             label_at=(306, 400), size="xl", label_anchor="middle",
             pts=[(176, 228), (436, 228), (436, 562), (422, 562), (422, 706),
                  (200, 706), (200, 616), (176, 616)]),
        dict(role="service", label="Kitchen", sub="", label_at=(162, 340),
             size="xs", label_anchor="middle", pts=rect(148, 348, 176, 432)),
        dict(role="elevator", label="", pts=rect(98, 392, 146, 440)),
        dict(role="elevator", label="", pts=rect(98, 494, 146, 542)),
        dict(role="elevator", label="", pts=rect(478, 594, 512, 634)),
        dict(role="stair", label="", pts=rect(92, 192, 152, 245)),
        dict(role="stair", label="", pts=rect(466, 192, 526, 245)),
        dict(role="stair", label="", pts=rect(120, 612, 200, 704)),
        dict(role="stair", label="", pts=rect(422, 652, 502, 704)),
    ],
    # Projection surfaces, drawn as heavy magenta rules on the wall lines.
    screens=[
        dict(kind="line", p0=(178, 230), p1=(434, 230), label="DOMINO SCREEN WALL",
             label_at=(306, 258), rot=0),
        dict(kind="line", p0=(178, 232), p1=(178, 590), label="PROJECTION WALL",
             label_at=(196, 400), rot=90),
        dict(kind="line", p0=(434, 232), p1=(434, 590), label="PROJECTION WALL",
             label_at=(416, 400), rot=-90),
    ],
    pins=[
        dict(icon="stairs", role="stair", at=(275, 575), label="Grand Staircase",
             note="down to Lobby", side="right", show_label=True),
        dict(icon="elevator", role="elevator", at=(122, 416)),
        dict(icon="elevator", role="elevator", at=(122, 518)),
        dict(icon="elevator", role="elevator", at=(495, 614)),
        dict(icon="stairs", role="stair", at=(122, 218)),
        dict(icon="stairs", role="stair", at=(496, 218)),
        dict(icon="stairs", role="stair", at=(160, 658)),
        dict(icon="stairs", role="stair", at=(462, 678)),
        dict(icon="food", role="service", at=(162, 390)),
        dict(icon="theatre", role="event", at=(306, 300)),
    ],
    callouts=[
        dict(at=(306, 500), w=215, title="No washrooms on this level",
             body="Nearest washrooms are one level down in the Lobby, or one "
                  "level up in the Gallery. Stairs and elevators sit in all "
                  "four corners.", warn=True),
    ],
    connections="The Grand Staircase lands at the south edge of the floor, under "
                "the bridge. Washrooms are on Level 1 and Level 3 only.",
)

# ------------------------------------------------------------------ LEVEL 3 --
L3 = dict(
    key="level-3-gallery",
    level="3",
    name="Gallery",
    tagline="Exhibition hall and boardroom",
    geometry="f3.json",
    bbox=(92, 180, 520, 770),
    zones=[
        dict(role="event", label="GALLERY", sub="Exhibition hall",
             label_at=(168, 430), size="xl", label_anchor="middle",
             pts=[(109, 195), (231, 195), (231, 628), (455, 628), (455, 748),
                  (109, 748)]),
        dict(role="lounge", label="GALLERY BOARDROOM", sub="Patty Watt Room",
             label_at=(328, 252), size="m", label_anchor="middle",
             pts=rect(231, 196, 425, 319)),
        dict(role="washroom", label="WASHROOMS", sub="women's / men's / universal",
             label_at=(356, 485), size="s", label_anchor="middle", rot=-90,
             pts=rect(336, 385, 400, 585)),
        dict(role="elevator", label="", pts=rect(438, 410, 495, 478)),
        dict(role="elevator", label="", pts=rect(438, 520, 495, 570)),
        dict(role="stair", label="", pts=rect(445, 196, 502, 255)),
        dict(role="stair", label="", pts=rect(240, 494, 305, 588)),
        dict(role="stair", label="", pts=rect(462, 698, 505, 756)),
        dict(role="boh", label="", pts=rect(231, 321, 336, 627)),
    ],
    screens=[
        dict(kind="line", p0=(231, 370), p1=(231, 626), label="PROJECTION WALL",
             label_at=(249, 500), rot=90),
        dict(kind="line", p0=(233, 626), p1=(440, 626), label="PROJECTION WALL",
             label_at=(340, 650), rot=0),
        dict(kind="line", p0=(110, 596), p1=(110, 668), label="LED WALL",
             label_at=(128, 632), rot=90),
    ],
    pins=[
        dict(icon="stairs", role="stair", at=(272, 540), label="Stairs",
             note="down to Trading Floor", side="right", show_label=True),
        dict(icon="washroom", role="washroom", at=(368, 412)),
        dict(icon="accessible", role="washroom", at=(368, 556)),
        dict(icon="elevator", role="elevator", at=(466, 444)),
        dict(icon="elevator", role="elevator", at=(466, 545)),
        dict(icon="stairs", role="stair", at=(473, 224)),
        dict(icon="stairs", role="stair", at=(483, 726)),
        dict(icon="theatre", role="event", at=(328, 300)),
    ],
    callouts=[
        dict(at=(300, 700), w=190, title="Gallery loop",
             body="The exhibition floor wraps the building core in an L. "
                  "Washrooms, stairs and elevators are all inside that core, "
                  "reachable from either leg."),
    ],
    connections="The centre stair drops straight to the Trading Floor. Washrooms "
                "here are the closest to the Trading Floor going up.",
)

FLOORS = [L1, L2, L3]
