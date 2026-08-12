"""
Content model for the Level 3 Gallery *event* map.

This is the guest-facing sheet: the venue's real plan — walls, door swings,
fixtures — with room floors tinted by category and numbered pins over the top.
The zone polygons below are simplified rectangles used only to tint floors;
they are drawn *under* the poche, so they never have to line up perfectly.

COORDINATES
-----------
Positions are in the Floor 3 blueprint's PDF point space, the same space used
by geometry/f3.json:

    4.5 pt = 1 ft-0 in   (the drawing is 1/16" = 1'-0")

ORIENTATION
-----------
The blueprint's north arrow points to the *right* of its page, so the DX
sheets are drawn 90 deg off north-up. This sheet rotates the plan 90 deg
counter-clockwise, which puts true north at the top and matches the
orientation of the event team's own 3D gallery renders
(Floor_3__Reference_Images, "Vector - Gallery - Vendor Tables").

After that rotation the plan reads:

    up = north    right = east    down = south    left = west

    +---------------------------------------------------+
    | boardroom |  W   |   service core   |  E  |        |
    |           | corr |  (washrooms etc) | corr| east   |
    +-----------+------+------------------+-----+ wing   |
    |                exhibition hall (south wing)        |
    +---------------------------------------------------+

So the blueprint's "west leg" is really the building's SOUTH wing, and its
"south leg" is the EAST wing. The two together make the L-shaped hall.
"""

# ------------------------------------------------------------------ frame --
# Floorplate, interior faces of the exterior walls (blueprint space).
PLATE = (109.0, 205.0, 504.0, 754.0)          # x0, y0, x1, y1

# Drawing extent — the blueprint's own geometry bbox, so the exterior walls
# are inside the frame rather than clipped off at their inner face.
FRAME = (99.05, 184.66, 512.85, 764.19)       # x0, y0, x1, y1

# Rotation: map_u = y - FRAME.y0 ; map_v = FRAME.x1 - x
MAP_W = FRAME[3] - FRAME[1]                   # 579.5 units across (east-west)
MAP_H = FRAME[2] - FRAME[0]                   # 413.8 units down   (north-south)


def rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


from mapstyle import *          # palette, wall tones, rect()  # noqa: F403


# ------------------------------------------------------------------ zones --
# Painted in order. The whole floorplate is laid down as "staff" first, so
# anything not named here reads as building services without needing its own
# polygon — that is what keeps the sheet clear of blueprint clutter.
ZONES = [
    dict(key="hall", cat="hall", stroke=True,
         pts=[(109, 205), (236, 205), (236, 626), (443, 626),
              (443, 754), (109, 754)]),
    dict(key="board", cat="board", stroke=True, pts=rect(241, 209, 429, 319)),
    dict(key="corr_w", cat="corridor", pts=rect(236, 319, 445, 362)),
    dict(key="corr_e", cat="corridor", pts=rect(236, 591, 443, 626)),
    dict(key="mens", cat="washroom", stroke=True, pts=rect(334, 364, 384, 482)),
    dict(key="womens", cat="washroom", stroke=True, pts=rect(334, 486, 384, 591)),
    dict(key="stair_c", cat="stair", stroke=True, pts=rect(244, 496, 286, 574)),
    dict(key="stair_nw", cat="stair", stroke=True, pts=rect(450, 207, 502, 292)),
    dict(key="stair_ne", cat="stair", stroke=True, pts=rect(460, 690, 502, 752)),
    dict(key="elev", cat="elevator", stroke=True, pts=rect(447, 528, 487, 566)),
    dict(key="freight", cat="service", stroke=True, pts=rect(447, 364, 487, 471)),
]

# ------------------------------------------------------------- room names --
# Placed in blueprint space; the renderer rotates them and keeps text upright.
TITLES = [
    dict(at=(172, 480), size=46, weight=600, text="EXHIBITION HALL",
         sub="The Gallery", sub_size=22, num=1),
    dict(at=(335, 264), size=25, weight=600, text="GALLERY BOARDROOM",
         sub="Patty Watt Room", sub_size=17, num=2, max_chars=13),
    dict(at=(300, 440), size=15, weight=600, text="STAFF ONLY",
         colour=INK_SOFT, max_chars=11),
]

# --------------------------------------------------------------- features --
# Badge + number chip + label pill. `at` is the badge centre, `side` is where
# the label pill sits relative to it.
FEATURES = [
    dict(num=3, cat="washroom", icon="washroom", at=(359, 423),
         label="Men's", side="below"),
    dict(num=4, cat="washroom", icon="washroom", at=(359, 538),
         label="Women's", side="below"),
    dict(num=5, cat="stair", icon="stairs", at=(265, 535),
         label="Stairs down", side="left"),
    dict(num=6, cat="elevator", icon="elevator", at=(467, 547),
         label="Elevator", side="right"),
    dict(num=7, cat="stair", icon="stairs", at=(476, 250),
         label="Fire exit", side="right"),
    dict(num=7, cat="stair", icon="stairs", at=(481, 721),
         label="Fire exit", side="left", chip_only=False),
    dict(num=8, cat="service", icon="elevator", at=(467, 417),
         label="Freight", side="left"),
]

# ------------------------------------------------------- immersive AV kit --
# DX Tech Deck p.13-14 (the "Gallery" section; its sidebar heading reads
# TRADING FLOOR, which is a copy-paste slip in the deck itself).
#
# Full edge-to-edge surface is 7015 x 1080 px, made of
#   south wall 3242 px | gap 400 px | corner 307 px | east wall 3066 px
# The east run measures 46'-0" on the drawing, which pins the surface at
# ~66.7 px/ft; the south run then lands on the full height of the core's
# south face. The two runs wrap the hall's inside corner — exactly the
# corner photographed on p.13 of the deck.
SURFACES = [
    dict(path=[(236, 362), (236, 626), (443, 626)], num=9,
         label="IMMERSIVE PROJECTION WALLS", label_at=(219, 402)),
    dict(path=[(426, 232), (426, 292)], w=5, glow=False, size=12,
         label="SCREEN", label_at=(415, 262)),
]

# ---------------------------------------------------------- vendor tables --
# Indicative layout, traced from the event team's own
# "Vector - Gallery - Vendor Tables" plan (Floor_3__Reference_Images p.1).
RUNS = [
    dict(axis="y", const=211, lo=365, hi=598, n=7),    # south wing, inner row
    dict(axis="y", const=135, lo=245, hi=630, n=9),    # south wing, window row
    dict(axis="x", const=727, lo=180, hi=430, n=7),    # east wing, window row
]
# The two north-south corridors off the hall; naming them stops the light
# strips reading as gaps in the floor.
SMALL_LABELS = [
    dict(at=(424, 340), text="CORRIDOR"),
    dict(at=(424, 608), text="CORRIDOR"),
]

RUN_LABELS = [
    dict(at=(174, 300), text="VENDOR TABLES", rot=True),
    dict(at=(300, 668), text="VENDOR TABLES", rot=True),
]

# ------------------------------------------------------------ way-finding --
# Dashed guide from the hall, up each corridor, to a washroom door.
ROUTE_LABEL = "Route from the hall to the washrooms"

ROUTES = [
    [(225, 340), (370, 340), (370, 371)],      # to the men's room
    [(225, 608), (352, 608), (352, 570)],      # to the women's room
]

# ---------------------------------------------------------------- the key --
KEY = [
    dict(num=1, cat="hall", swatch=True,
         label="Exhibition Hall",
         sub="The main event floor — an L that wraps the service core"),
    dict(num=2, cat="board", swatch=True,
         label="Gallery Boardroom",
         sub="Patty Watt Room · 35'-9\" × 22'-10\" · wall screen"),
    dict(num=3, cat="washroom", icon="washroom",
         label="Men's washroom",
         sub="Off the west corridor · accessible stall"),
    dict(num=4, cat="washroom", icon="washroom",
         label="Women's washroom",
         sub="Off the east corridor · accessible stall"),
    dict(num=5, cat="stair", icon="stairs",
         label="Stairs to Trading Floor",
         sub="Centre stair, down one level"),
    dict(num=6, cat="elevator", icon="elevator",
         label="Elevator",
         sub="Serves every level"),
    dict(num=7, cat="stair", icon="stairs",
         label="Fire exit stairs",
         sub="Two, both along the north side"),
    dict(num=8, cat="service", icon="elevator",
         label="Freight elevator",
         sub="Load-in and crew only"),
    dict(num=9, cat="hall", rule=True,
         label="Immersive projection walls",
         sub="Wrap the hall's inside corner · 7015 × 1080 px"),
    dict(num=10, cat="hall", table=True,
         label="Vendor tables",
         sub="Indicative — from the event team's gallery plan"),
]

CARDS = [
    dict(title="Immersive AV", accent="magenta",
         rows=[("Projection, edge to edge", "7015 × 1080 px"),
               ("  south run · gap · corner", "3242 · 400 · 307"),
               ("  east run", "3066 px"),
               ("LED wall (separate)", "1920 × 1080 px"),
               ("Ceiling, unobstructed", "12 ft")],
         note="LED wall position to be confirmed with the venue."),
    dict(title="Getting between floors", accent="cobalt",
         body="The centre stair drops straight to the Trading Floor, one "
              "level down — and that floor has no washrooms, so these are the "
              "closest. Elevators serve every level; the two fire stairs are "
              "the exits."),
]

SHEET = dict(
    key="gallery-event-map",
    geometry="f3.json",
    level="3",
    title="Gallery",
    tagline="Exhibition hall, boardroom and immersive walls",
    footer_left="Event floor map · Gallery, Level 3",
    footer_right="Design Exchange · 234 Bay Street, Toronto",
    scale_note="Wall geometry taken from the venue's blueprint · north is up "
               "(the venue's own drawings are turned 90°)",
)
