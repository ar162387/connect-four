from une_ai.models import Agent, GridMap

class TicTacToePlayer(Agent):

    def __init__(self, agent_name, agent_program, board_size=3):
        self._board_size = board_size
        super().__init__(agent_name, agent_program)

    def is_valid_box(self, v):
        if v is None:
            return True
        
        return isinstance(v, tuple) and len(v) == 2 and v[0] in range(0,self._board_size) and v[1] in range(0,self._board_size)

    def add_all_sensors(self):
        self.add_sensor(
            'game-board-sensor',
            GridMap(self._board_size, self._board_size, None),
            lambda v, s=self._board_size: isinstance(v, GridMap) and v.get_height() == s and v.get_width() == s
        )

        self.add_sensor(
            'turn-taking-indicator',
            'X',
            lambda v: v in ['X', 'O']
        )
    
    def add_all_actuators(self):
        self.add_actuator(
            'marker',
            None,
            self.is_valid_box
        )
    
    def add_all_actions(self):
        for i in range(0, self._board_size):
            for j in range(0, self._board_size):
                self.add_action(
                    'mark-{0}-{1}'.format(i, j),
                    lambda r=i, c=j: {'marker': (r, c)} if self.is_valid_box((r, c)) else {}
                )