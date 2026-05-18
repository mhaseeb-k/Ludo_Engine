import pygame
import sys
import random
import time

pygame.init()

from gui.constants import *
from gui.renderer import draw_board, draw_piece, draw_dice, draw_dice_queue, draw_popup_menu, draw_leaderboard, draw_roll_prompt_dice
from gui.board_layout import get_pixel_position, get_dice_rect
from gui.animations import AnimationManager, get_pulse_scale, is_dice_blink_on
from gui.setup_menu import run_setup_menu
from backend_bridge import LudoBridge

def main():
    idleValue = random.randint(1, 5)
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Modern Ludo")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont('Arial', 24, bold=True)

    players, modes = run_setup_menu(screen)
    if not players:
        pygame.quit()
        sys.exit()

    bridge = LudoBridge()
    bridge.init_game(players, modes)
    
    anim_manager = AnimationManager()
    
    # Game State Variables
    current_turn = bridge.get_current_turn()
    turn_phase = 'idle' # 'idle', 'rolling', 'moving', 'game_over'
    dice_queue = []
    dice_roll_start_time = 0
    ai_timer_start = 0
    bonus_roll_earned = False
    
    leaderboard = []
    
    ds = 50
    dice_rects = {p: get_dice_rect(p, ds) for p in players}
    
    popup_rects = []
    selected_piece_id = None
    
    def check_finished_and_next():
        nonlocal current_turn, turn_phase, dice_queue, ai_timer_start, selected_piece_id, bonus_roll_earned
        selected_piece_id = None
        
        if current_turn not in leaderboard and bridge.is_player_finished(current_turn):
            leaderboard.append(current_turn)
            
        active_players = [p for p in players if p not in leaderboard]
        if len(active_players) <= 1:
            if active_players:
                leaderboard.append(active_players[0])
            turn_phase = 'game_over'
            return
            
        if bonus_roll_earned:
            bonus_roll_earned = False
            dice_queue = []
            turn_phase = 'idle'
            ai_timer_start = pygame.time.get_ticks()
            return
            
        bridge.next_turn()
        current_turn = bridge.get_current_turn()
        dice_queue = []
        turn_phase = 'idle'
        ai_timer_start = pygame.time.get_ticks()

    def has_any_valid_moves():
        for d in set(dice_queue):
            if bridge.get_valid_moves(d):
                return True
        return False

    def execute_move(pid, used_dice, new_pos):
        nonlocal selected_piece_id, bonus_roll_earned
        selected_piece_id = None
        positions = bridge.get_all_piece_positions().get(current_turn, {})
        pos_str = positions.get(pid)
        start_pos = get_pixel_position(pos_str, current_turn, pid)
        end_pos = get_pixel_position(new_pos, current_turn, pid)
        anim_manager.add_glide(current_turn, pid, start_pos, end_pos, ANIMATION_FRAMES)
        bonus = bridge.execute_move(current_turn, pid, new_pos)
        if bonus:
            bonus_roll_earned = True
        dice_queue.remove(used_dice)

    running = True
    while running:
        current_time = pygame.time.get_ticks()
        is_ai_turn = bridge.get_player_mode(current_turn) == 'ai'
        
        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            if event.type == pygame.MOUSEBUTTONDOWN and not anim_manager.is_animating() and not is_ai_turn and turn_phase != 'game_over':
                mx, my = pygame.mouse.get_pos()
                
                if turn_phase == 'idle':
                    current_dice_rect = dice_rects[current_turn]
                    if current_dice_rect.collidepoint(mx, my):
                        turn_phase = 'rolling'
                        dice_roll_start_time = current_time
                
                elif turn_phase == 'moving':
                    # Check popup clicks
                    if selected_piece_id and popup_rects:
                        clicked_popup = False
                        for rect, opt_dice in popup_rects:
                            if rect.collidepoint(mx, my):
                                clicked_popup = True
                                # Find new_pos for this dice and piece
                                moves = bridge.get_valid_moves(opt_dice)
                                for m in moves:
                                    if m['piece_id'] == selected_piece_id:
                                        execute_move(selected_piece_id, opt_dice, m['new_pos'])
                                        break
                                break
                        if clicked_popup:
                            popup_rects = []
                            continue
                        else:
                            # click outside popup dismisses it
                            selected_piece_id = None
                            popup_rects = []
                            continue
                    
                    # Check piece clicks
                    if not selected_piece_id:
                        positions = bridge.get_all_piece_positions().get(current_turn, {})
                        for pid, pos_str in positions.items():
                            px, py = get_pixel_position(pos_str, current_turn, pid)
                            if (mx - px)**2 + (my - py)**2 < (CELL_SIZE//2)**2:
                                # User clicked this piece. Find valid dice options
                                valid_options = []
                                for d in set(dice_queue):
                                    moves = bridge.get_valid_moves(d)
                                    for m in moves:
                                        if m['piece_id'] == pid:
                                            valid_options.append((d, m['new_pos']))
                                
                                if len(valid_options) == 1:
                                    d, new_pos = valid_options[0]
                                    execute_move(pid, d, new_pos)
                                elif len(valid_options) > 1:
                                    selected_piece_id = pid
                                break

        # --- AI Handling ---
        if is_ai_turn and not anim_manager.is_animating() and turn_phase != 'game_over':
            if turn_phase == 'idle':
                if current_time - ai_timer_start > 800:
                    turn_phase = 'rolling'
                    dice_roll_start_time = current_time
            
            elif turn_phase == 'moving':
                if current_time - ai_timer_start > 1000: # Wait 1s between moves
                    if dice_queue:
                        best_dice, best_pid = bridge.choose_best_move_from_list(current_turn, dice_queue)
                        if best_pid:
                            moves = bridge.get_valid_moves(best_dice)
                            for m in moves:
                                if m['piece_id'] == best_pid:
                                    execute_move(best_pid, best_dice, m['new_pos'])
                                    break
                            ai_timer_start = current_time
                        else:
                            # No valid moves for any dice
                            dice_queue.clear()
                            
        # --- Phase Logic Updates ---
        if turn_phase == 'rolling':
            if current_time - dice_roll_start_time > 600: # 600ms spin animation
                val = random.randint(1, 6)  # uniform 1–6 from OS entropy
                dice_queue.append(val)
                
                if val == 6:
                    if dice_queue.count(6) == 3:
                        dice_queue.clear()
                        check_finished_and_next()
                    else:
                        turn_phase = 'idle' # Wait for next roll click or AI delay
                        ai_timer_start = current_time
                else:
                    turn_phase = 'moving'
                    ai_timer_start = current_time

        if turn_phase == 'moving' and not anim_manager.is_animating():
            if not dice_queue or not has_any_valid_moves():
                if dice_queue:
                    idleValue = dice_queue[0] # Use the last dice value as the idle value
                dice_queue.clear()
                check_finished_and_next()

        anim_manager.update()

        # --- Rendering ---
        draw_board(screen, current_turn)
        
        # Draw Pieces
        all_positions = bridge.get_all_piece_positions()
        
        for color, pieces in all_positions.items():
            for pid, pos_str in pieces.items():
                override = anim_manager.get_piece_override(color, pid)
                if override:
                    px, py = override
                else:
                    px, py = get_pixel_position(pos_str, color, pid)
                
                pulse = 1.0
                if color == current_turn and turn_phase == 'moving' and not anim_manager.is_animating():
                    # Check if this piece has any valid moves
                    can_move = False
                    for d in set(dice_queue):
                        moves = bridge.get_valid_moves(d)
                        if any(m['piece_id'] == pid for m in moves):
                            can_move = True
                            break
                    if can_move:
                        pulse = get_pulse_scale()
                    
                draw_piece(screen, px, py, color, pulse)

        # Draw Dice Queue and Active Dice
        for p in players:
            d_rect = dice_rects[p]
            if p == current_turn:
                if turn_phase == 'rolling':
                    draw_dice(screen, None, d_rect.x, d_rect.y, size=ds, spinning=True)
                else:
                    # Draw a placeholder "roll" button if idle
                    if turn_phase == 'idle':
                        draw_roll_prompt_dice(screen, d_rect, p, is_dice_blink_on(current_time))
                
                # Draw the queue
                if dice_queue:
                    draw_dice_queue(screen, dice_queue, d_rect.x + ds + 20, d_rect.y, size=40)
            else:
                draw_dice(screen, idleValue, d_rect.x, d_rect.y, size=ds, spinning=False)

        # Draw Popup
        if turn_phase == 'moving' and selected_piece_id:
            pos_str = all_positions.get(current_turn, {}).get(selected_piece_id)
            if pos_str:
                px, py = get_pixel_position(pos_str, current_turn, selected_piece_id)
                valid_options = []
                for d in set(dice_queue):
                    moves = bridge.get_valid_moves(d)
                    if any(m['piece_id'] == selected_piece_id for m in moves):
                        valid_options.append(d)
                
                if valid_options:
                    popup_rects = draw_popup_menu(screen, font, valid_options, px + 20, py - 20)

        # Draw Game Over Leaderboard
        if turn_phase == 'game_over':
            draw_leaderboard(screen, font, leaderboard)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
