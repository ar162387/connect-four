from une_ai.models import Agent

class ConnectFourPlayer(Agent):

    def __init__(self, agent_name, agent_program):
        super().__init__(agent_name, agent_program)

    def add_all_sensors(self):
        """Declare the sensors required by the assignment.

        - 'game-board-sensor': stores a GridMap of size 6x7 containing values in {'Y','R','W',None}
        - 'powerups-sensor': dictionary {'Y': powerup_or_None, 'R': powerup_or_None}
        - 'turn-taking-indicator': current player's turn ('Y' or 'R')
        """
        def is_valid_gridmap(value):
            try:
                # Lazy validation: ensure required methods exist and size matches 7x6
                w = value.get_width()
                h = value.get_height()
                ok_size = (w == 7 and h == 6)
                _ = value.get_map()
                return ok_size
            except Exception:
                return False

        def is_valid_powerups(value):
            return isinstance(value, dict) and 'Y' in value and 'R' in value

        def is_valid_turn(value):
            return value in ['Y', 'R']

        # Add sensors with permissive placeholder values; they will be overwritten by sense()
        self.add_sensor('game-board-sensor', None, lambda v: True if v is None else is_valid_gridmap(v))
        self.add_sensor('powerups-sensor', {'Y': None, 'R': None}, is_valid_powerups)
        self.add_sensor('turn-taking-indicator', 'Y', is_valid_turn)

    def add_all_actuators(self):
        """Declare the actuators required by the assignment.

        - 'checker-handler': tuple (handling_type, column_index)
            handling_type in {'release','popup'}; col in [0..6]
        - 'powerup-selector': boolean flag indicating whether to use a power-up
        """
        def is_valid_checker_handler(value):
            if not isinstance(value, tuple) or len(value) != 2:
                return False
            handling_type, col = value
            return handling_type in ['release', 'popup'] and isinstance(col, int) and 0 <= col <= 6

        self.add_actuator('checker-handler', ('release', 0), is_valid_checker_handler)
        self.add_actuator('powerup-selector', False, lambda v: isinstance(v, bool))

    def add_all_actions(self):
        """Bind action names to functions that update actuators.

        Actions:
        - release-0..6
        - popup-0..6
        - use-power-up-0..6
        """
        def mk_release(col):
            return lambda: {
                'checker-handler': ('release', col),
                'powerup-selector': False
            }

        def mk_popup(col):
            return lambda: {
                'checker-handler': ('popup', col),
                'powerup-selector': False
            }

        def mk_power(col):
            return lambda: {
                'checker-handler': ('release', col),
                'powerup-selector': True
            }

        for c in range(7):
            self.add_action(f'release-{c}', mk_release(c))
        for c in range(7):
            self.add_action(f'popup-{c}', mk_popup(c))
        for c in range(7):
            self.add_action(f'use-power-up-{c}', mk_power(c))