from abc import ABC, abstractmethod, abstractstaticmethod
from .environment import Environment
from .agent import Agent

class GameEnvironment(Environment):

    def __init__(self, environment_name):
        super().__init__(environment_name)

        self._players = {}
    
    @abstractmethod
    def add_player(self, player):
        pass

    def get_player(self, player_name):
        assert player_name in self._players.keys(), "The player with name '{0}' was not added to the game.".format(player_name)

        return self._players[player_name]
    
    @abstractmethod
    def get_game_state(self):
        pass

    @abstractstaticmethod
    def get_legal_actions(game_state):
        pass

    @abstractstaticmethod
    def is_terminal(game_state):
        pass
    
    @abstractstaticmethod
    def get_winner(game_state):
        pass

    @abstractstaticmethod
    def transition_result(game_state, action):
        pass

    @abstractstaticmethod
    def turn(game_state):
        pass

    @abstractstaticmethod
    def payoff(game_state, player_name):
        pass