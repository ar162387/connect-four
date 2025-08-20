import pygame

from une_ai.models import GridMap

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

DISPLAY_WIDTH = 320
DISPLAY_HEIGHT = 240
SCORE_BAR_HEIGHT = 40
BOX_SIZE = 50

class TicTacToeGame:

    def __init__(self, agent_X, agent_O, environment, board_size=3, display_w=DISPLAY_WIDTH, display_h=DISPLAY_HEIGHT, box_size=BOX_SIZE):
        assert type(agent_X).__name__ == 'TicTacToePlayer', "agent_X must be an instance of a the class TicTacToePlayer"
        assert type(agent_O).__name__ == 'TicTacToePlayer', "agent_O must be an instance of the class TicTacToePlayer"
        assert type(environment).__name__ == 'TicTacToeGameEnvironment', "The parameter environment must be an instance of the class TicTacToeGameEnvironment"
        
        pygame.init()
        window = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT+SCORE_BAR_HEIGHT))
        pygame.display.set_caption('Tic Tac Toe')
        self._window_clock = pygame.time.Clock()

        self._box_size = box_size
        self._display = window
        self._display_size = (display_w, display_h)
        self._agents = {}
        self._agents['X'] = agent_X
        self._agents['O'] = agent_O
        self._environment = environment
        self._board_size = board_size
        
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
        
        try:
            cur_marker = type(self._environment).turn(game_state)
        except:
            print("Error. The game environment class does not return a correct game state. Skipping updating the game state")
            return
        
        # SENSE
        self._agents[cur_marker].sense(self._environment)
        # THINK
        actions = self._agents[cur_marker].think()
        # ACT
        self._agents[cur_marker].act(actions, self._environment)
    
    def _reset_bg(self):
        self._display.fill(BLACK)
    
    def _draw_box(self, x, y, color, alpha = 255):
        font = pygame.font.SysFont(self._font, 30)
        game_state = self._environment.get_game_state()
        n_cells = self._board_size
        padding_left = int((self._display_size[0] - n_cells*self._box_size)/2)
        padding_top = int((self._display_size[1] - n_cells*self._box_size)/2)
        x_coord = padding_left + x*self._box_size
        y_coord = padding_top + y*self._box_size

        surface = pygame.Surface((self._box_size-2,self._box_size-2))
        surface.set_alpha(alpha) # alpha level
        pygame.draw.rect(surface, color, surface.get_rect())
        self._display.blit(surface, (x_coord, y_coord) )

        if isinstance(game_state, dict) and 'game-board' in game_state.keys():
            game_board = game_state['game-board']
        else:
            print("Error. The game environment class does not return a correct game state. Drawing an empty game board.")
            game_board = GridMap(self._board_size, self._board_size, None)

        cur_mark = game_board.get_item_value(x, y)
        if cur_mark != None:
            color = RED if cur_mark == 'X' else BLUE
            text_size = font.size(cur_mark)
            mark_text = font.render(cur_mark, True, color)
            top = y_coord + int((BOX_SIZE - text_size[1])/2)
            left = x_coord + int((BOX_SIZE - text_size[0])/2)
            self._display.blit(mark_text, (left, top))
    
    def _draw_board(self):
        n_cells = self._board_size
        for i in range(0, n_cells):
            for j in range(0, n_cells):
                self._draw_box(j, i, WHITE)
    
    def _draw_game_over(self):
        winner = type(self._environment).get_winner(self._environment.get_game_state())
        
        if winner is not None:
            text = "Player {0} won!".format(winner)
        else:
            text = "Tie!"
        
        n_cells = self._board_size
        font = pygame.font.SysFont(self._font, 20)
        text_size = font.size(text)
        game_over_text = font.render(text, True, WHITE)
        padding_top = int((self._display_size[1] - n_cells*self._box_size)/2)
        x_coord = int((self._display_size[0] - text_size[0])/2)
        y_coord = padding_top + n_cells*self._box_size + 30
        self._display.blit(game_over_text, (x_coord, y_coord))
                
    def _draw_frame(self):
        self._reset_bg()
        self._draw_board()
        if type(self._environment).is_terminal(self._environment.get_game_state()):
            self._draw_game_over()

    def main(self):
        running = True

        while running:
            # update frame
            self._draw_frame()
            # Update the clock and display
            pygame.display.update()

            #Event Tasking
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    running = False
                    quit()
            
            # updating game with one step
            # sense - think - act
            self._play_step()
            
            self._window_clock.tick(1)
