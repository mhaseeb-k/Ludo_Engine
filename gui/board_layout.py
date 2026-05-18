import pygame

from .constants import CELL_SIZE, OFFSET_X, OFFSET_Y

# Logical coordinates (grid 0-14)
# 52 main tiles
MAIN_TRACK_COORDS = [
    (8,1), (8,2), (8,3), (8,4), (8,5),
    (9,6), (10,6), (11,6), (12,6), (13,6), (14,6),
    (14,7),
    (14,8), (13,8), (12,8), (11,8), (10,8), (9,8),
    (8,9), (8,10), (8,11), (8,12), (8,13), (8,14),
    (7,14),
    (6,14), (6,13), (6,12), (6,11), (6,10), (6,9),
    (5,8), (4,8), (3,8), (2,8), (1,8), (0,8),
    (0,7),
    (0,6), (1,6), (2,6), (3,6), (4,6), (5,6),
    (6,5), (6,4), (6,3), (6,2), (6,1), (6,0),
    (7,0),
    (8,0)
]

STRETCHES = {
    'red': [(7,1), (7,2), (7,3), (7,4), (7,5)],
    'green': [(13,7), (12,7), (11,7), (10,7), (9,7)],
    'yellow': [(7,13), (7,12), (7,11), (7,10), (7,9)],
    'blue': [(1,7), (2,7), (3,7), (4,7), (5,7)]
}

# Home base layout: 6x6 colored box per player; dice sits at center, tokens in corners.
BASE_ORIGINS = {
    'blue': (0, 0),
    'red': (9, 0),
    'yellow': (0, 9),
    'green': (9, 9),
}
# Fractional cell centers — pushed to inner corners so they never overlap center dice.
BASE_PIECE_LOCAL = [
    (0.85, 0.85),
    (0.85, 4.15),
    (4.15, 0.85),
    (4.15, 4.15),
]
DICE_LOCAL_CENTER = (2.5, 2.5)

def coord_to_pixel(cx, cy):
    """Convert fractional board coordinate to pixel center (cell n → center n+0.5)."""
    px = OFFSET_X + cx * CELL_SIZE
    py = OFFSET_Y + cy * CELL_SIZE
    return int(px), int(py)

def grid_to_pixel(gx, gy):
    """Convert integer grid cell index to center pixel coordinate."""
    return coord_to_pixel(gx + 0.5, gy + 0.5)

def get_dice_rect(color, size):
    """Pixel rect for a player's roll dice, centered in their home base."""
    ox, oy = BASE_ORIGINS[color]
    lx, ly = DICE_LOCAL_CENTER
    px, py = coord_to_pixel(ox + lx, oy + ly)
    return pygame.Rect(px - size // 2, py - size // 2, size, size)

def get_pixel_position(pos_str, color=None, piece_id=1):
    """
    Parses a Prolog position string (e.g. 'tile(5)', 'base(red)', 'stretch(red, 1)')
    and returns pixel (x, y)
    """
    if pos_str.startswith('tile('):
        n = int(pos_str[5:-1])
        # Prolog tiles are 1-indexed, Python list is 0-indexed
        gx, gy = MAIN_TRACK_COORDS[n - 1]
        return grid_to_pixel(gx, gy)
        
    elif pos_str.startswith('stretch('):
        # Format: stretch(color, n)
        parts = pos_str[8:-1].split(',')
        c = parts[0].strip()
        n = int(parts[1].strip())
        gx, gy = STRETCHES[c][n - 1]
        return grid_to_pixel(gx, gy)
        
    elif pos_str.startswith('base('):
        c = pos_str[5:-1]
        ox, oy = BASE_ORIGINS[c]
        lx, ly = BASE_PIECE_LOCAL[piece_id - 1]
        return coord_to_pixel(ox + lx, oy + ly)
        
    elif pos_str.startswith('finish('):
        # Center triangle
        # Can add small offsets based on color so they don't completely overlap
        gx, gy = 7, 7
        px, py = grid_to_pixel(gx, gy)
        offsets = {
            'red': (0, -10),
            'green': (10, 0),
            'yellow': (0, 10),
            'blue': (-10, 0)
        }
        ox, oy = offsets.get(color, (0,0))
        return px + ox, py + oy

    return 0, 0
