from une_ai.assignments import ConnectFourBaseEnvironment

class ConnectFourEnvironment(ConnectFourBaseEnvironment):

    def __init__(self):
        super().__init__()

    @staticmethod
    def get_legal_actions(game_state):
        """Compute all legal actions from the given game_state.

        Returned actions follow the strings consumed by transition_result:
        - 'release-<col>' to drop a checker in column <col>
        - 'popup-<col>' to pop the bottom checker from column <col>
        - 'use-power-up-<col>' to play the current player's power-up in column <col>

        Advanced rules are fully supported:
        - Popups: a player may pop only their own checker from the bottom of a column.
        - Power-ups: 'anvil' (clear target column first), 'wall' (drop a W checker), 'x2' (keeps the turn).
        """
        assert isinstance(game_state, dict), "game_state must be a dictionary"
        game_board = game_state['game-board']
        cur_player = game_state['player-turn']

        legal = []

        # Basic release actions: any valid column that is not full
        for col in range(game_board.get_width()):
            if not ConnectFourBaseEnvironment.is_column_full(game_board, col):
                legal.append(f"release-{col}")

        # Popup actions: only if bottom checker belongs to current player
        for col in range(game_board.get_width()):
            bottom_row = game_board.get_height() - 1
            bottom_checker = game_board.get_item_value(col, bottom_row)
            if bottom_checker == cur_player:
                legal.append(f"popup-{col}")

        # Power-up actions: depend on the current player's available power-up
        powerup_key = f"power-up-{cur_player}"
        powerup = game_state.get(powerup_key, None)
        if powerup is not None:
            if powerup == 'anvil':
                # Can target any valid column (even if full)
                for col in range(game_board.get_width()):
                    legal.append(f"use-power-up-{col}")
            else:
                # 'wall' and 'x2' require a non-full column
                for col in range(game_board.get_width()):
                    if not ConnectFourBaseEnvironment.is_column_full(game_board, col):
                        legal.append(f"use-power-up-{col}")

        return legal
    
    @staticmethod
    def is_terminal(game_state):
        """A state is terminal if a winner exists or there are no legal actions left."""
        if ConnectFourBaseEnvironment.get_winner(game_state) is not None:
            return True
        return len(ConnectFourEnvironment.get_legal_actions(game_state)) == 0
    
    @staticmethod
    def payoff(game_state, player_colour):
        """Heuristic evaluation of a game_state from player_colour's perspective.

        Terminal states return large-magnitude values, non-terminals are scored using:
        - Weighted count of open 3-in-a-row, 2-in-a-row, 1-in-a-row opportunities
          obtained from get_openings()
        - Mild center-column preference to encourage strong structure
        """
        assert player_colour in ['Y', 'R'], "player_colour must be 'Y' or 'R'"

        winner = ConnectFourBaseEnvironment.get_winner(game_state)
        if winner == player_colour:
            return 1_000_000
        if winner is not None and winner != player_colour:
            return -1_000_000

        legal_moves = ConnectFourEnvironment.get_legal_actions(game_state)
        if len(legal_moves) == 0:
            # Stalemate
            return 0

        game_board = game_state['game-board']

        def score_openings(for_player: str) -> int:
            openings = ConnectFourBaseEnvironment.get_openings(game_board, for_player)
            # Weights emphasize immediate threats/opportunities
            weight_for_val = {3: 100, 2: 10, 1: 2}
            total = 0
            for rows in openings.values():
                for _, max_val in rows:
                    total += weight_for_val.get(int(max_val), 0)
            # Center column preference
            center_col = game_board.get_width() // 2
            center_tokens = (game_board.get_column(center_col) == for_player).sum()
            total += 5 * int(center_tokens)
            return int(total)

        opponent = 'R' if player_colour == 'Y' else 'Y'
        my_score = score_openings(player_colour)
        opp_score = score_openings(opponent)
        return int(my_score - opp_score)