from une_ai.models import Agent

import pygame
import math

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
MAGENTA = (255, 0, 255)

pygame.init()
DISPLAY_WIDTH = 320
DISPLAY_HEIGHT = 240
SCORE_BAR_HEIGHT = 40
TILE_SIZE = 10

window = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT+SCORE_BAR_HEIGHT))
pygame.display.set_caption('Vacuum cleaner agent')
window_clock = pygame.time.Clock()

class VacuumGame:

    def __init__(self, vacuum_agent, uses_charging_dock=False, display_w=DISPLAY_WIDTH, display_h=DISPLAY_HEIGHT, tile_size=TILE_SIZE):
        assert isinstance(vacuum_agent, Agent), "The parameter vacuum_agent must be an instance of a subclass of the class Agent."

        self._tile_size = tile_size
        self._display = window
        self._display_size = (display_w, display_h)
        w_env = math.floor(display_w / self._tile_size)
        h_env = math.floor(display_h / self._tile_size)
        if uses_charging_dock:
            from une_ai.vacuum import VacuumDockEnvironment
            self._environment = VacuumDockEnvironment(w_env, h_env)
        else:
            from une_ai.vacuum import VacuumEnvironment
            self._environment = VacuumEnvironment(w_env, h_env)
        self._agent = vacuum_agent

        # updating the sensors based on initial environment state
        self._agent.sense(self._environment)

        fonts = pygame.font.get_fonts()
        self._font = fonts[0] # default to a random font
        # try to look among the most common fonts
        test_fonts = ['arial', 'couriernew', 'verdana', 'helvetica', 'roboto']
        for font in test_fonts:
            if font in fonts:
                self._font = font
                break

        self.main()
        
    def _play_step(self):        
        # SENSE
        self._agent.sense(self._environment)
        # THINK
        actions = self._agent.think()
        # ACT
        self._agent.act(actions, self._environment)
    
    def _reset_bg(self):
        self._display.fill(BLACK)
    
    def _draw_tile(self, x, y, color, alpha = 255):
        x_coord = x*self._tile_size
        y_coord = y*self._tile_size

        surface = pygame.Surface((self._tile_size,self._tile_size))
        surface.set_alpha(alpha) # alpha level
        pygame.draw.rect(surface, color, surface.get_rect())
        self._display.blit(surface, (x_coord, y_coord,self._tile_size,self._tile_size) )
    
    def _draw_charging_dock(self):
        try:
            x, y = self._environment.get_charging_dock_location()
            self._draw_tile(x, y, MAGENTA)
        except:
            # using the environment without charging dock
            pass
    
    def _draw_vacuum_agent(self):
        color = GREEN
        p = self._environment.get_percepts()
        pos = (p['location-sensor'][0], p['location-sensor'][1])
        agent_state = self._environment.get_agent_state()
        if agent_state['collided'] is not None:
            color = YELLOW

        self._draw_tile(pos[0], pos[1], color)

    def _draw_dirt(self):
        dirt_coords = self._environment.get_dirt_coords()
        for coord in dirt_coords:
            self._draw_tile(coord[0], coord[1], RED)
    
    def _draw_walls(self):
        walls_coords = self._environment.get_walls_coords()
        for coord in walls_coords:
            self._draw_tile(coord[0], coord[1], WHITE)
        
        # draw as a wall the rest of the window outside the boundings
        # of the environment (if not multiple of the tile size)
        if self._display_size[0] % self._tile_size > 0:
            x_coord = self._environment.get_width()*(self._tile_size - 1)
            y_coord = 0
            pygame.draw.rect(self._display, WHITE, pygame.Rect(x_coord, y_coord, self._display_size[0] - x_coord, self._display_size[1]))
        if self._display_size[1] % self._tile_size > 0:
            x_coord = 0
            y_coord = self._environment.get_height()*(self._tile_size - 1)
            pygame.draw.rect(self._display, WHITE, pygame.Rect(x_coord, y_coord, self._display_size[0], self._display_size[1] - y_coord))
    
    def _draw_explored(self):
        explored = self._environment.get_explored_tiles_coords()
        for coord in explored:
            self._draw_tile(coord[0], coord[1], BLUE, 80)
    
    def _draw_score_bar(self):
        surface = pygame.Surface((DISPLAY_WIDTH,SCORE_BAR_HEIGHT))
        pygame.draw.rect(surface, WHITE, surface.get_rect())
        self._display.blit(surface, (0, DISPLAY_HEIGHT,DISPLAY_WIDTH,SCORE_BAR_HEIGHT) )
        font = pygame.font.SysFont(self._font, 15)
        score_text_str = "Score: {0}".format(self._environment.get_score())
        score_text_size = font.size(score_text_str)
        score_text = font.render(score_text_str, True, BLACK)
        battery_text_str = "Battery level: {0}%".format(self._agent.get_battery_level())
        battery_text_size = font.size(battery_text_str)
        battery_text = font.render(battery_text_str, True, BLACK)
        white_space = DISPLAY_WIDTH - score_text_size[0] - battery_text_size[0]
        padding_top = int((SCORE_BAR_HEIGHT - score_text_size[1]) / 2)
        padding_side = int(white_space * 0.25)
        central_padding = white_space - (padding_side * 2)
        self._display.blit(score_text, (padding_side, DISPLAY_HEIGHT+padding_top))
        self._display.blit(battery_text, (padding_side + score_text_size[0] + central_padding, DISPLAY_HEIGHT+padding_top))

    def _draw_frame(self):
        self._reset_bg()
        self._draw_walls()
        self._draw_explored()
        self._draw_dirt()
        self._draw_charging_dock()
        self._draw_vacuum_agent()
        self._draw_score_bar()

    def main(self):
        running = True

        while running:
            # update frame
            self._draw_frame()

            #Event Tasking
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    running = False
                    quit()
            
            # updating game with one step
            # sense - think - act
            self._play_step()

            # Update the clock and display
            pygame.display.update()
            window_clock.tick(5)
