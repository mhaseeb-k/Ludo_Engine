import pygame
import math
import time
from .constants import *
from .board_layout import MAIN_TRACK_COORDS, STRETCHES, grid_to_pixel

# Safe zone indices (1-indexed based on Prolog, converted to 0-indexed coords index)
SAFE_ZONES = [1, 9, 14, 22, 27, 35, 40, 48]

def draw_star(surface, color, x, y, size):
    """Draws a simple 5-pointed star"""
    points = []
    for i in range(10):
        angle = i * math.pi / 5 - math.pi / 2
        radius = size if i % 2 == 0 else size / 2
        points.append((x + math.cos(angle) * radius, y + math.sin(angle) * radius))
    pygame.draw.polygon(surface, color, points)

def draw_board(surface, active_color=None):
    surface.fill(BG_COLOR)
    
    # Draw bases
    base_size = CELL_SIZE * 6
    
    # Calculate pulse thickness for active base
    pulse_width = int(3 + 3 * (math.sin(time.time() * 6) + 1) / 2)
    
    # Blue Base (Top Left)
    bx, by = OFFSET_X, OFFSET_Y
    pygame.draw.rect(surface, BLUE, (bx, by, base_size, base_size), border_radius=20)
    pygame.draw.rect(surface, WHITE, (bx+20, by+20, base_size-40, base_size-40), border_radius=15)
    if active_color == 'blue':
        pygame.draw.rect(surface, WHITE, (bx, by, base_size, base_size), width=pulse_width, border_radius=20)
        
    # Red Base (Top Right)
    rx, ry = OFFSET_X + 9 * CELL_SIZE, OFFSET_Y
    pygame.draw.rect(surface, RED, (rx, ry, base_size, base_size), border_radius=20)
    pygame.draw.rect(surface, WHITE, (rx+20, ry+20, base_size-40, base_size-40), border_radius=15)
    if active_color == 'red':
        pygame.draw.rect(surface, WHITE, (rx, ry, base_size, base_size), width=pulse_width, border_radius=20)

    # Yellow Base (Bottom Left)
    yx, yy = OFFSET_X, OFFSET_Y + 9 * CELL_SIZE
    pygame.draw.rect(surface, YELLOW, (yx, yy, base_size, base_size), border_radius=20)
    pygame.draw.rect(surface, WHITE, (yx+20, yy+20, base_size-40, base_size-40), border_radius=15)
    if active_color == 'yellow':
        pygame.draw.rect(surface, WHITE, (yx, yy, base_size, base_size), width=pulse_width, border_radius=20)

    # Green Base (Bottom Right)
    gx, gy = OFFSET_X + 9 * CELL_SIZE, OFFSET_Y + 9 * CELL_SIZE
    pygame.draw.rect(surface, GREEN, (gx, gy, base_size, base_size), border_radius=20)
    pygame.draw.rect(surface, WHITE, (gx+20, gy+20, base_size-40, base_size-40), border_radius=15)
    if active_color == 'green':
        pygame.draw.rect(surface, WHITE, (gx, gy, base_size, base_size), width=pulse_width, border_radius=20)

    # Draw Center Finish
    cx, cy = grid_to_pixel(7, 7)
    cx -= CELL_SIZE//2
    cy -= CELL_SIZE//2
    # Triangles
    pygame.draw.polygon(surface, RED, [(cx, cy), (cx+CELL_SIZE, cy), (cx+CELL_SIZE//2, cy+CELL_SIZE//2)])
    pygame.draw.polygon(surface, GREEN, [(cx+CELL_SIZE, cy), (cx+CELL_SIZE, cy+CELL_SIZE), (cx+CELL_SIZE//2, cy+CELL_SIZE//2)])
    pygame.draw.polygon(surface, YELLOW, [(cx, cy+CELL_SIZE), (cx+CELL_SIZE, cy+CELL_SIZE), (cx+CELL_SIZE//2, cy+CELL_SIZE//2)])
    pygame.draw.polygon(surface, BLUE, [(cx, cy), (cx, cy+CELL_SIZE), (cx+CELL_SIZE//2, cy+CELL_SIZE//2)])

    # Draw Main Track
    for i, (gx, gy) in enumerate(MAIN_TRACK_COORDS):
        px = OFFSET_X + gx * CELL_SIZE
        py = OFFSET_Y + gy * CELL_SIZE
        
        # Determine cell color based on start tiles
        cell_color = WHITE
        if i + 1 == 1: cell_color = RED
        elif i + 1 == 14: cell_color = GREEN
        elif i + 1 == 27: cell_color = YELLOW
        elif i + 1 == 40: cell_color = BLUE
            
        pygame.draw.rect(surface, cell_color, (px, py, CELL_SIZE, CELL_SIZE))
        pygame.draw.rect(surface, GRAY, (px, py, CELL_SIZE, CELL_SIZE), 1)
        
        # Draw Safe Zone Icons
        if i + 1 in SAFE_ZONES:
            draw_star(surface, LIGHT_GRAY, px + CELL_SIZE//2, py + CELL_SIZE//2, CELL_SIZE//3)

    # Draw Stretches
    for color_name, stretch_coords in STRETCHES.items():
        c = COLOR_MAP[color_name]
        for gx, gy in stretch_coords:
            px = OFFSET_X + gx * CELL_SIZE
            py = OFFSET_Y + gy * CELL_SIZE
            pygame.draw.rect(surface, c, (px, py, CELL_SIZE, CELL_SIZE))
            pygame.draw.rect(surface, GRAY, (px, py, CELL_SIZE, CELL_SIZE), 1)

def draw_piece(surface, x, y, color, pulse_scale=1.0):
    """Draws a single token, with optional pulsing effect"""
    radius = int((CELL_SIZE // 2 - 4) * pulse_scale)
    # Darker outline
    pygame.draw.circle(surface, BLACK, (int(x), int(y)), radius + 2)
    # Main body
    pygame.draw.circle(surface, COLOR_MAP[color], (int(x), int(y)), radius)
    # Highlight for 3D effect
    pygame.draw.circle(surface, WHITE, (int(x) - radius//3, int(y) - radius//3), radius//4)

def draw_dice(surface, value, x, y, size=60, spinning=False, face_color=None, border_color=None, border_width=2, prompt_char_color=None):
    """Draws a modern dice with a simple 3D extrusion effect. If spinning, draws a blurred version."""
    face_color = face_color if face_color is not None else WHITE
    border_color = border_color if border_color is not None else GRAY

    # Draw 3D shadow/extrusion
    depth = size // 10
    shadow_rect = pygame.Rect(x + depth, y + depth, size, size)
    pygame.draw.rect(surface, (200, 200, 200), shadow_rect, border_radius=10)
    
    # Draw main face
    rect = pygame.Rect(x, y, size, size)
    pygame.draw.rect(surface, face_color, rect, border_radius=10)
    pygame.draw.rect(surface, border_color, rect, width=border_width, border_radius=10)
    
    if spinning:
        # Just draw some random dots to simulate blur
        import random
        for _ in range(3):
            dx = x + random.randint(10, size-10)
            dy = y + random.randint(10, size-10)
            pygame.draw.circle(surface, BLACK, (dx, dy), size//10)
        return

    if not value:
        font = pygame.font.SysFont('Arial', size // 2, bold=True)
        text = font.render('?', True, prompt_char_color or BLACK)
        text_rect = text.get_rect(center=(x + size//2, y + size//2))
        surface.blit(text, text_rect)
        return
        
    dot_size = size // 10
    c = size // 2
    q1 = size // 4
    q3 = size * 3 // 4
    
    dots = []
    if value in [1, 3, 5]: dots.append((c, c))
    if value in [2, 3, 4, 5, 6]: 
        dots.extend([(q1, q1), (q3, q3)])
    if value in [4, 5, 6]:
        dots.extend([(q1, q3), (q3, q1)])
    if value == 6:
        dots.extend([(q1, c), (q3, c)])
        
    for dx, dy in dots:
        pygame.draw.circle(surface, BLACK, (x + dx, y + dy), dot_size)

def draw_roll_prompt_dice(surface, rect, player_color, blink_on):
    """High-contrast idle roll prompt — sharp alternate between player color and bright glow."""
    x, y, size = rect.x, rect.y, rect.width
    player = COLOR_MAP[player_color]

    if blink_on:
        outer = rect.inflate(18, 18)
        pygame.draw.rect(surface, (255, 255, 0), outer, border_radius=16)
        pygame.draw.rect(surface, WHITE, outer, width=5, border_radius=16)
        draw_dice(
            surface, 0, x, y, size=size,
            face_color=WHITE, border_color=(255, 200, 0), border_width=5,
            prompt_char_color=(255, 140, 0),
        )
    else:
        outer = rect.inflate(14, 14)
        pygame.draw.rect(surface, player, outer, border_radius=14)
        pygame.draw.rect(surface, WHITE, outer, width=4, border_radius=14)
        dim_face = tuple(max(0, c - 30) for c in player)
        draw_dice(
            surface, 0, x, y, size=size,
            face_color=dim_face, border_color=WHITE, border_width=4,
            prompt_char_color=WHITE,
        )

def draw_dice_queue(surface, queue, x, y, size=40):
    """Draws multiple dice in a row for the queue"""
    for i, val in enumerate(queue):
        draw_dice(surface, val, x + i * (size + 10), y, size=size, spinning=False)

def draw_popup_menu(surface, font, options, x, y):
    """
    Draws a popup menu and returns a list of (rect, option_value) tuples.
    options is a list of valid dice values to choose from.
    """
    padding = 10
    item_height = 30
    width = 120
    height = len(options) * item_height + padding * 2
    
    # Keep on screen
    if x + width > surface.get_width():
        x = surface.get_width() - width
    if y + height > surface.get_height():
        y = surface.get_height() - height

    rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(surface, WHITE, rect, border_radius=8)
    pygame.draw.rect(surface, BLACK, rect, width=2, border_radius=8)
    
    click_rects = []
    
    # Title
    title = font.render("Choose Dice:", True, GRAY)
    surface.blit(title, (x + padding, y + 5))
    
    cy = y + padding + 20
    for opt in options:
        item_rect = pygame.Rect(x + padding, cy, width - 2*padding, item_height - 5)
        pygame.draw.rect(surface, LIGHT_GRAY, item_rect, border_radius=4)
        
        text = font.render(f"Dice {opt}", True, BLACK)
        text_rect = text.get_rect(center=item_rect.center)
        surface.blit(text, text_rect)
        
        click_rects.append((item_rect, opt))
        cy += item_height
        
    return click_rects

def draw_leaderboard(surface, font, leaderboard):
    """Draws the final game over screen with ranks"""
    overlay = pygame.Surface((surface.get_width(), surface.get_height()), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    surface.blit(overlay, (0, 0))
    
    width, height = 400, 300
    x = (surface.get_width() - width) // 2
    y = (surface.get_height() - height) // 2
    
    rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(surface, WHITE, rect, border_radius=15)
    pygame.draw.rect(surface, (255, 215, 0), rect, width=4, border_radius=15) # Gold
    
    title = font.render("Game Over! Rankings:", True, BLACK)
    surface.blit(title, (x + width//2 - title.get_width()//2, y + 20))
    
    cy = y + 70
    ranks = ["1st", "2nd", "3rd", "4th"]
    
    for i, p in enumerate(leaderboard):
        if i < len(ranks):
            rank_text = f"{ranks[i]}: {p.upper()}"
            color = COLOR_MAP.get(p, BLACK)
            text = font.render(rank_text, True, color)
            
            shadow = font.render(rank_text, True, GRAY)
            surface.blit(shadow, (x + width//2 - shadow.get_width()//2 + 2, cy + 2))
            surface.blit(text, (x + width//2 - text.get_width()//2, cy))
            cy += 40

