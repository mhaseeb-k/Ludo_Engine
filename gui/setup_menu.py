import pygame
from .constants import *

def run_setup_menu(screen):
    """
    Displays a simple menu to choose players.
    Returns: players (list of colors), modes (list of 'human'/'ai')
    """
    font = pygame.font.SysFont(None, 48)
    small_font = pygame.font.SysFont(None, 36)
    
    selected_option = 0
    options = [
        ("2 Players (Red vs Green)", ['red', 'green'], ['human', 'human']),
        ("3 Players (Red vs Green vs Yellow)", ['red', 'green', 'yellow'], ['human', 'human', 'human']),
        ("4 Players (All)", ['red', 'green', 'yellow', 'blue'], ['human', 'human', 'human', 'human']),
        ("1v1 (Human vs AI)", ['red', 'green'], ['human', 'ai']),
    ]
    
    clock = pygame.time.Clock()
    
    while True:
        screen.fill(BG_COLOR)
        
        # Title
        title = font.render("LUDO - MODERN", True, WHITE)
        screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 100))
        
        # Options
        for i, (text, _, _) in enumerate(options):
            color = GREEN if i == selected_option else GRAY
            text_surf = small_font.render(text, True, color)
            screen.blit(text_surf, (WINDOW_WIDTH//2 - text_surf.get_width()//2, 250 + i * 60))
            
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None, None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_option = (selected_option - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    return options[selected_option][1], options[selected_option][2]
                    
        clock.tick(30)
