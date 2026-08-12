"""
Content model for the Level 1 Lobby event map.

Same treatment as the Gallery sheet: the venue's real plan — walls, door
swings, fixtures — with room floors tinted by category and numbered pins over
the top. See event_map.py for the renderer.

COORDINATES
-----------
Positions are in the Floor 1 blueprint's PDF point space, shared with
geometry/f1.json:

    4.5 pt = 1 ft-0 in   (the drawing is 1/16" = 1'-0")

ORIENTATION
-----------
The DX blueprints put north to the *right* of the page, so this sheet turns
the plan 90 deg counter-clockwise to get north up. That means the blueprint's
page directions map across as:

    page-top    -> west          page-bottom -> east
    page-left   -> south         page-right  -> north

which is worth keeping in mind when reading the coordinates below: the
escalators sit at the page's left edge but land in the SOUTH-WEST of the
finished map, and the coat check reads page-bottom-right but is NORTH-EAST.

After the rotation the floor reads:

    +--------------------------------------------------------+
    |  stair | offices (staff) |            | coat | universal|
    +--------+-----------------+   lobby    | check|  w/r     |
    |  escalators |  w/r  |          floor  |   Teknion       |
    |             |       |   check-in      |   lounge        |
    +-------------+-------+-----------------+-----------------+
                            Grand Staircase -^   entrances -> E
"""
from mapstyle import *          # palette, wall tones, rect()  # noqa: F403

# ------------------------------------------------------------------ frame --
# Drawing extent. Trimmed slightly off the geometry bbox (74.4 176.1 534.9
# 702.8) to drop the property-line dashes on the page-left and the adjoining
# structure down the page-right edge.
FRAME = (76.0, 176.0, 512.0, 703.0)
PLATE = (78.0, 178.0, 510.0, 701.0)

# ------------------------------------------------------------------ zones --
ZONES = [
    # The open lobby floor. Its page-left edge is the angled glass wall the
    # blueprint dimensions as 44'-1"; the notches on the page-right are the
    # office block, the back-of-house rooms and the coat check.
    dict(key="lobby", cat="hall",
         pts=[(250, 240), (336, 240), (336, 330), (427, 330), (427, 344),
              (389, 344), (389, 380), (506, 380), (506, 475), (429, 475),
              (429, 533), (389, 533), (389, 645), (200, 645), (186, 545),
              (247, 336)]),
    dict(key="lounge", cat="lounge", pts=rect(430, 386, 504, 472)),
    dict(key="womens", cat="washroom", pts=rect(131, 382, 166, 518)),
    dict(key="mens", cat="washroom", pts=rect(166, 382, 199, 518)),
    dict(key="universal", cat="washroom", pts=rect(475, 541, 508, 591)),
    dict(key="grand_stair", cat="stair", pts=rect(100, 578, 178, 700)),
    dict(key="escalators", cat="stair", pts=rect(96, 286, 192, 336)),
    dict(key="stair_nw", cat="stair", pts=rect(466, 208, 508, 274)),
    dict(key="stair_ne", cat="stair", pts=rect(436, 650, 496, 698)),
    dict(key="elev_s", cat="elevator", pts=rect(85, 489, 125, 522)),
    dict(key="elev_e", cat="elevator", pts=rect(478, 594, 508, 630)),
    dict(key="coat", cat="service", pts=rect(389, 527, 440, 592)),
    dict(key="coat_store", cat="service", pts=rect(429, 476, 506, 533)),
    dict(key="freight", cat="plant", pts=rect(85, 386, 125, 438)),
    dict(key="offices", cat="staff", pts=rect(336, 210, 462, 330)),
]

# ------------------------------------------------------------- room names --
TITLES = [
    dict(at=(330, 442), size=46, weight=600, text="LOBBY",
         sub="Arrival & check-in", sub_size=22, num=1),
    dict(at=(467, 428), size=16, weight=600, text="TEKNION LOUNGE",
         max_chars=8),
    dict(at=(399, 268), size=14, weight=600, text="STAFF OFFICES",
         colour=INK_SOFT, max_chars=6),
]

SMALL_LABELS = [
    dict(at=(219, 534), text="SECURITY", size=10),
    dict(at=(105, 412), text="FREIGHT", size=11),
]

# --------------------------------------------------------------- features --
FEATURES = [
    dict(num=2, cat="service", icon="info", at=(250, 432),
         label="Check-in", side="right"),
    dict(num=3, cat="service", icon="coat", at=(414, 558),
         label="Coat check", side="left"),
    dict(num=4, cat="washroom", icon="washroom", at=(148, 452),
         label="Women's", side="below"),
    dict(num=5, cat="washroom", icon="washroom", at=(183, 452),
         label="Men's", side="above"),
    dict(num=6, cat="washroom", icon="accessible", at=(491, 566),
         label="Universal", side="left"),
    dict(num=7, cat="stair", icon="stairs", at=(139, 640),
         label="Up to Trading Floor", side="above"),
    dict(num=8, cat="stair", icon="escalator", at=(144, 311),
         label="Down to TD Concourse", side="right"),
    dict(num=9, cat="elevator", icon="elevator", at=(105, 505),
         label="Elevator", side="right"),
    dict(num=9, cat="elevator", icon="elevator", at=(493, 612),
         label="Elevator", side="below"),
    dict(num=10, cat="stair", icon="stairs", at=(487, 241),
         label="Fire exit", side="below"),
    dict(num=10, cat="stair", icon="stairs", at=(466, 674),
         label="Fire exit", side="above"),
    dict(num=11, cat="hall", icon="entrance", at=(412, 672),
         label="Entrance", side="left"),
    dict(num=11, cat="hall", icon="entrance", at=(200, 690),
         label="Entrance", side="above"),
]

# ------------------------------------------------------------- furnishings --
# The front desk and the security desk, both drawn on the blueprint. The
# security desk sits at an angle on the real plan; it is squared off here.
BLOCKS = [
    dict(box=(241, 373, 259, 493)),          # front desk, 2'-8" deep
    dict(box=(206, 493, 233, 521)),          # security desk
]

# ------------------------------------------------------------ way-finding --
ROUTE_LABEL = "Arrival route — entrance to check-in"
ROUTES = [
    [(380, 638), (330, 638), (330, 460), (268, 460)],
]

# ---------------------------------------------------------------- the key --
KEY = [
    dict(num=1, cat="hall", swatch=True, label="Lobby",
         sub="The arrival floor — check in here first"),
    dict(num=2, cat="service", icon="info", label="Check-in",
         sub="Front desk, with the security desk beside it"),
    dict(num=3, cat="service", icon="coat", label="Coat check",
         sub="On the east side, with storage behind"),
    dict(num=4, cat="washroom", icon="washroom", label="Women's washroom",
         sub="South side, off the lobby floor"),
    dict(num=5, cat="washroom", icon="washroom", label="Men's washroom",
         sub="Beside the women's, same entrance"),
    dict(num=6, cat="washroom", icon="accessible", label="Universal washroom",
         sub="North-east corner · step-free"),
    dict(num=7, cat="stair", icon="stairs", label="Grand Staircase",
         sub="Up to the Trading Floor — the main guest route"),
    dict(num=8, cat="stair", icon="escalator", label="Escalators",
         sub="Down to the TD Concourse (PATH)"),
    dict(num=9, cat="elevator", icon="elevator", label="Elevators",
         sub="Two locations · serve every level"),
    dict(num=10, cat="stair", icon="stairs", label="Fire exit stairs",
         sub="North-west and north-east corners"),
    dict(num=11, cat="hall", icon="entrance", label="Entrances",
         sub="East side — confirm guest routing with the venue"),
]

CARDS = [
    dict(title="Lobby LED sign", accent="magenta",
         rows=[("Full aspect ratio", "1080 × 1920 px"),
               ("Image / text safe", "980 × 1820 px"),
               ("Format", "PNG stills only")],
         note="A free-standing totem — place it wherever you like. No video."),
    dict(title="Arrival & getting up", accent="cobalt",
         body="Guests arrive from Bay Street or up the escalators from the TD "
              "Concourse. Check in at the front desk, leave coats on the east "
              "side, then take the Grand Staircase up to the Trading Floor."),
]

SHEET = dict(
    key="lobby-event-map",
    geometry="f1.json",
    level="1",
    title="Lobby",
    tagline="Arrival, check-in and coat check",
    footer_left="Event floor map · Lobby, Level 1",
    footer_right="Design Exchange · 234 Bay Street, Toronto",
    scale_note="Wall geometry taken from the venue's blueprint · north is up "
               "(the venue's own drawings are turned 90°)",
)
