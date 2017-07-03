from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import numpy as np
import minimax
import time


class Game(object):

    def __init__(self):
        self.browser = webdriver.Firefox()
        self.browser.get("https://gabrielecirulli.github.io/2048/")
        self.state = np.array([[0, 0, 0, 0],
                               [0, 0, 0, 0],
                               [0, 0, 0, 0],
                               [0, 0, 0, 0]])

    def play(self):
        '''
        Plays one move - to be completed
        '''
        t1 = time.time()
        move = self.calculate_move()
        t2 = time.time()
        print('Search took {:.2f} seconds'.format(t2-t1))
        print('Executing {} move'.format(move))
        self.execute_move(move)

    def execute_move(self, move):
        elem = self.browser.find_element_by_class_name('game-container')
        if move == 'right':
            elem.send_keys(Keys.ARROW_RIGHT)
        elif move == 'down':
            elem.send_keys(Keys.ARROW_DOWN)
        elif move == 'up':
            elem.send_keys(Keys.ARROW_UP)

    def read_state(self):
        '''
        Examines game current game state and returns it as a numpy array
        '''

        elem = self.browser.find_element_by_class_name("tile-container")
        tiles = elem.find_elements_by_class_name("tile")
        active_tiles = [tile.get_attribute("class") for tile in tiles]
        for tile in active_tiles:
            tile = tile.split(" ")
            val_tile = tile[1].split("-")
            value = val_tile[1]
            row = tile[2][-1]
            col = tile[2][-3]
            self.state[int(row)-1][int(col)-1] = int(value)

    def calculate_move(self, depth=4):
        game_tree = minimax.Game_tree(depth, self.state)
        ai = minimax.Minimax(game_tree)
        move = ai.search()
        return move

if __name__ == "__main__":
    import doctest
    doctest.testmod()

game = Game()

for i in range(20):
    game.read_state()
    game.play()
