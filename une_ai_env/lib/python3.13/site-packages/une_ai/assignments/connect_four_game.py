import pygame
import numpy as np

BLACK = (30, 30, 30)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GRAY = (125, 125, 125)
BLUE = (10, 20, 200)
GREEN = (255, 125, 125)

DISPLAY_WIDTH = 640
DISPLAY_HEIGHT = 500
POWERUPS_BAR_HEIGHT = 35
SCORE_BAR_HEIGHT = 35
INFO_BAR_HEIGHT = 35
BOX_SIZE = 60

class ConnectFourGame:

    def __init__(self, agent_Y, agent_R, environment, is_debugging=False, display_w=DISPLAY_WIDTH, display_h=DISPLAY_HEIGHT, box_size=BOX_SIZE):
        assert type(agent_R).__name__ == 'ConnectFourPlayer', "agent_R must be an instance of the class ConnectFourPlayer"
        assert type(agent_Y).__name__ == 'ConnectFourPlayer', "agent_Y must be an instance of the class ConnectFourPlayer"
        assert type(environment).__name__ == 'ConnectFourEnvironment', "environment must be an instance of a subclass of the class ConnectFourBaseEnvironment"

        pygame.init()
        window = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT+SCORE_BAR_HEIGHT))
        pygame.display.set_caption('Connect Four')
        window_clock = pygame.time.Clock()

        self._box_size = box_size
        self._display = window
        self._window_clock = window_clock
        self._display_size = (display_w, display_h)
        self._agents = {}
        self._agents['Y'] = agent_Y
        self._agents['R'] = agent_R
        self._environment = environment
        self._last_action = ""
        self._is_debugging = is_debugging

        game_state = self._environment.get_game_state()
        game_board = game_state['game-board']
        self._n_cols = game_board.get_width()
        self._n_rows = game_board.get_height()
        self._padding_left = int((self._display_size[0] - self._n_cols*self._box_size)/2)
        self._padding_top = int((self._display_size[1] - self._n_rows*self._box_size)/2)

        self._coordinates = np.array([[None]*self._n_cols]*self._n_rows)
        for y in range(self._n_rows):
            for x in range(self._n_cols):
                self._coordinates[y, x] = (x, y)

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
        game_state = self._environment.get_game_state()
        if type(self._environment).is_terminal(game_state):
            return
        
        cur_colour = type(self._environment).turn(game_state)
        
        # SENSE
        self._agents[cur_colour].sense(self._environment)
        # THINK
        actions = self._agents[cur_colour].think()
        player = 'Yellow' if cur_colour == 'Y' else 'Red'
        if len(actions) != 0:
            self._last_action = "{0} player played the move '{1}'".format(player, actions[0])
        # ACT
        self._agents[cur_colour].act(actions, self._environment)
    
    def _reset_bg(self):
        self._display.fill(BLACK)
    
    def _draw_box(self, x, y, color, alpha = 255):
        game_state = self._environment.get_game_state()
        game_board = game_state['game-board']
        x_coord = self._padding_left + x*self._box_size
        y_coord = self._padding_top + y*self._box_size

        surface = pygame.Surface((self._box_size,self._box_size))
        surface.set_alpha(alpha) # alpha level
        pygame.draw.rect(surface, color, surface.get_rect())
        self._display.blit(surface, (x_coord, y_coord))

        cur_checker = game_board.get_item_value(x, y)
        
        if cur_checker == 'Y':
            checker_color = YELLOW
        elif cur_checker == 'R':
            checker_color = RED
        elif cur_checker == 'W':
            checker_color = GRAY
        else:
            # no checker
            checker_color = WHITE
        checker_surface = pygame.Surface((self._box_size,self._box_size))
        checker_surface.set_alpha(255) # alpha level
        checker_surface.fill(color)
        radius = int((self._box_size/2)*0.8)
        center = int(self._box_size/2)
        pygame.draw.circle(checker_surface, checker_color, (center, center), radius)
        self._display.blit(checker_surface, (x_coord, y_coord))
    
    def _draw_board(self):
        game_state = self._environment.get_game_state()
        game_board = game_state['game-board']
        winner = type(self._environment).get_winner(game_state)
        winning_coords = []
        max_diagonals = game_board.get_width() + game_board.get_height() - 7
        diagonal_idx = lambda normalised_idx: normalised_idx - int(max_diagonals / 2) + 1
        if winner is not None:
            openings = type(self._environment).get_openings(game_board, winner)
            for k, l_openings in openings.items():
                for t in l_openings:
                    if t[1] == 4:
                        if k == 'horizontals':
                            winning_coords = self._coordinates[game_board.get_height() -1 - t[0], :].tolist()
                            break
                        elif k == 'verticals':
                            winning_coords = self._coordinates[:, t[0]].tolist()
                            break
                        elif k == 'left-diagonals':
                            winning_coords = np.diagonal(self._coordinates, diagonal_idx(t[0])).tolist()
                            break
                        else:
                            winning_coords = np.diagonal(np.fliplr(self._coordinates), diagonal_idx(t[0])).tolist()
                            break
        for i in range(0, self._n_cols):
            for j in range(0, self._n_rows):
                if (i, j) in winning_coords:
                    color = GREEN
                else:
                    color = BLUE
                self._draw_box(i, j, color)
    
    def _draw_text(self, text_message, padding_top, orientation, font_size = 20):
        font = pygame.font.SysFont(self._font, font_size)
        text_size = font.size(text_message)
        text = font.render(text_message, True, WHITE)
        top = self._padding_top + self._n_rows*self._box_size + 10 + padding_top
        if orientation == 'center':
            left = int((self._display_size[0] - text_size[0])/2)
        elif orientation == 'left':
            left = self._padding_left
        elif orientation == 'right':
            left = self._display_size[0] - text_size[0] - self._padding_left
        else:
            left = 0
        self._display.blit(text, (left, top))
    
    def _draw_game_over(self):
        game_state = self._environment.get_game_state()
        game_board = game_state['game-board']
        colour = type(self._environment).get_winner(game_state)
        if colour == 'Y':
            winner = 'Yellow player'
        elif colour == 'R':
            winner = 'Red player'
        else:
            winner = None
        
        if winner is not None:
            text = "{0} won!".format(winner)
        else:
            text = "Tie!"
        
        padding_top = POWERUPS_BAR_HEIGHT + INFO_BAR_HEIGHT
        self._draw_text(text, padding_top, 'center')
    
    def _draw_powerups(self):
        game_state = self._environment.get_game_state()
        powerup_y = game_state['power-up-Y']
        powerup_r = game_state['power-up-R']

        self._draw_text("Yellow player power-up: {0}".format(powerup_y), 0, 'left', 15)
        self._draw_text("Red player power-up: {0}".format(powerup_r), 0, 'right', 15)
    
    def _draw_frame(self):
        self._reset_bg()
        self._draw_board()
        self._draw_powerups()
        self._draw_text("Last action: {0}".format(self._last_action), POWERUPS_BAR_HEIGHT, 'left', 15)
        if type(self._environment).is_terminal(self._environment.get_game_state()):
            self._draw_game_over()
        else:
            colour = type(self._environment).turn(self._environment.get_game_state())
            player = "Yellow" if colour == 'Y' else "Red"
            self._draw_text("Player Turn: {0}".format(player), POWERUPS_BAR_HEIGHT + INFO_BAR_HEIGHT, 'left', 15)
    
    def key_to_action(key):
        if key >= pygame.K_1 and key <= pygame.K_7:
            col = key - pygame.K_1
            return 'release-{0}'.format(col)
        else:
            for col, k in enumerate(['q', 'w', 'e', 'r', 't', 'y', 'u']):
                if key == getattr(pygame, 'K_{0}'.format(k)):
                    return 'popup-{0}'.format(col)
            for col, k in enumerate(['a', 's', 'd', 'f', 'g', 'h', 'j']):
                if key == getattr(pygame, 'K_{0}'.format(k)):
                    return 'use-power-up-{0}'.format(col)
        
        return None
    
    def wait_for_user_input():
        action = None
        while action is None:
            event = pygame.event.wait()
            if event.type == pygame.KEYDOWN:
                action = ConnectFourGame.key_to_action(event.key)
        
        return action

    def main(self):
        running = True

        while running:
            # update frame
            self._draw_frame()
            pygame.display.update()
            self._window_clock.tick(1)
            #Event Tasking
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    running = False
                    quit()

            
            # updating game with one step
            # sense - think - act
            self._play_step()

            if self._is_debugging:
                pygame.time.delay(2000)
            
