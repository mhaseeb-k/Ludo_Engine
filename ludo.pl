% --- Dynamic State Trackers ---
:- dynamic player_state/2.      % player_state(Color, Type) -> Type = human/ai
:- dynamic piece_position/3.    % piece_position(Color, PieceID, Pos)
:- dynamic current_turn/1.      % current_turn(Color)
:- dynamic current_dice/1.      % current_dice(Value)
:- dynamic players_list/1.      % players_list([red, green, ...])

% Colors
color(red). color(green). color(yellow). color(blue).

% Safe Zones
safe_zone(tile(1)). safe_zone(tile(9)). safe_zone(tile(14)). safe_zone(tile(22)).
safe_zone(tile(27)). safe_zone(tile(35)). safe_zone(tile(40)). safe_zone(tile(48)).

% Start Tiles
start_tile(red, 1).
start_tile(green, 14).
start_tile(yellow, 27).
start_tile(blue, 40).

% End Tiles (Main Track)
end_tile(red, 51).
end_tile(green, 12).
end_tile(yellow, 25).
end_tile(blue, 38).

% --- Initialization ---
init_game(Players, Modes) :-
    retractall(player_state(_, _)),
    retractall(piece_position(_, _, _)),
    retractall(current_turn(_)),
    retractall(current_dice(_)),
    retractall(players_list(_)),
    
    assertz(players_list(Players)),
    setup_players(Players, Modes),
    [FirstPlayer|_] = Players,
    assertz(current_turn(FirstPlayer)).

setup_players([], []).
setup_players([Color|Cs], [Mode|Ms]) :-
    assertz(player_state(Color, Mode)),
    assertz(piece_position(Color, 1, base(Color))),
    assertz(piece_position(Color, 2, base(Color))),
    assertz(piece_position(Color, 3, base(Color))),
    assertz(piece_position(Color, 4, base(Color))),
    setup_players(Cs, Ms).

% --- Movement Logic ---

% Getting the next tile sequence on the main track
next_main_tile(52, 1) :- !.
next_main_tile(N, M) :- M is N + 1.

% Step function: piece_step(+Color, +CurrentPos, -NextPos)
piece_step(Color, base(Color), tile(Start)) :-
    start_tile(Color, Start).
    
piece_step(Color, tile(End), stretch(Color, 1)) :-
    end_tile(Color, End).

piece_step(_, tile(N), tile(M)) :-
    next_main_tile(N, M).

piece_step(Color, stretch(Color, N), stretch(Color, M)) :-
    N < 5, M is N + 1.

piece_step(Color, stretch(Color, 5), finish(Color)).

% Calculate path over multiple steps
% step_n(+Color, +Pos, +Steps, -FinalPos)
step_n(_, Pos, 0, Pos) :- !.
step_n(Color, Pos, Steps, FinalPos) :-
    Steps > 0,
    piece_step(Color, Pos, NextPos),
    NextSteps is Steps - 1,
    step_n(Color, NextPos, NextSteps, FinalPos).

% --- Validation Rules ---
% valid_move(+Color, +PieceID, +DiceValue, -NewPos)

% Rule: Spawn from base needs a 6. Moves to start tile.
valid_move(Color, PieceID, 6, tile(Start)) :-
    piece_position(Color, PieceID, base(Color)),
    start_tile(Color, Start).

% Rule: Move from non-base
valid_move(Color, PieceID, DiceValue, NewPos) :-
    piece_position(Color, PieceID, CurrentPos),
    CurrentPos \= base(Color),
    CurrentPos \= finish(Color),
    step_n(Color, CurrentPos, DiceValue, NewPos).

% Helper to get all valid moves for current player
valid_moves_for_current_player(Dice, Moves) :-
    current_turn(Color),
    findall([PieceID, NewPos], valid_move(Color, PieceID, Dice, NewPos), Moves).

% --- Execution and Capturing ---

% execute_move(+Color, +PieceID, +NewPos, -BonusFlag)
execute_move(Color, PieceID, NewPos, BonusFlag) :-
    retract(piece_position(Color, PieceID, _)),
    assertz(piece_position(Color, PieceID, NewPos)),
    check_capture(Color, NewPos, CaptureStatus),
    (
        (CaptureStatus == captured ; NewPos == finish(Color)) -> BonusFlag = true
    ;
        BonusFlag = false
    ).

% Capture opponent piece if landing on non-safe zone
check_capture(Color, tile(N), captured) :-
    \+ safe_zone(tile(N)),
    piece_position(OppColor, _, tile(N)),
    OppColor \= Color,
    !, % We found a capture!
    % Retract all opponents on this tile and send to base
    findall(OppPieceID, (piece_position(OppColor, OppPieceID, tile(N))), IDs),
    retractall(piece_position(OppColor, _, tile(N))),
    % Re-assert them in base
    forall(member(ID, IDs), assertz(piece_position(OppColor, ID, base(OppColor)))).

check_capture(_, _, none).

% --- Turn Management ---

player_finished(Color) :-
    piece_position(Color, 1, finish(Color)),
    piece_position(Color, 2, finish(Color)),
    piece_position(Color, 3, finish(Color)),
    piece_position(Color, 4, finish(Color)).

next_turn :-
    current_turn(Color),
    players_list(Players),
    next_active_player(Color, Players, NextColor),
    retract(current_turn(_)),
    assertz(current_turn(NextColor)).

next_active_player(Current, Players, Next) :-
    next_player(Current, Players, Candidate),
    ( \+ player_finished(Candidate) -> Next = Candidate ; next_active_player(Candidate, Players, Next) ).

next_player(Current, Players, Next) :-
    append(_, [Current, Next | _], Players), !.
next_player(Current, Players, Next) :-
    last(Players, Current),
    [Next | _] = Players.

% --- AI Logic ---
% choose_best_move_from_list(+Color, +DiceList, -BestDice, -BestPieceID)
choose_best_move_from_list(Color, DiceList, BestDice, BestPieceID) :-
    findall(
        Score-Dice-PieceID,
        (
            member(Dice, DiceList),
            valid_move(Color, PieceID, Dice, NewPos),
            piece_position(Color, PieceID, OldPos),
            evaluate_move(Color, PieceID, OldPos, NewPos, Score)
        ),
        ScoredMoves
    ),
    ScoredMoves \= [],
    keysort(ScoredMoves, SortedMoves),
    reverse(SortedMoves, [_-BestDice-BestPieceID | _]).

% choose_best_move(+Color, +DiceValue, -PieceID)
% Evaluates all valid moves and chooses the one with the highest heuristic score.
choose_best_move(Color, DiceValue, BestPieceID) :-
    findall(
        Score-PieceID,
        (
            valid_move(Color, PieceID, DiceValue, NewPos),
            piece_position(Color, PieceID, OldPos),
            evaluate_move(Color, PieceID, OldPos, NewPos, Score)
        ),
        ScoredMoves
    ),
    ScoredMoves \= [],
    keysort(ScoredMoves, SortedMoves),
    reverse(SortedMoves, [_-BestPieceID | _]).

% evaluate_move(+Color, +PieceID, +OldPos, +NewPos, -Score)
evaluate_move(Color, _, OldPos, NewPos, Score) :-
    score_capture(Color, NewPos, ScoreCap),
    score_goal(Color, NewPos, ScoreGoal),
    score_deploy(Color, OldPos, NewPos, ScoreDep),
    score_safe(NewPos, ScoreSafe),
    score_danger(Color, NewPos, ScoreDan),
    progress(Color, NewPos, ScoreProg),
    Score is ScoreCap + ScoreGoal + ScoreDep + ScoreSafe + ScoreDan + ScoreProg.

% 1. Capture Opponent (+100)
score_capture(Color, tile(N), 100) :-
    \+ safe_zone(tile(N)),
    piece_position(OppColor, _, tile(N)),
    OppColor \= Color, !.
score_capture(_, _, 0).

% 2. Goal/Home (+80)
score_goal(Color, finish(Color), 80) :- !.
score_goal(_, _, 0).

% 3. Deploy Piece (+50)
score_deploy(Color, base(Color), tile(_), 50) :- !.
score_deploy(_, _, _, 0).

% 4. Safe Zone (+30)
score_safe(tile(N), 30) :- safe_zone(tile(N)), !.
score_safe(_, 0).

% 5. Avoid Danger (-40)
% Penalty if we land on a non-safe tile that an opponent can reach in 1-6 steps.
score_danger(Color, tile(N), -40) :-
    \+ safe_zone(tile(N)),
    piece_position(OppColor, _, tile(OppN)),
    OppColor \= Color,
    track_distance(OppN, N, Dist),
    Dist >= 1, Dist =< 6, !.
score_danger(_, _, 0).

% 6. Progress (+1 per tile)
progress(_, base(_), 0).
progress(Color, tile(N), Prog) :-
    start_tile(Color, S),
    (N >= S -> Prog is N - S ; Prog is N - S + 52).
progress(_, stretch(_, N), Prog) :-
    Prog is 51 + N.
progress(_, finish(_), 57).

% Helper for distance on the main track
track_distance(A, B, Dist) :-
    D is B - A,
    (D =< 0 -> Dist is D + 52 ; Dist is D).
