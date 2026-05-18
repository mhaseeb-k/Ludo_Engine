# Colors (Modern Pastel/Neon)
RED = (255, 51, 102)     # #FF3366 (Ruby / Crimson)
GREEN = (46, 204, 113)   # #2ECC71 (Emerald / Mint)
YELLOW = (241, 196, 15)  # #F1C40F (Amber / Gold)
BLUE = (52, 152, 219)    # #3498DB (Electric / Sapphire)

BG_COLOR = (30, 30, 36)  # #1E1E24 (Deep charcoal)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
LIGHT_GRAY = (200, 200, 200)

# Board Dimensions
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 800
BOARD_SIZE = min(WINDOW_WIDTH, WINDOW_HEIGHT) - 100
CELL_SIZE = BOARD_SIZE // 15
OFFSET_X = (WINDOW_WIDTH - BOARD_SIZE) // 2
OFFSET_Y = (WINDOW_HEIGHT - BOARD_SIZE) // 2

# Game Constants
FPS = 60
ANIMATION_FRAMES = 15 # Frames for a piece to move one tile

COLOR_MAP = {
    'red': RED,
    'green': GREEN,
    'yellow': YELLOW,
    'blue': BLUE
}
