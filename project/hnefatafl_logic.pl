:- use_module(library(lists)).

size(11).

empty(e).
attacker(a).
defender(d).
king(k).
corner(x).

throne(5,5).

corner_pos(0,0).
corner_pos(0,10).
corner_pos(10,0).
corner_pos(10,10).

opponent(a, d).
opponent(d, a).

switch_player(a, d).
switch_player(d, a).

initial_board([
[x,e,e,a,a,a,a,a,e,e,x],
[e,e,e,e,e,a,e,e,e,e,e],
[e,e,e,e,e,e,e,e,e,e,e],
[a,e,e,e,e,d,e,e,e,e,a],
[a,e,e,e,d,d,d,e,e,e,a],
[a,a,e,d,d,k,d,d,e,a,a],
[a,e,e,e,d,d,d,e,e,e,a],
[a,e,e,e,e,d,e,e,e,e,a],
[e,e,e,e,e,e,e,e,e,e,e],
[e,e,e,e,e,a,e,e,e,e,e],
[x,e,e,a,a,a,a,a,e,e,x]
]).

in_bounds(R,C) :-
    size(S),
    R >= 0, R < S,
    C >= 0, C < S.

get_cell(Board,R,C,Val) :-
    nth0(R,Board,Row),
    nth0(C,Row,Val).

replace_nth0(0, [_|T], X, [X|T]).
replace_nth0(N, [H|T], X, [H|R]) :-
    N > 0,
    N1 is N - 1,
    replace_nth0(N1, T, X, R).

set_cell(Board,R,C,Val,NewBoard) :-
    nth0(R,Board,Row),
    replace_nth0(C,Row,Val,NewRow),
    replace_nth0(R,Board,NewRow,NewBoard).

piece_for_player(a,a).
piece_for_player(d,d).
piece_for_player(k,d).

is_empty_target(Board,R,C,Piece) :-
    corner_pos(R,C),
    Piece = k.

is_empty_target(Board,R,C,_) :-
    \+ corner_pos(R,C),
    get_cell(Board,R,C,e).

valid_piece(Board,Player,R,C,Piece) :-
    in_bounds(R,C),
    get_cell(Board,R,C,Piece),
    piece_for_player(Piece,Player).

straight_move(R,C,NR,NC) :-
    (R =:= NR ; C =:= NC),
    \+ (R =:= NR, C =:= NC).

step_dir(R,C,NR,NC,DR,DC) :-
    (NR > R -> DR = 1 ; NR < R -> DR = -1 ; DR = 0),
    (NC > C -> DC = 1 ; NC < C -> DC = -1 ; DC = 0).

path_clear(Board,R,C,NR,NC) :-
    step_dir(R,C,NR,NC,DR,DC),
    CR is R + DR,
    CC is C + DC,
    path_clear_loop(Board,CR,CC,NR,NC,DR,DC).

path_clear_loop(_,R,C,R,C,_,_) :- !.
path_clear_loop(Board,R,C,NR,NC,DR,DC) :-
    get_cell(Board,R,C,e),
    R2 is R + DR,
    C2 is C + DC,
    path_clear_loop(Board,R2,C2,NR,NC,DR,DC).

valid_move(Board,Player,R,C,NR,NC) :-
    in_bounds(R,C),
    in_bounds(NR,NC),
    valid_piece(Board,Player,R,C,Piece),
    straight_move(R,C,NR,NC),
    is_empty_target(Board,NR,NC,Piece),
    \+ (throne(NR,NC), Piece \= k),
    path_clear(Board,R,C,NR,NC).

enemy_for_piece(a,d).
enemy_for_piece(d,a).

is_enemy_side(Board,Piece,R,C) :-
    enemy_for_piece(Piece,Enemy),
    get_cell(Board,R,C,Enemy).

in_sandwich(Board,R,C,Piece) :-
    Piece \= k,
    in_bounds(R,C),
    (
        C1 is C - 1,
        C2 is C + 1,
        in_bounds(R,C1),
        in_bounds(R,C2),
        is_enemy_side(Board,Piece,R,C1),
        is_enemy_side(Board,Piece,R,C2)
    ;
        R1 is R - 1,
        R2 is R + 1,
        in_bounds(R1,C),
        in_bounds(R2,C),
        is_enemy_side(Board,Piece,R1,C),
        is_enemy_side(Board,Piece,R2,C)
    ).

legal_move(Board,Player,R,C,NR,NC) :-
    valid_move(Board,Player,R,C,NR,NC),
    get_cell(Board,R,C,Piece),
    \+ in_sandwich_after_move(Board,R,C,NR,NC,Piece).

in_sandwich_after_move(Board,R,C,NR,NC,Piece) :-
    set_cell(Board,R,C,e,B1),
    set_cell(B1,NR,NC,Piece,B2),
    in_sandwich(B2,NR,NC,Piece).

friendly_capture_side(Board,Current,R,C) :-
    get_cell(Board,R,C,Current).

friendly_capture_side(_,_,R,C) :-
    corner_pos(R,C).

friendly_capture_side(_,_,R,C) :-
    throne(R,C).

capture_enemy(a,d).
capture_enemy(d,a).

direction(-1,0).
direction(1,0).
direction(0,-1).
direction(0,1).

check_capture(Board,R,C,FinalBoard,Captured) :-
    get_cell(Board,R,C,Current),
    (Current = k ->
        FinalBoard = Board,
        Captured = []
    ;
        findall(pos(AR,AC,Enemy),
            capturable(Board,R,C,Current,AR,AC,Enemy),
            Captured),
        remove_captured(Board,Captured,FinalBoard)
    ).

capturable(Board,R,C,Current,AR,AC,Enemy) :-
    direction(DR,DC),
    AR is R + DR,
    AC is C + DC,
    BR is R + 2*DR,
    BC is C + 2*DC,
    in_bounds(AR,AC),
    in_bounds(BR,BC),
    capture_enemy(Current,Enemy),
    get_cell(Board,AR,AC,Enemy),
    Enemy \= k,
    friendly_capture_side(Board,Current,BR,BC).

remove_captured(Board,[],Board).
remove_captured(Board,[pos(R,C,_)|Rest],FinalBoard) :-
    set_cell(Board,R,C,e,B2),
    remove_captured(B2,Rest,FinalBoard).

apply_move(Board,Player,R,C,NR,NC,NewBoard,Captured) :-
    legal_move(Board,Player,R,C,NR,NC),
    get_cell(Board,R,C,Piece),
    set_cell(Board,R,C,e,B1),
    set_cell(B1,NR,NC,Piece,B2),
    check_capture(B2,NR,NC,NewBoard,Captured).

king_pos(Board,R,C) :-
    nth0(R,Board,Row),
    nth0(C,Row,k).

king_escaped(Board) :-
    corner_pos(R,C),
    get_cell(Board,R,C,k).

king_captured(Board) :-
    \+ king_pos(Board,_,_), !.

king_captured(Board) :-
    king_pos(Board,R,C),
    findall(1, king_blocked_side(Board,R,C), Blocks),
    length(Blocks, Count),
    required_blocks(R,C,Required),
    Count >= Required.

king_blocked_side(Board,R,C) :-
    direction(DR,DC),
    NR is R + DR,
    NC is C + DC,
    in_bounds(NR,NC),
    (
        get_cell(Board,NR,NC,a)
        ;
        corner_pos(NR,NC)
    ).

required_blocks(R,C,2) :-
    corner_pos(R,C), !.
required_blocks(R,C,3) :-
    size(S),
    Last is S - 1,
    (R =:= 0 ; R =:= Last ; C =:= 0 ; C =:= Last), !.
required_blocks(_,_,4).

all_pieces(Board,Player,Pieces) :-
    findall(pos(R,C),
        (
            nth0(R,Board,Row),
            nth0(C,Row,Piece),
            piece_for_player(Piece,Player)
        ),
        Pieces).

possible_move(Board,Player,move(R,C,NR,NC)) :-
    all_pieces(Board,Player,Pieces),
    member(pos(R,C),Pieces),
    direction(DR,DC),
    scan_direction(Board,Player,R,C,DR,DC,NR,NC).

scan_direction(Board,Player,R,C,DR,DC,NR,NC) :-
    R1 is R + DR,
    C1 is C + DC,
    in_bounds(R1,C1),
    legal_move(Board,Player,R,C,R1,C1),
    (
        NR = R1,
        NC = C1
        ;
        scan_direction(Board,Player,R1,C1,DR,DC,NR,NC)
    ).

all_moves(Board,Player,Moves) :-
    findall(M, possible_move(Board,Player,M), Moves).

manhattan(R1,C1,R2,C2,D) :-
    D is abs(R1-R2) + abs(C1-C2).

min_corner_distance(R,C,MinD) :-
    findall(D,
        (
            corner_pos(CR,CC),
            manhattan(R,C,CR,CC,D)
        ),
        Ds),
    min_list(Ds,MinD).

adjacent_attackers(Board,R,C,Count) :-
    findall(1,
        (
            direction(DR,DC),
            NR is R + DR,
            NC is C + DC,
            in_bounds(NR,NC),
            get_cell(Board,NR,NC,a)
        ),
        L),
    length(L,Count).

sandwich_score(Board,Score) :-
    findall(S,
        (
            nth0(R,Board,Row),
            nth0(C,Row,Piece),
            Piece \= e,
            Piece \= x,
            (
                in_sandwich(Board,R,C,Piece)
                ->
                (
                    Piece = a -> S = -40
                    ;
                    S = 40
                )
                ;
                S = 0
            )
        ),
        Scores),
    sum_list(Scores,Score).

evaluate(Board,Player,Value) :-
    king_captured(Board), !,
    (Player = a -> Value = 10000 ; Value = -10000).

evaluate(Board,Player,Value) :-
    king_escaped(Board), !,
    (Player = d -> Value = 10000 ; Value = -10000).

evaluate(Board,Player,Value) :-
    king_pos(Board,KR,KC),
    min_corner_distance(KR,KC,Dist),
    KingEscapeScore is -Dist * 40,
    adjacent_attackers(Board,KR,KC,Adj),
    EncircleScore is Adj * 250,
    sandwich_score(Board,SandwichScore),
    
   (throne(TR,TC), manhattan(KR,KC,TR,TC,TD), TD =< 1 
    -> ThroneScore1 = 100       
    ; ThroneScore1 = 0           
),
( corner_pos(KR,KC) 
    -> ThroneScore is ThroneScore1 + 500 
    ; ThroneScore is ThroneScore1        
)

    Raw is KingEscapeScore * 1.2 + EncircleScore * 2.0 + SandwichScore * 1.5 + ThroneScore,
    (Player = d -> Value is -Raw ; Value is Raw).

terminal(Board) :-
    king_escaped(Board);
    king_captured(Board).

best_move(Board,Player,Depth,BestMove,BestValue) :-
    all_moves(Board,Player,Moves),
    Moves \= [],
    alpha_beta_root(Board,Player,Depth,Moves,none,-1000000,BestMove,BestValue).

alpha_beta_root(_,_,_,[],BestMove,BestValue,BestMove,BestValue).

alpha_beta_root(Board,Player,Depth,[move(R,C,NR,NC)|Rest],CurrentBest,CurrentVal,BestMove,BestValue) :-
    apply_move(Board,Player,R,C,NR,NC,NewBoard,_),
    switch_player(Player,Opponent),
    D1 is Depth - 1,
    alpha_beta(NewBoard,D1,-1000000,1000000,Opponent,Player,false,Val),
    (
        Val > CurrentVal
        ->
        NewBest = move(R,C,NR,NC),
        NewVal = Val
        ;
        NewBest = CurrentBest,
        NewVal = CurrentVal
    ),
    alpha_beta_root(Board,Player,Depth,Rest,NewBest,NewVal,BestMove,BestValue).

alpha_beta(Board,0,_,_,_,RootPlayer,_,Value) :-
    evaluate(Board,RootPlayer,Value), !.

alpha_beta(Board,_,_,_,_,RootPlayer,_,Value) :-
    terminal(Board),
    evaluate(Board,RootPlayer,Value), !.

alpha_beta(Board,Depth,Alpha,Beta,CurrentPlayer,RootPlayer,true,Value) :-
    all_moves(Board,CurrentPlayer,Moves),
    (
        Moves = []
        ->
        evaluate(Board,RootPlayer,Value)
        ;
        max_value(Board,Moves,Depth,Alpha,Beta,CurrentPlayer,RootPlayer,-1000000,Value)
    ).

alpha_beta(Board,Depth,Alpha,Beta,CurrentPlayer,RootPlayer,false,Value) :-
    all_moves(Board,CurrentPlayer,Moves),
    (
        Moves = []
        ->
        evaluate(Board,RootPlayer,Value)
        ;
        min_value(Board,Moves,Depth,Alpha,Beta,CurrentPlayer,RootPlayer,1000000,Value)
    ).

max_value(_,[],_,_,_,_,_,Best,Best).

max_value(Board,[move(R,C,NR,NC)|Rest],Depth,Alpha,Beta,Player,Root,BestSoFar,Value) :-
    apply_move(Board,Player,R,C,NR,NC,NewBoard,_),
    switch_player(Player,Opp),
    D1 is Depth - 1,
    alpha_beta(NewBoard,D1,Alpha,Beta,Opp,Root,false,V),
    NewBest is max(BestSoFar,V),
    NewAlpha is max(Alpha,NewBest),
    (
        NewAlpha >= Beta
        ->
        Value = NewBest
        ;
        max_value(Board,Rest,Depth,NewAlpha,Beta,Player,Root,NewBest,Value)
    ).

min_value(_,[],_,_,_,_,_,Best,Best).

min_value(Board,[move(R,C,NR,NC)|Rest],Depth,Alpha,Beta,Player,Root,BestSoFar,Value) :-
    apply_move(Board,Player,R,C,NR,NC,NewBoard,_),
    switch_player(Player,Opp),
    D1 is Depth - 1,
    alpha_beta(NewBoard,D1,Alpha,Beta,Opp,Root,true,V),
    NewBest is min(BestSoFar,V),
    NewBeta is min(Beta,NewBest),
    (
        Alpha >= NewBeta
        ->
        Value = NewBest
        ;
        min_value(Board,Rest,Depth,Alpha,NewBeta,Player,Root,NewBest,Value)
    ).
