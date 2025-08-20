from une_ai.assignments import SnakeEnvironment

import pygame
import math
import random

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

pygame.init()
DISPLAY_WIDTH = 640
DISPLAY_HEIGHT = 480
SCORE_BAR_HEIGHT = 40
GAME_OVER_HEIGHT = 40
TILE_SIZE = 10

window = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT+SCORE_BAR_HEIGHT))
pygame.display.set_caption('Assignment 1 - Snake')
window_clock = pygame.time.Clock()

class SnakeGame:

    def __init__(self, snake_agent, display_w=DISPLAY_WIDTH, display_h=DISPLAY_HEIGHT, tile_size=TILE_SIZE, max_time=60, tick=5):
        self._tile_size = tile_size
        self._display = window
        self._display_size = (display_w, display_h)
        w_env = math.floor(display_w / self._tile_size)
        h_env = math.floor(display_h / self._tile_size)
        self._environment = SnakeEnvironment(w_env, h_env, max_time)
        self._agent = snake_agent
        # update sensors with initial state
        self._agent.sense(self._environment)
        self._tick = tick

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
    
    def _draw_snake(self):
        if self._environment.is_game_over() and self._environment.get_time() > 0:
            color = YELLOW
        else:
            color = GREEN
        percepts = self._environment.get_percepts()
        snake_body = percepts['body-sensor']
        for segment in snake_body:
            self._draw_tile(segment[0], segment[1], color)

    def _draw_food(self):
        food_coords = self._environment.get_food_coords()
        for coord in food_coords:
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
    
    def _draw_score_bar(self):
        surface = pygame.Surface((DISPLAY_WIDTH,SCORE_BAR_HEIGHT))
        pygame.draw.rect(surface, WHITE, surface.get_rect())
        self._display.blit(surface, (0, DISPLAY_HEIGHT,DISPLAY_WIDTH,SCORE_BAR_HEIGHT) )
        font = pygame.font.SysFont(self._font, 15)
        score_text_str = "Score: {0}".format(self._environment.get_score())
        score_text_size = font.size(score_text_str)
        score_text = font.render(score_text_str, True, BLACK)
        if self._environment.is_game_over():
            time = 0
        else:
            time = int(self._environment.get_time())
        time_text_str = "Time: {0}".format(time)
        time_text_size = font.size(time_text_str)
        time_text = font.render(time_text_str, True, BLACK)
        padding_top = int((SCORE_BAR_HEIGHT - score_text_size[1]) / 2)
        white_space = DISPLAY_WIDTH - score_text_size[0] - time_text_size[0]
        padding_side = int(white_space * 0.25)
        padding_central = white_space - 2 * padding_side
        self._display.blit(score_text, (padding_side, DISPLAY_HEIGHT+padding_top))
        self._display.blit(time_text, (padding_side + score_text_size[0] + padding_central, DISPLAY_HEIGHT+padding_top))
    
    def _draw_game_over(self):
        surface = pygame.Surface((DISPLAY_WIDTH,DISPLAY_HEIGHT))
        surface.set_alpha(60)
        pygame.draw.rect(surface, WHITE, surface.get_rect())
        y_pos = int((DISPLAY_HEIGHT-GAME_OVER_HEIGHT)/2)
        self._display.blit(surface, (0, 0, DISPLAY_WIDTH,DISPLAY_HEIGHT) )
        font = pygame.font.SysFont(self._font, 30)
        game_over_text = font.render("GAME OVER", True, RED)
        self._display.blit(game_over_text, (int((DISPLAY_WIDTH-150)/2), int((DISPLAY_HEIGHT-30)/2), 100, 30))

    def _draw_frame(self):
        self._reset_bg()
        self._draw_walls()
        self._draw_food()
        self._draw_snake()
        self._draw_score_bar()
        if self._environment.is_game_over():
            self._draw_game_over()

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
            if not self._environment.is_game_over():
                self._play_step()

            # Update the clock and display
            pygame.display.update()
            window_clock.tick(self._tick)
            elapsed = window_clock.get_time() / 1000
            self._environment.tick(elapsed)
