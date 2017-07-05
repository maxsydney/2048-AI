import numpy as np 
import time
import math

class Game_tree(object):
    '''
    Constructs and stores the tree of possible game states for the online game 2048
    '''

    def __init__(self, depth, state, player=1, move=None):
        self.depth = depth
        self.player = player
        self.state = state
        self.children = []
        self.score = None
        self.move = move
        self.over = False
        if np.count_nonzero(state) == 16:
            self.over = self.check_game_over()
        self.build_game_tree(self.player)

    def build_game_tree(self, player):
        '''
        Recursively construct the tree of possible game states
        '''
        if self.depth >= 0:
            if player == -1:
                zero_indices = np.argwhere(self.state == 0)
                for index in zero_indices:
                    new_state = np.copy(self.state)
                    new_state[index[0], index[1]] = 2
                    self.children.append(Game_tree(self.depth-1, new_state, self.player*-1))
            else:
                moves = ('right', 'down', 'up')
                for move in moves:
                    valid = self.is_valid(move)
                    if move in ('right', 'left') and valid:
                        new_state = self.explore_horizontal_move(self.state, move)
                        self.children.append(Game_tree(self.depth-1, new_state, self.player*-1, move))
                    elif move in ('up', 'down') and valid:
                        new_state = self.explore_vertical_move(self.state, move)
                        self.children.append(Game_tree(self.depth-1, new_state, self.player*-1, move))

    def is_valid(self, move):
        if move in ('left', 'right'):
            new_state = self.explore_horizontal_move(self.state, move)
        else:
            new_state = self.explore_vertical_move(self.state, move)
        if np.array_equal(self.state, new_state):
            return False
        return True

    def explore_horizontal_move(self, state, direction):
        '''
        Returns the game state after playing a right move
        '''
        if direction not in ('left', 'right'):
            raise NameError

        projected_state = np.copy(state)
        for row_index, row in enumerate(projected_state):
            if not self.has_adjacent_cells(row):
                row = row[row != 0]
            else:
                row = self.merge_cells(row, direction)
            pad = (4-len(row)) * [0]
            if direction == 'right':
                projected_state[row_index] = np.concatenate((pad, row))
            elif direction == 'left':
                projected_state[row_index] = np.concatenate((row, pad))
        return projected_state

    def explore_vertical_move(self, state, direction):
        """
        TODO: sliding up on col with [0 2 2 2]' merges wrong cells
        """
        if direction not in ('up', 'down'):
            raise NameError
        projected_state = np.copy(state)
        projected_state = np.transpose(projected_state)

        lookup = {'up': 'right',
                  'down': 'left'}
        for row_index, row in enumerate(projected_state):
            if not self.has_adjacent_cells(row):
                row = row[row != 0]
            else:
                row = self.merge_cells(row, lookup[direction])
            pad = (4-len(row)) * [0]
            if direction == 'down':
                projected_state[row_index] = np.concatenate((pad, row))
            elif direction == 'up':
                projected_state[row_index] = np.concatenate((row, pad))

        return np.transpose(projected_state)

    def merge_cells(self, row, move):
        '''
        Calculates game state after cells have been merged
        '''
        if move in ('right', 'up'):
            row = row[::-1]
        row = row[row != 0]
        row = self._merge_helper(row)
        if move in ('right', 'up'):
            row = row[::-1]
        return row

    def _merge_helper(self, row):
        '''
        Recursively merges cells until no more merges are possible
        '''
        for i, item in enumerate(row[:-1]):
            if item == row[i+1]:
                return np.concatenate((row[:i], [2*item], self._merge_helper(row[i+2:])))
        return row

    def has_adjacent_cells(self, row):
        '''
        Determines if there are any adjacent cells eligible for merging in row/column
        >>> game = Game()
        >>> game.has_adjacent_cells(np.array([1, 2, 3, 4]))
        False
        >>> game.has_adjacent_cells(np.array([1, 2, 2, 4]))
        True
        >>> game.has_adjacent_cells(np.array([2, 2, 3, 4]))
        True
        >>> game.has_adjacent_cells(np.array([4, 2, 3, 4]))
        False
        '''
        row = row[row != 0]
        for index, cell in enumerate(row):
            if len(row[row == cell]) > 1:   # More than one instance of cell in row
                if index > 0:
                    if row[index-1] == cell:
                        return True
                if index < len(row) - 1:
                    if row[index+1] == cell:
                        return True
        return False
    
    def check_game_over(self):
        up_state = self.explore_vertical_move(self.state, 'up')
        down_state = self.explore_vertical_move(self.state, 'down')
        right_state = self.explore_horizontal_move(self.state, 'right')

        if ((self.state == up_state) == (down_state == right_state)).all():
            return True
        return False

class Minimax(object):
    '''
    Applies a minimax search to the game tree
    '''
    def __init__(self, game_tree):
        self.game_tree = game_tree

    def search(self):
        '''
        Minimax search
        '''
        best_val = self.max_value(self.game_tree)
        best_move = None
        for child in self.game_tree.children:
            #print('Move {} has a score of {}'.format(child.move, child.score), flush=True)
            if child.score == best_val:
                best_move = child.move
                break
        return best_move

    def max_value(self, node):
        if len(node.children) == 0:
            return self.get_score(node)

        infinity = float('inf')
        max_val = -infinity

        #print('Executing max search, values are')
        for child in node.children:
            #max_val = max(max_val, self.min_value(child))
            max_val = max(max_val, self.expecti(child))
           # print(max_val, flush=True)
        node.score = max_val
        return max_val

    def min_value(self, node):
        '''
        Minimiser for minimax algorithm
        '''
        if len(node.children) == 0:
            return self.get_score(node)

        infinity = float('inf')
        min_val = infinity
        for child in node.children:
            min_val = min(min_val, self.max_value(child))
        node.score = min_val
        return min_val
    
    def expecti(self, node):
        '''
        Minimiser for minimax algorithm
        '''
        if len(node.children) == 0:
            return self.get_score(node)

        child_values = []
        for child in node.children:
            child_values.append(self.max_value(child))
        expected_val = sum(child_values) / len(child_values)
        node.score = expected_val
        return expected_val


    def get_score(self, node):
        '''
        Main game heuristic. Reward snake structure and having largest tile in bottom right
        '''
        snake = []
        for i, row in enumerate(np.transpose(node.state)):
            snake.extend(reversed(row) if i % 2 == 0 else row)
        snake = snake[::-1]
        m = np.amax(node.state)
        score = sum(val/10 ** index for index, val in enumerate(snake)) \
        - math.pow((node.state[3][3] != m)*abs(node.state[3][3] - m), 2)
        return score



if __name__ == '__main__':
    '''
    Mainly debugging code. Not called when minimax imported to controller
    '''
    s = np.array([[0, 0, 0, 2],
                  [0, 0, 2, 8],
                  [0, 0, 4, 2],
                  [0, 0, 8, 32]])
    t1 = time.time()
    n = Game_tree(5, s)
    t2 = time.time()
    print("Built tree in {:.2f} seconds".format(t2 - t1))
    m = Minimax(n)
    t1 = time.time()
    m.search()
    t2 = time.time()
    print("Executed search in {:.2f} seconds".format(t2 - t1))
    # d = 2
    # start = time.time()
    # n = Game_tree(d, s, 1)
    # end = time.time()

    # print("Simulated {} layers in {:.2f}s".format(d, end-start))
    # print(len(n.children[1].children[0].children))

