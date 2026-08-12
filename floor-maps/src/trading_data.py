"""
Content model for the Level 2 Trading Floor event map.

Same treatment as the other event maps: the venue's real plan with room floors
tinted by category and numbered pins over the top. See event_map.py.

COORDINATES
-----------
Floor 2 blueprint PDF point space, shared with geometry/f2.json:

    4.5 pt = 1 ft-0 in   (the drawing is 1/16" = 1'-0")

ORIENTATION
-----------
North is to the *right* of the blueprint page, so this sheet turns the plan
90 deg counter-clockwise to put north up:

    page-top -> west     page-bottom -> east
    page-left -> south   page-right  -> north

The hall is 106'-2" the page-y way and 57'-8" the page-x way, so after the
rotation it reads as a wide room — about 106 ft east to west, 58 ft north to
south — under a 40 ft unobstructed ceiling.

    +-------------------------------------------------------+
    | stair |          NORTH projection wall        | stair |
    | D  +----------------------------------------------+   |
    | O  |                                              |   |
    | M  |            TRADING FLOOR                | br |   |
    | I  |                                         | dg |   |
    | N  +----------------------------------------------+   |
    | O  |          SOUTH projection wall          |  Grand |
    | stair | kitchen | freight | elevator |        | Stair |
    +-------------------------------------------------------+
"""
from mapstyle import *          # palette, wall tones, rect()  # noqa: F403

# ------------------------------------------------------------------ frame --
# Trimmed off the geometry bbox (70.2 185.2 537.9 710.6) to drop the empty
# margin down the page-right edge.
FRAME = (70.0, 185.0, 520.0, 711.0)
PLATE = (72.0, 187.0, 518.0, 709.0)

# ------------------------------------------------------------------ zones --
ZONES = [
    # The hall itself: 57'-8" x 106'-2" on the blueprint's own dimensions.
    dict(key="hall", cat="hall", pts=rect(178, 220, 434, 694)),
    dict(key="kitchen", cat="service", pts=rect(136, 346, 176, 430)),
    dict(key="grand_stair", cat="stair", pts=rect(96, 628, 170, 706)),
    dict(key="hall_stair", cat="stair", pts=rect(239, 562, 310, 590)),
    dict(key="stair_sw", cat="stair", pts=rect(98, 197, 133, 245)),
    dict(key="stair_nw", cat="stair", pts=rect(475, 199, 509, 246)),
    dict(key="stair_ne", cat="stair", pts=rect(450, 665, 502, 709)),
    dict(key="elev_s", cat="elevator", pts=rect(88, 499, 124, 531)),
    dict(key="elev_ne", cat="elevator", pts=rect(478, 601, 509, 639)),
    dict(key="freight", cat="plant", pts=rect(88, 393, 124, 448)),
]

# --------------------------------------------------------------- overhead --
# "Bridge Over" on the blueprint — it crosses above the hall, and the tech
# deck ships a separate projector mask for it.
OVERHEAD = [
    dict(box=(178, 587, 434, 625), label="BRIDGE OVER",
         label_at=(306, 606), rot=True),
]

# ------------------------------------------------------------- seating --
# "Vector - 350px Theater Style", page 1 of the Level 2 reference file. That
# document is a raster, so this is traced rather than measured: the seat grid
# was found by pixel profile, then registered to the blueprint on the hall's
# own walls — image y 394/1350 against blueprint x 178/434, image x 1786
# against blueprint y 220. The two scales that fell out agree to 1.3%.
#
# 22 rows of 16 in two blocks with a centre cross-aisle = 352 marks against a
# stated 350, so a row is presumably two short. Indicative, not surveyed.
GRIDS = [
    dict(x0=198, x1=290, nx=11, y0=308, y1=527, ny=16, w=6.5, d=7.5),
    dict(x0=319, x1=412, nx=11, y0=308, y1=527, ny=16, w=6.5, d=7.5),
]

# ------------------------------------------------------------- room names --
TITLES = [
    # In the centre cross-aisle — the one part of the hall the seating leaves
    # clear. The header already carries the floor name at full size.
    dict(at=(305, 417), size=34, weight=600, text="TRADING FLOOR", num=1),
]

RUN_LABELS = [
    dict(at=(306, 560), text="350 SEATS"),
]

SMALL_LABELS = [
    dict(at=(470, 430), text="STAFF", size=11),
]

# --------------------------------------------------------------- features --
FEATURES = [
    dict(num=2, cat="stair", icon="stairs", at=(133, 667),
         label="Down to the Lobby", side="left"),
    dict(num=3, cat="stair", icon="stairs", at=(274, 576),
         label="Up to the Gallery", side="below"),
    dict(num=4, cat="elevator", icon="elevator", at=(106, 515),
         label="Elevator", side="left"),
    dict(num=4, cat="elevator", icon="elevator", at=(493, 620),
         label="Elevator", side="left"),
    dict(num=5, cat="stair", icon="stairs", at=(115, 221),
         label="Fire exit", side="right"),
    dict(num=5, cat="stair", icon="stairs", at=(492, 222),
         label="Fire exit", side="right"),
    dict(num=5, cat="stair", icon="stairs", at=(476, 687),
         label="Fire exit", side="below"),
    dict(num=6, cat="service", icon="food", at=(156, 388),
         label="Kitchen", side="above"),
    dict(num=7, cat="plant", icon="elevator", at=(106, 420),
         label="Freight", side="below"),
]

# ------------------------------------------------------- immersive AV kit --
# DX Tech Deck p.7-8. Three walls, ~45 ft tall, ~270 ft of surface, delivered
# as one 6872 x 1080 px file. The projection surfaces are built forms — each
# long wall carries a "cube" with draped areas either side — so the pixel
# widths do not divide onto the structural walls in simple proportion. What
# the plan can show reliably is which wall is which:
#
#   north wall 2239 px | west wall 1679 px (carries the Domino screen)
#   south wall 2239 px
#
# With north to the page-right, the two 2239 px walls are the hall's long
# north and south sides and the Domino sits on the short west end, which is
# exactly what the deck's naming says.
SURFACES = [
    dict(path=[(434, 224), (434, 690)], num=8, label="NORTH PROJECTION WALL",
         label_at=(426, 457)),
    dict(path=[(178, 224), (178, 690)], label="SOUTH PROJECTION WALL",
         label_at=(186, 515)),
    dict(path=[(180, 220), (432, 220)], num=9, label="DOMINO SCREEN",
         label_at=(306, 229), rot=True),
]

# ---------------------------------------------------------------- the key --
KEY = [
    dict(num=1, cat="hall", swatch=True, label="Trading Floor",
         sub="The immersive theatre — 106 × 58 ft, 40 ft ceiling"),
    dict(num=2, cat="stair", icon="stairs", label="Grand Staircase",
         sub="Down to the Lobby — the main guest route"),
    dict(num=3, cat="stair", icon="stairs", label="Stairs to the Gallery",
         sub="From the middle of the hall, up one level"),
    dict(num=4, cat="elevator", icon="elevator", label="Elevators",
         sub="Two locations · serve every level"),
    dict(num=5, cat="stair", icon="stairs", label="Fire exit stairs",
         sub="Three corners of the floor"),
    dict(num=6, cat="service", icon="food", label="Kitchen",
         sub="Catering — staff only"),
    dict(num=7, cat="plant", icon="elevator", label="Freight elevator",
         sub="Load-in and crew only"),
    dict(num=8, cat="hall", rule=True, label="Immersive projection walls",
         sub="Three walls · ~45 ft tall · 6872 × 1080 px"),
    dict(num=9, cat="hall", rule=True, label="Domino screen",
         sub="On the west wall · 1655 × 630 px"),
    dict(num=10, cat="staff", dash=True, label="Bridge over",
         sub="Crosses above the hall · has its own projector mask"),
    dict(num=11, cat="hall", table=True, label="Seating — 350, theatre style",
         sub="Indicative — from the event team's Level 2 plan"),
]

CARDS = [
    dict(title="Immersive projection", accent="magenta",
         rows=[("Full, edge to edge", "6872 × 1080 px"),
               ("North / south walls", "2239 × 1080 each"),
               ("West wall (Domino)", "1679 × 1080 px"),
               ("Ceiling, unobstructed", "40 ft")],
         note="Deliver one flattened file at full size, plus a layer per surface."),
    dict(title="No washrooms on this level", accent="cobalt",
         body="The nearest are one level down in the Lobby, or one level up "
              "in the Gallery. The Grand Staircase lands in the south-east "
              "corner of this floor."),
]

SHEET = dict(
    key="trading-floor-event-map",
    geometry="f2.json",
    level="2",
    title="Trading Floor",
    tagline="The immersive projection theatre",
    footer_left="Event floor map · Trading Floor, Level 2",
    footer_right="Design Exchange · 234 Bay Street, Toronto",
    scale_note="Wall geometry taken from the venue's blueprint · north is up "
               "(the venue's own drawings are turned 90°)",
)
