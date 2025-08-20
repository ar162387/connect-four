import traceback
import random
import math

from une_ai.assignments import ConnectFourGame
from connect_four_environment import ConnectFourEnvironment

# A simple agent program choosing actions randomly
def random_behaviour(percepts, actuators):
    try:
        game_state = {
            'game-board': percepts['game-board-sensor'],
            'power-up-Y': percepts['powerups-sensor']['Y'],
            'power-up-R': percepts['powerups-sensor']['R'],
            'player-turn': percepts['turn-taking-indicator']
        }
    except KeyError as e:
        game_state = {}
        print("You may have forgotten to add the necessary sensors:")
        traceback.print_exc()

    if not ConnectFourEnvironment.is_terminal(game_state):
        legal_moves = ConnectFourEnvironment.get_legal_actions(game_state)
        try:
            action = random.choice(legal_moves)
        except IndexError as e:
            print("You may have forgotten to implement the ConnectFourEnvironment methods, or you implemented them incorrectly:")
            traceback.print_exc()
            return []

        return [action]
    else:
        return []

# An agent program to allow a human player to play Connect Four
# see the assignment's requirements for a list of valid keys
# to interact with the game
def human_agent(percepts, actuators):
    action = ConnectFourGame.wait_for_user_input()
    return [action]

def intelligent_behaviour(percepts, actuators):
    """Select an action using alpha-beta search with a heuristic evaluation.

    Design choices for speed and strength:
    - Fixed depth search with move ordering (center-first, immediate wins, blocks)
    - Use environment's static helpers for legality, transitions, and payoff
    - Fallback to random when no legal moves (defensive)
    """
    try:
        game_state = {
            'game-board': percepts['game-board-sensor'],
            'power-up-Y': percepts['powerups-sensor']['Y'],
            'power-up-R': percepts['powerups-sensor']['R'],
            'player-turn': percepts['turn-taking-indicator']
        }
    except Exception:
        traceback.print_exc()
        return []

    if ConnectFourEnvironment.is_terminal(game_state):
        return []

    my_colour = game_state['player-turn']
    opponent = 'R' if my_colour == 'Y' else 'Y'

    def ordered_moves(state):
        moves = ConnectFourEnvironment.get_legal_actions(state)
        # Prefer center columns, then nearer-to-center, and prioritize direct wins/blocks
        board = state['game-board']
        center = board.get_width() // 2
        def col_of(m):
            return int(m.split('-')[-1])
        def win_in_one(m, colour):
            ns = ConnectFourEnvironment.transition_result(state, m)
            return ConnectFourEnvironment.get_winner(ns) == colour
        # Precompute wins/blocks
        win_now = [m for m in moves if win_in_one(m, my_colour)]
        block_now = [m for m in moves if win_in_one(m, opponent)]
        rest = [m for m in moves if m not in win_now and m not in block_now]
        rest.sort(key=lambda m: abs(col_of(m) - center))
        # Heuristic order: winning moves, blocking moves, center-ish
        return win_now + block_now + rest

    # Depth tuned for speed; increased if few moves available
    MAX_DEPTH = 4
    branching = len(ConnectFourEnvironment.get_legal_actions(game_state))
    if branching <= 6:
        MAX_DEPTH = 5

    def evaluate(state):
        return ConnectFourEnvironment.payoff(state, my_colour)

    def max_value(state, alpha, beta, depth):
        if depth == 0 or ConnectFourEnvironment.is_terminal(state):
            return evaluate(state), None
        v = -math.inf
        best = None
        for a in ordered_moves(state):
            ns = ConnectFourEnvironment.transition_result(state, a)
            val, _ = min_value(ns, alpha, beta, depth - 1)
            if val > v:
                v, best = val, a
            alpha = max(alpha, v)
            if v >= beta:
                break
        return v, best

    def min_value(state, alpha, beta, depth):
        if depth == 0 or ConnectFourEnvironment.is_terminal(state):
            return evaluate(state), None
        v = math.inf
        best = None
        for a in ordered_moves(state):
            ns = ConnectFourEnvironment.transition_result(state, a)
            val, _ = max_value(ns, alpha, beta, depth - 1)
            if val < v:
                v, best = val, a
            beta = min(beta, v)
            if v <= alpha:
                break
        return v, best

    _, action = max_value(game_state, -math.inf, math.inf, MAX_DEPTH)
    if action is None:
        legal = ConnectFourEnvironment.get_legal_actions(game_state)
        if not legal:
            return []
        action = random.choice(legal)
    return [action]

