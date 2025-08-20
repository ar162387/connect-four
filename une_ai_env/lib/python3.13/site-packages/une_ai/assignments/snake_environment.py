import numpy as np
import random
import math
import logging

from une_ai.models import Environment, GridMap

class InvalidMoveException(Exception):
    pass

class SnakeEnvironment(Environment):

    def __init__(self, width, height, max_time):
        super().__init__("Snake Environment")

        self._w = width
        self._h = height
        self._food_map = GridMap(width, height, 0)
        self._walls_map = GridMap(width, height)
        self._initialise_walls(0.01)
        self._initialise_food()
        empty_coords = self.get_free_coords()
        agent_pos = random.choice(empty_coords)
        self._snake = [agent_pos]
        self._grow = False
        self._prev_direction = None

        self._score = 0
        self._clock = max_time
        self._game_over = False
    
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
    
    def _initialise_food(self):
        food = [5, 10, 20]
        self._spawn_food(food)
            
    def _spawn_food(self, food):
        condition_func = lambda walls_map: np.logical_and(walls_map == False, self._food_map.get_map() == 0)
        valid_coords = self._walls_map.find_value_by_condition(condition_func)
        new_coord = random.sample(valid_coords, len(food))
        for i, coord in enumerate(new_coord):
            self._food_map.set_item_value(coord[0], coord[1], food[i])
    
    def get_food_coords(self):
        condition_func = lambda food_map: food_map != 0
        return self._food_map.find_value_by_condition(condition_func)
    
    def get_walls_coords(self):
        return self._walls_map.find_value(True)
    
    def get_free_coords(self):
        condition_func = lambda walls_map: np.logical_and(walls_map == False, self._food_map.get_map() == 0)
        return self._walls_map.find_value_by_condition(condition_func)
    
    def move_snake_head(self, direction):
        assert direction in ['up', 'down', 'left', 'right'], "Direction not valid ('{0}').".format(direction)

        if self.is_game_over():
            return
        
        if (self._prev_direction == 'up' and direction == 'down') or (self._prev_direction == 'down' and direction == 'up') or (self._prev_direction == 'left' and direction == 'right') or (self._prev_direction == 'right' and direction == 'left'):
            raise(InvalidMoveException("Invalid move action! The current direction of the head snake is '{0}' and it cannot go the opposite direction '{1}'. You might be missing something when adding your actions...".format(self._prev_direction, direction)))
        
        self._prev_direction = direction

        prev_body = self._snake.copy()

        # move the head according to the current direction
        cur_head = self._snake[0]
        if direction == 'up':
            new_head = (cur_head[0], cur_head[1] - 1)
        elif direction == 'down':
            new_head = (cur_head[0], cur_head[1] + 1)
        elif direction == 'left':
            new_head = (cur_head[0] - 1, cur_head[1])
        elif direction == 'right':
            new_head = (cur_head[0] + 1, cur_head[1])
        
        self._snake.insert(0, new_head)

        # remove the snake's tail if it did not eat fruit
        if not self._grow:
            self._snake.pop()
        else:
            # stop growing
            self._grow = False

        if self.did_snake_collide():
            self._snake = prev_body
            self._game_over = True
    
    def did_snake_collide(self):
        head = self._snake[0]
        try:
            is_obstacle = self._walls_map.get_item_value(head[0], head[1]) or head in self._snake[1:]
        except:
            # out of bounds, crashed against border
            is_obstacle = True
        
        return is_obstacle
    
    def eat_food(self):
        head = self._snake[0]
        food = self._food_map.get_item_value(head[0], head[1])
        if food != 0:
            self._food_map.set_item_value(head[0], head[1], 0)
            self._spawn_food([food])
            self._score += food
            self._grow = True
        else:
            # eating where there is no food, penalty
            self._score -= 5

    def is_game_over(self):
        return self._game_over
    
    def get_score(self):
        return self._score
    
    def tick(self, tick):
        self._clock -= tick
        if self._clock <= 0:
            self._clock = 0
            self._game_over = True
    
    def get_time(self):
        return self._clock
    
    def get_percepts(self):
        percepts = {}

        percepts['body-sensor'] = self._snake.copy()

        food_coords = self.get_food_coords()
        food = []
        for coord in food_coords:
            points = self._food_map.get_item_value(coord[0], coord[1])
            food.append((coord[0], coord[1], points))
        percepts['food-sensor'] = food

        percepts['obstacles-sensor'] = self._walls_map.find_value(True)
        percepts['clock'] = int(self._clock)

        return percepts
    
    def state_transition(self, agent_actuators):
        if agent_actuators is not None and 'head' in agent_actuators.keys():
            try:
                direction = agent_actuators['head']
                if direction in ['up', 'down', 'left', 'right']:
                    self.move_snake_head(direction)
                else:
                    logging.error("The value '{0}' is not a valid direction for the 'head' actuator.".format(direction))
            except AssertionError as err:
                logging.warning("The actuator 'head' might not be implemented, it might be implemented incorrectly or an invalid move was chosen. Error: {0}".format(err))
        else:
            logging.warning("The actuator 'head' might not be implemented or implemented incorrectly.")
        
        if agent_actuators is not None and 'mouth' in agent_actuators.keys():
            try:
                mouth_state = agent_actuators['mouth']
                if mouth_state in ['open', 'close']:
                    if mouth_state == 'open':
                        self.eat_food()
                else:
                    logging.error("The value '{0}' is not a valid mouth state for the 'mouth' actuator.".format(mouth_state))
            except Exception as err:
                logging.warning("The actuator 'mouth' might not be implemented or it might be implemented incorrectly. Error: {0}".format(err))
        else:
            logging.warning("The actuator 'mouth' might not be implemented or implemented incorrectly.")