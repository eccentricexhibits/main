"""
Content model for the "Getting Around" sheet.

This is the one sheet in the set that is not a floor plan. It is a section
through the building: the four levels stacked, with every vertical route drawn
across them like lines on a transit map, so you can read at a glance which
stair or elevator reaches which floor.

That shape is deliberate. Each DX blueprint was drawn as its own sheet with its
own page origin, so the levels do not register against one another well enough
to claim where a shaft sits in plan. What can be stated with confidence is what
each route *connects*, and that is exactly what a section shows.

Colour follows the rest of the set: violet for stairs and escalators, cobalt
for elevators, turquoise for washrooms, grey for anything crew-only.
"""
from mapstyle import *          # palette, wall tones, rect()  # noqa: F403

# Levels, top of the building first.
LEVELS = [
    dict(id="3", name="Gallery", cat="hall", washrooms=True,
         desc="Exhibition hall + boardroom"),
    dict(id="2", name="Trading Floor", cat="hall", washrooms=False,
         desc="The immersive theatre"),
    dict(id="1", name="Lobby", cat="hall", washrooms=True,
         desc="Arrival and check-in"),
    dict(id="C", name="TD Concourse", cat="corridor", washrooms=None,
         chip_cat="plain", desc="PATH connection"),
]

# Vertical routes. `levels` lists every floor the route stops at; the renderer
# draws the line from the topmost to the bottommost and marks each stop.
LANES = [
    dict(num=1, cat="stair", icon="escalator", label="Escalators",
         levels=["1", "C"]),
    dict(num=2, cat="stair", icon="stairs", label="Grand Staircase",
         levels=["2", "1"]),
    dict(num=3, cat="stair", icon="stairs", label="Centre stair",
         levels=["3", "2"]),
    dict(num=4, cat="elevator", icon="elevator", label="Elevators",
         levels=["3", "2", "1"]),
    dict(num=5, cat="stair", icon="stairs", label="Fire stairs",
         levels=["3", "2", "1"]),
    dict(num=6, cat="plant", icon="elevator", label="Freight",
         levels=["3", "2", "1"]),
]

KEY = [
    dict(num=1, cat="stair", icon="escalator", label="Escalators",
         sub="TD Concourse up to the Lobby — the PATH connection"),
    dict(num=2, cat="stair", icon="stairs", label="Grand Staircase",
         sub="Lobby up to the Trading Floor — the main guest route"),
    dict(num=3, cat="stair", icon="stairs", label="Centre stair",
         sub="Trading Floor up to the Gallery"),
    dict(num=4, cat="elevator", icon="elevator", label="Elevators",
         sub="Every level · two locations on each floor"),
    dict(num=5, cat="stair", icon="stairs", label="Fire exit stairs",
         sub="Every level · corner stairwells, also the exits"),
    dict(num=6, cat="plant", icon="elevator", label="Freight elevator",
         sub="Every level · load-in and crew only"),
    dict(num=7, cat="washroom", icon="washroom", label="Washrooms",
         sub="Levels 1 and 3 only — none on the Trading Floor"),
]

CARDS = [
    dict(title="The guest route", accent="magenta",
         body="Arrive in the Lobby from Bay Street, or up the escalators from "
              "the TD Concourse. Check in, leave coats, then take the Grand "
              "Staircase up to the Trading Floor. The Gallery is one more "
              "level up, by the centre stair or the elevators."),
    dict(title="Step-free access", accent="cobalt",
         body="Elevators reach every level. The universal washroom is on "
              "Level 1; Level 3's washrooms have accessible stalls. There are "
              "no washrooms at all on the Trading Floor."),
]

SHEET = dict(
    key="building-overview",
    title="Getting Around",
    tagline="Every vertical route in the building",
    chip_top="LEVELS",
    chip_main="1–3",
    chip_size=44,
    footer_left="Event floor map · Getting Around",
    footer_right="Design Exchange · 234 Bay Street, Toronto",
    note="A section through the building, not a plan — each route is drawn "
         "across the levels it reaches.",
)
