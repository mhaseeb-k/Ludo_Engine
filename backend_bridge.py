from pyswip import Prolog

class LudoBridge:
    def __init__(self, prolog_file="ludo.pl"):
        self.prolog = Prolog()
        self.prolog.consult(prolog_file)
        
    def init_game(self, players, modes):
        """
        Initializes the game. 
        players: list of strings e.g. ['red', 'green']
        modes: list of strings e.g. ['human', 'ai']
        """
        # Convert Python lists to Prolog lists syntax
        p_str = "[" + ",".join(players) + "]"
        m_str = "[" + ",".join(modes) + "]"
        list(self.prolog.query(f"init_game({p_str}, {m_str})"))
        
    def roll_dice(self, value):
        list(self.prolog.query("retractall(current_dice(_))"))
        list(self.prolog.query(f"assertz(current_dice({value}))"))

    def get_current_turn(self):
        res = list(self.prolog.query("current_turn(Color)"))
        if res:
            return res[0]['Color']
        return None

    def get_player_mode(self, color):
        res = list(self.prolog.query(f"player_state({color}, Mode)"))
        if res:
            return res[0]['Mode']
        return None

    def get_valid_moves(self, dice_value):
        """Returns a list of dicts: [{'piece_id': 1, 'new_pos': 'tile(5)'}, ...]"""
        res = list(self.prolog.query(f"valid_moves_for_current_player({dice_value}, Moves)"))
        parsed_moves = []
        if res and res[0]['Moves']:
            for move in res[0]['Moves']:
                piece_id = move[0]
                # pyswip returns atoms/functors as strings or objects. We need to parse safely.
                new_pos = str(move[1])
                parsed_moves.append({'piece_id': piece_id, 'new_pos': new_pos})
        return parsed_moves

    def execute_move(self, color, piece_id, new_pos_str):
        # We need to ensure new_pos_str is exactly what Prolog expects (e.g. tile(5) or stretch(red,1))
        # It's safer to pass it exactly as the string we got
        query = f"execute_move({color}, {piece_id}, {new_pos_str}, BonusFlag)"
        res = list(self.prolog.query(query))
        if res:
            return str(res[0]['BonusFlag']) == 'true'
        return False

    def next_turn(self):
        list(self.prolog.query("next_turn"))

    def get_all_piece_positions(self):
        """
        Returns a dictionary:
        {
            'red': {1: 'base(red)', 2: 'tile(5)', ...},
            'green': {...}
        }
        """
        res = list(self.prolog.query("piece_position(Color, ID, Pos)"))
        positions = {}
        for r in res:
            c = str(r['Color'])
            pid = int(r['ID'])
            pos = str(r['Pos'])
            
            if c not in positions:
                positions[c] = {}
            positions[c][pid] = pos
            
        return positions

    def choose_best_move(self, color, dice_value):
        res = list(self.prolog.query(f"choose_best_move({color}, {dice_value}, PieceID)"))
        if res:
            return res[0]['PieceID']
        return None

    def choose_best_move_from_list(self, color, dice_list):
        """
        Returns a tuple: (best_dice_value, piece_id)
        """
        d_str = "[" + ",".join(map(str, dice_list)) + "]"
        res = list(self.prolog.query(f"choose_best_move_from_list({color}, {d_str}, BestDice, PieceID)"))
        if res:
            return res[0]['BestDice'], res[0]['PieceID']
        return None, None

    def is_player_finished(self, color):
        res = list(self.prolog.query(f"player_finished({color})"))
        return len(res) > 0

