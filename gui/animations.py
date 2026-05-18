import time
import math

class AnimationManager:
    def __init__(self):
        self.animations = []

    def add_glide(self, color, piece_id, start_pos, end_pos, frames):
        """
        Adds a translation animation.
        start_pos and end_pos are (x, y) pixel coordinates.
        """
        self.animations.append({
            'type': 'glide',
            'color': color,
            'piece_id': piece_id,
            'start': start_pos,
            'end': end_pos,
            'current_frame': 0,
            'total_frames': frames,
            'done': False
        })

    def update(self):
        for anim in self.animations:
            if anim['current_frame'] < anim['total_frames']:
                anim['current_frame'] += 1
            else:
                anim['done'] = True
        
        self.animations = [a for a in self.animations if not a['done']]

    def is_animating(self):
        return len(self.animations) > 0

    def get_piece_override(self, color, piece_id):
        """
        Returns the interpolated (x, y) if the piece is animating, else None.
        """
        for anim in self.animations:
            if anim['color'] == color and anim['piece_id'] == piece_id and anim['type'] == 'glide':
                raw_t = anim['current_frame'] / anim['total_frames']
                # Ease-out cubic for X and base Y
                t = 1 - pow(1 - raw_t, 3)
                
                # Sine arc for bouncing effect (peaks in the middle of the animation)
                bounce_offset = math.sin(raw_t * math.pi) * 25
                
                sx, sy = anim['start']
                ex, ey = anim['end']
                
                curr_x = sx + (ex - sx) * t
                curr_y = sy + (ey - sy) * t - bounce_offset
                
                return (curr_x, curr_y)
        return None

def get_pulse_scale():
    """Returns a scale factor oscillating between 1.0 and 1.2 based on time."""
    return 1.0 + 0.15 * (math.sin(time.time() * 8) + 1) / 2

DICE_BLINK_PERIOD_MS = 400

def is_dice_blink_on(current_time_ms):
    """Sharp on/off phase for idle roll dice (400ms each)."""
    period = DICE_BLINK_PERIOD_MS
    return (current_time_ms % (period * 2)) < period
