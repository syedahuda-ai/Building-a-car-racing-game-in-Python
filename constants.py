"""
constants.py - All game constants and configuration values
"""

# Screen
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 700
FPS = 60
TITLE = "🏎️  TURBO RACE 3D"

# Colors
BLACK        = (0,   0,   0)
WHITE        = (255, 255, 255)
RED          = (220, 30,  30)
DARK_RED     = (150, 10,  10)
GREEN        = (34,  197, 94)
DARK_GREEN   = (20,  120, 60)
BLUE         = (30,  100, 220)
YELLOW       = (255, 215, 0)
ORANGE       = (255, 140, 0)
GRAY         = (100, 100, 100)
DARK_GRAY    = (40,  40,  40)
LIGHT_GRAY   = (180, 180, 180)
ROAD_DARK    = (50,  50,  50)
ROAD_LIGHT   = (70,  70,  70)
GRASS_GREEN  = (34,  139, 34)
DARK_GRASS   = (20,  90,  20)
SKY_BLUE     = (100, 180, 240)
HORIZON_BLUE = (150, 210, 240)
ASPHALT      = (55,  55,  60)
LINE_WHITE   = (230, 230, 230)
NEON_CYAN    = (0,   240, 255)
NEON_PINK    = (255, 20,  147)
GOLD         = (255, 200, 0)
SILVER       = (192, 192, 192)
BRONZE       = (205, 127, 50)

# Road geometry (3D pseudo perspective)
ROAD_WIDTH_TOP    = 160   # road width at horizon
ROAD_WIDTH_BOTTOM = 560   # road width at player bottom
HORIZON_Y         = 280   # y-position of the horizon line
VANISH_X          = SCREEN_WIDTH // 2  # vanishing point X

# Player car
PLAYER_START_X   = SCREEN_WIDTH // 2
PLAYER_START_Y   = SCREEN_HEIGHT - 130
PLAYER_CAR_W     = 60
PLAYER_CAR_H     = 100
PLAYER_SPEED     = 5
PLAYER_ACCEL     = 0.3
PLAYER_BRAKE     = 0.5
PLAYER_MAX_SPEED = 12
PLAYER_LATERAL   = 5      # side movement speed

# Difficulty settings  {name: (enemy_speed, spawn_rate, road_curves)}
DIFFICULTIES = {
    "EASY":   {"enemy_speed": 4,  "spawn_interval": 90,  "curve_strength": 0.5, "score_mult": 1},
    "MEDIUM": {"enemy_speed": 7,  "spawn_interval": 60,  "curve_strength": 1.0, "score_mult": 2},
    "HARD":   {"enemy_speed": 11, "spawn_interval": 40,  "curve_strength": 1.5, "score_mult": 3},
}

# Enemy cars
ENEMY_CAR_W = 55
ENEMY_CAR_H = 90
ENEMY_COLORS = [
    (220, 50,  50),
    (50,  50,  220),
    (50,  180, 50),
    (200, 200, 50),
    (180, 50,  180),
    (50,  200, 200),
    (255, 140, 0),
]

# Scenery
NUM_TREES    = 10   # trees visible on each side
NUM_CLOUDS   = 6

# Game states
STATE_MENU        = "menu"
STATE_DIFFICULTY  = "difficulty"
STATE_PLAYING     = "playing"
STATE_PAUSED      = "paused"
STATE_GAME_OVER   = "game_over"
STATE_HIGH_SCORES = "high_scores"

# Scoring
SCORE_PER_FRAME    = 1
SCORE_OVERTAKE     = 50   # bonus for passing an enemy

# High score file
HIGH_SCORE_FILE = "highscores.json"
