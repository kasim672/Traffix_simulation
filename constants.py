# =============================================================================
#  constants.py  –  Global configuration for the Traffic Simulation
# =============================================================================

# ── Window ────────────────────────────────────────────────────────────────────
SCREEN_WIDTH  = 1100
SCREEN_HEIGHT = 750
FPS           = 60
TITLE         = "Real-Time Traffic Simulation"

# ── Direction identifiers ─────────────────────────────────────────────────────
EAST  = 0   # moving right  (+x)
WEST  = 1   # moving left   (−x)
SOUTH = 2   # moving down   (+y)
NORTH = 3   # moving up     (−y)

DIR_NAMES = {EAST: "EAST", WEST: "WEST", SOUTH: "SOUTH", NORTH: "NORTH"}

# ── Colour palette ────────────────────────────────────────────────────────────
WHITE        = (255, 255, 255)
BLACK        = (10,  10,  10)
GRASS        = (68, 105, 60)
GRASS_DARK   = (55,  88, 48)
ROAD_DARK    = (50,  52,  60)
ROAD_MID     = (62,  64,  72)
LANE_MARK    = (210, 200, 80)     # yellow dashes
STOP_LINE    = (235, 235, 235)    # white stop lines
SIDEWALK     = (148, 140, 130)
CURB         = (120, 112, 102)
LIGHT_RED    = (230,  55,  55)
LIGHT_YELLOW = (245, 200,  30)
LIGHT_GREEN  = (45,  215,  80)
LIGHT_OFF    = (50,  50,   52)
POLE_DARK    = (30,  30,   36)
POLE_EDGE    = (65,  65,   78)
UI_PANEL     = (14,  18,  28)
UI_BORDER    = (70, 140, 220)
UI_LABEL     = (140, 150, 170)
UI_VALUE     = (100, 235, 145)
UI_TITLE_C   = (80,  165, 230)
UI_WARN      = (235, 170,  50)
AMBULANCE_BODY = (238, 242, 248)
AMBULANCE_STRIPE = (220, 54, 54)
AMBULANCE_LIGHT_RED = (235, 70, 70)
AMBULANCE_LIGHT_BLUE = (70, 130, 235)

# ── Road geometry ─────────────────────────────────────────────────────────────
ROAD_CENTER_X = SCREEN_WIDTH  // 2          # 550
ROAD_CENTER_Y = SCREEN_HEIGHT // 2          # 375

ROAD_HALF_W   = 88       # half of total road width; one lane = 88 px (total = 176 px)

INTER_LEFT   = ROAD_CENTER_X - ROAD_HALF_W  # left  edge of intersection box
INTER_RIGHT  = ROAD_CENTER_X + ROAD_HALF_W  # right edge
INTER_TOP    = ROAD_CENTER_Y - ROAD_HALF_W  # top   edge
INTER_BOTTOM = ROAD_CENTER_Y + ROAD_HALF_W  # bottom edge
INTER_W      = ROAD_HALF_W * 2
INTER_H      = ROAD_HALF_W * 2

# Lane centre lines
EASTBOUND_Y  = ROAD_CENTER_Y + ROAD_HALF_W // 2   # lower horizontal lane  (→)
WESTBOUND_Y  = ROAD_CENTER_Y - ROAD_HALF_W // 2   # upper horizontal lane  (←)
SOUTHBOUND_X = ROAD_CENTER_X - ROAD_HALF_W // 2   # left  vertical   lane  (↓)
NORTHBOUND_X = ROAD_CENTER_X + ROAD_HALF_W // 2   # right vertical   lane  (↑)

# ── Vehicle physics ───────────────────────────────────────────────────────────
VEHICLE_LENGTH = 38     # pixels
VEHICLE_WIDTH  = 22     # pixels
BASE_SPEED     = 2.4    # pixels per frame at 60 fps
BRAKE_DIST     = 88     # start braking within this distance (px)
MIN_GAP        = 9      # minimum bumper-to-bumper gap (px)
ACCEL_RATE     = 0.09   # acceleration (px/frame)
DECEL_RATE     = 0.22   # deceleration (px/frame)

# ── Traffic signals ───────────────────────────────────────────────────────────
GREEN_DURATION  = 7.0   # seconds per green phase
YELLOW_DURATION = 2.5   # seconds per yellow phase

# Phase name constants
NS_GREEN  = "NS_GREEN"
NS_YELLOW = "NS_YELLOW"
EW_GREEN  = "EW_GREEN"
EW_YELLOW = "EW_YELLOW"

# Human-readable phase labels for the UI
PHASE_LABELS = {
    NS_GREEN:  "N/S  GREEN ",
    NS_YELLOW: "N/S  YELLOW",
    EW_GREEN:  "E/W  GREEN ",
    EW_YELLOW: "E/W  YELLOW",
}
PHASE_COLORS = {
    NS_GREEN:  LIGHT_GREEN,
    NS_YELLOW: LIGHT_YELLOW,
    EW_GREEN:  LIGHT_GREEN,
    EW_YELLOW: LIGHT_YELLOW,
}

# ── Spawning ──────────────────────────────────────────────────────────────────
BASE_SPAWN_INTERVAL = 2.2    # simulation-seconds between spawn attempts
SPAWN_PROBABILITY   = 0.80   # chance a spawn attempt actually creates a vehicle

# ── Speed control ─────────────────────────────────────────────────────────────
MIN_SPEED_MULT = 0.25
MAX_SPEED_MULT = 4.00
SPEED_STEP     = 0.25
