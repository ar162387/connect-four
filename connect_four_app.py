from une_ai.assignments import ConnectFourGame
from connect_four_environment import ConnectFourEnvironment
from connect_four_player import ConnectFourPlayer
from agent_programs import random_behaviour, human_agent, intelligent_behaviour

if __name__ == '__main__':
    # Select players: Yellow uses intelligent behaviour; Red can be random or intelligent
    yellow_player = ConnectFourPlayer('Y', intelligent_behaviour)
    red_player = ConnectFourPlayer('R', intelligent_behaviour)

    # DO NOT EDIT THESE LINES OF CODE!!!
    game_environment = ConnectFourEnvironment()
    game_environment.add_player(yellow_player)
    game_environment.add_player(red_player)

    game = ConnectFourGame(yellow_player, red_player, game_environment)