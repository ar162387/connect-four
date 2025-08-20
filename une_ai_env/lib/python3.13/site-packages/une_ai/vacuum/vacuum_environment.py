import numpy as np
import random
import math
import logging

from une_ai.models.grid_map import GridMap
from une_ai.models.environment import Environment

class VacuumEnvironment(Environment):

    def __init__(self, w, h):
        super().__init__('Vacuum world')
        self._w = w
        self._h = h
        self._dirt_map = GridMap(w, h)
        self._walls_map = GridMap(w, h)
        self._explored_tiles = GridMap(w, h)
        self._initialise_walls(0.01)
        self._initialise_dirt(0.01)
        empty_coords = self.get_free_coords()
        agent_pos = random.choice(empty_coords)
        self._max_battery_level = 1000
        self._agent_state = {
            'position': agent_pos,
            'battery': self._max_battery_level,
            'collided': None
        }

        self._score = 0
    
    def get_percepts(self):
        # starts the percepts with current values of sensors
        percepts = {}
        agent_state = self.get_agent_state()
        agent_x, agent_y = agent_state['position']
        coords = {
            'center': (agent_x, agent_y),
            'north': (agent_x, agent_y-1),
            'south': (agent_x, agent_y+1),
            'west': (agent_x-1, agent_y),
            'east': (agent_x+1, agent_y)
        }

        # reset bumper sensors
        for direction in coords.keys():
            if direction != 'center':
                percepts['bumper-sensor-{0}'.format(direction)] = False
        
        # check if the agent crashed against a wall
        collision_dir = agent_state['collided']
        if collision_dir is not None:
            percepts['bumper-sensor-{0}'.format(collision_dir)] = True
        
        percepts['location-sensor'] = agent_state['position']
        percepts['battery-level'] = (agent_state['battery'] / self._max_battery_level)*100

        # now check if there is dirt in the surroundings
        for coord_name, coord in coords.items():
            try:
                is_dirty = self.is_dirty(coord[0], coord[1])
            except:
                is_dirty = False
            percepts['dirt-sensor-{0}'.format(coord_name)] = is_dirty
            
        return percepts
    
    def get_agent_state(self):
        return self._agent_state.copy()
    
    def _consume_agent_battery(self, consumption):
        agent_state = self.get_agent_state()
        cur_level = agent_state['battery']
        if cur_level - consumption < 0:
            new_level = 0
        else:
            new_level = cur_level - consumption
        
        self._agent_state['battery'] = new_level

    def state_transition(self, agent_actuators):
        agent_state = self.get_agent_state()
        try:
            direction = agent_actuators['wheels-direction']
        except:
            # wheels-direction actuator not implemented, using north as default direction
            logging.warning("The actuator 'wheels-direction' is not implemented. Using default direction 'north'")
            direction = 'north'
        
        try:
            suction_power = agent_actuators['suction-power']
        except:
            # suction-power actuator not implemented, using default value
            logging.warning("The actuator 'suction-power' is not implemented. Using default value 0")
            suction_power = 0
        
        try:
            vacuum_power = agent_actuators['vacuum-power']
        except:
            # vacuum-power actuator not implemented, using default value
            logging.warning("The actuator 'vacuum-power' is not implemented. Using default value 0")
            vacuum_power = 0
        
        cur_x, cur_y = agent_state['position']
        try:
            self.set_explored(cur_x, cur_y)
        except:
            # out of boundaries, but that's all good
            # the environment class will manage the
            # crash with the wall in the following instructions
            pass
        
        # remove dirt on current position if suction power on
        if agent_state['battery'] > 0 and suction_power == 1:
            self.remove_dirt(cur_x, cur_y)
            self._consume_agent_battery(5)

        # moving the agent in the new position
        if agent_state['battery'] > 0 and vacuum_power == 1:
            self._consume_agent_battery(1)
            if direction == "west":
                offset = (-1, 0)
            elif direction == "east":
                offset = (1, 0)
            elif direction == "north":
                offset = (0, -1)
            elif direction == "south":
                offset = (0, 1)
            
            new_x, new_y = (cur_x + offset[0], cur_y + offset[1])

            # reset bumper sensors
            self._agent_state['collided'] = None
            
            # check that the agent is not crashing against a wall
            if not self.is_wall(new_x, new_y):
                # the position is a valid position
                self._agent_state['position'] = (new_x, new_y)
            else:
                # there is a wall!
                # update collision state
                self._agent_state['collided'] = direction
                # set the wall position as explored
                try:
                    self._explored_tiles.set_item_value(new_x, new_y, True)
                except:
                    # out of bounds, pass
                    pass
    
    def get_score(self):
        return self._score

    def get_width(self):
        return self._w
    
    def get_height(self):
        return self._h
    
    def set_explored(self, pos_x, pos_y):
        self._explored_tiles.set_item_value(pos_x, pos_y, True)
        
    def _initialise_walls(self, wall_density=0.01):
        total_size = self._w*self._h
        n_walls = math.floor(total_size*wall_density)
        empty_tiles = self._walls_map.find_value(False)
        walls_coords = random.sample(empty_tiles, n_walls)
        for coord in walls_coords:
            orientation = random.choice(['h', 'v'])
            length = random.choice([3, 4, 5])
            cur_x = coord[0]
            cur_y = coord[1]
            for i in range(0, length):
                if cur_x >= self._w or cur_y >= self._h:
                    #if out of bounds, end
                    break
                self._walls_map.set_item_value(cur_x, cur_y, True)
                if orientation == 'h':
                    cur_x += 1
                else:
                    cur_y += 1
    
    def _initialise_dirt(self, dirt_density=0.01):
        total_size = self._w*self._h
        n_dirt = math.floor(total_size*dirt_density)
        self._spawn_dirt(n_dirt)
            
    def _spawn_dirt(self, k=1):
        condition_func = lambda walls_map: np.logical_and(walls_map == False, self._dirt_map.get_map() == False)
        valid_coords = self._walls_map.find_value_by_condition(condition_func)
        new_coord = random.sample(valid_coords, k)
        for coord in new_coord:
            self._dirt_map.set_item_value(coord[0], coord[1], True)

    def is_dirty(self, pos_x, pos_y):
        return self._dirt_map.get_item_value(pos_x, pos_y)
    
    def is_wall(self, pos_x, pos_y):
        try:
            return self._walls_map.get_item_value(pos_x, pos_y)
        except:
            # out of bounds, it's a wall
            return True
    
    def remove_dirt(self, x, y):
        try:
            is_dirt = self.is_dirty(x, y)
            if is_dirt:
                self._score += 1
                self._dirt_map.set_item_value(x, y, False)
        except:
            # we may be out of bounds, but there is no dirt outside bounds
            pass
    
    def get_dirt_coords(self):
        return self._dirt_map.find_value(True)
    
    def get_walls_coords(self):
        return self._walls_map.find_value(True)
    
    def get_free_coords(self):
        condition_func = lambda walls_map: np.logical_and(walls_map == False, self._dirt_map.get_map() == False)
        return self._walls_map.find_value_by_condition(condition_func)
    
    def get_explored_tiles_coords(self):
        return self._explored_tiles.find_value(True)