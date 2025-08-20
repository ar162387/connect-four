import random
import numpy as np

from une_ai.models import Agent

class VacuumAgent(Agent):

    WHEELS_DIRECTIONS = ['north', 'south', 'west', 'east']

    def __init__(self, agent_program, init_x=0, init_y=0, max_battery_level=1000):
        super().__init__(
            agent_name='vacuum_agent',
            agent_program=agent_program
        )

        self._collision = False
        self._max_battery_level = max_battery_level

        # adding the sensors
        self.add_sensor('battery-level', max_battery_level, lambda v: isinstance(v, int) and v >= 0)
        self.add_sensor('location-sensor', (init_x, init_y), lambda v: isinstance(v, tuple) and isinstance(v[0], int) and isinstance(v[1], int))

        directions = VacuumAgent.WHEELS_DIRECTIONS.copy()
        directions.append('center')
        for direction in directions:
            self.add_sensor('dirt-sensor-{0}'.format(direction), False, lambda v: isinstance(v, bool) or isinstance(v, np.bool_))
            if direction != 'center':
                self.add_sensor('bumper-sensor-{0}'.format(direction), False, lambda v: isinstance(v, bool) or isinstance(v, np.bool_))

        # adding the actuators
        self.add_actuator(
            'wheels-direction',
            random.choice(VacuumAgent.WHEELS_DIRECTIONS),
            lambda v: v in VacuumAgent.WHEELS_DIRECTIONS
        )
        self.add_actuator(
            'vacuum-power',
            0,
            lambda v: v in [0, 1]
        )
        self.add_actuator(
            'suction-power',
            0,
            lambda v: v in [0, 1]
        )

        # adding the actions
        self.add_action(
            'start-cleaning',
            lambda: {'vacuum-power': 1} if not self.is_out_of_charge() else {}
        )
        self.add_action(
            'stop-cleaning',
            lambda: {
                'vacuum-power': 0
            }
        )
        self.add_action(
            'activate-suction-mechanism',
            lambda: {'suction-power': 1} if not self.is_out_of_charge() else {}
        )
        self.add_action(
            'deactivate-suction-mechanism',
            lambda: {
                'suction-power': 0
            }
        )
        for direction in VacuumAgent.WHEELS_DIRECTIONS:
            self.add_action(
                'change-direction-{0}'.format(direction),
                lambda d=direction: {'wheels-direction': d} if not self.is_out_of_charge() else {}
            )

    def get_pos_x(self):
        return self.read_sensor_value('location-sensor')[0]
    
    def get_pos_y(self):
        return self.read_sensor_value('location-sensor')[1]

    def _update_position(self, new_x, new_y):
        self._pos_x = new_x
        self._pos_y = new_y
        self._update_sensor_value('location-sensor', (new_x, new_y))
    
    def _consume_battery(self, consumption=1):
        cur_level = self.read_sensor_value('battery-level')
        if cur_level - consumption < 0:
            new_level = 0

            # turn off powers
            self._update_actuator_value('suction-power', 0)
            self._update_actuator_value('vacuum-power', 0)
        else:
            new_level = cur_level - consumption
        
        self._update_sensor_value('battery-level', new_level)
    
    def is_out_of_charge(self):
        return self.read_sensor_value('battery-level') == 0
    
    def get_battery_level(self):
        return int(self.read_sensor_value('battery-level')/self._max_battery_level*100)
    
    def collision_detected(self):
        self._collision = True
    
    def reset_collisions(self):
        self._collision = False

    def did_collide(self):
        return self._collision

    def _interact_with_environment(self, environment):
        self.reset_collisions()

        # remove dirt on current position if suction power on
        cur_x = self.get_pos_x()
        cur_y = self.get_pos_y()
        
        if self.read_actuator_value('suction-power') == 1:
            environment.remove_dirt(cur_x, cur_y)
            self._consume_battery(5)

        if self.read_actuator_value('vacuum-power') == 1:
            self._consume_battery(1)
            direction = self.read_actuator_value('wheels-direction')
            if direction == "west":
                offset = (-1, 0)
            elif direction == "east":
                offset = (1, 0)
            elif direction == "north":
                offset = (0, -1)
            elif direction == "south":
                offset = (0, 1)
            
            new_x, new_y = (cur_x + offset[0], cur_y + offset[1])
            
            try:
                environment.set_explored(new_x, new_y)
            except:
                # out of boundaries, but that's all good
                # the environment class will manage the
                # crash with the wall when sensing
                pass

            if environment.is_wall(new_x, new_y):
                self.collision_detected()

            self._update_position(new_x, new_y)
                