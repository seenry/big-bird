# An example how how Big Bird can be implemented in order
# to learn how to play "snake," everyone's favorite game
# on Nokia phones of yore.

import bigbird
import numpy as np

# Big Bird Parameter Configuration
size = 2000
lnc = [10, 7, 7, 7, 3]
m_r8 = 0.3
step_ratio = 1/3.6
reinit_r = 0.015
imm = int(0.01 * size)

max_generation = 300

print('Initializing Population\n')
population = bigbird.SimplePopulation(size, lnc)

# Snake Game Configuration
board_size = 21

def generate_pellet(board):
    if len(np.where(board==0)[0]) == 0:
        return (-1, -1)
    open_row = np.where(board == 0)[0]
    open_col = np.where(board == 0)[1]
    choice = np.random.randint(0, len(open_col))
    return (open_row[choice], open_col[choice])

def update_board(board_size, py, px, snek):
    board = np.zeros([board_size, board_size], dtype=int)
    board[py][px] = 2
    for i in snek.coords:
        board[i[0]][i[1]] = 1
    return board

def get_input(board, py, px, snek):
    y = snek.coords[-1][0]
    x = snek.coords[-1][1]
    
    # 0: Danger in front; 1, 2: Danger to sides; 3: current y-dir; 4: current x-dir; 5: current y; 6: current x; 7: angle to pellet; 8: bias;
    input = np.zeros(10)
    if x == 0:
        if snek.x_dir == -1:
            input[0] = 1
        if snek.y_dir == -1:
            input[1] = 1
        elif snek.y_dir == 1:
            input[2] = 1
    elif x == board_size - 1:
        if snek.x_dir == 1:
            input[0] = 1
        if snek.y_dir == -1:
            input[2] = 1
        elif snek.y_dir == 1:
            input[1] = 1
    if y == 0:
        if snek.y_dir == -1:
            input[0] = 1
        if snek.x_dir == -1:
            input[2] = 1
        elif snek.x_dir == 1:
            input[1] = 1
    elif y == board_size - 1:
        if snek.y_dir == 1:
            input[0] = 1
        if snek.x_dir == -1:
            input[1] = 1
        elif snek.x_dir == 1:
            input[2] = 1
    if input[0] == 0 and (board[y + snek.y_dir][x + snek.x_dir] == 1):
        input[0] = 1
    if input[1] == 0 and (board[y + (snek.y_dir * snek.x_dir) - snek.x_dir][x + (snek.x_dir * snek.y_dir) + snek.y_dir] == 1):
        input[1] = 1
    if input[2] == 0 and (board[y + (snek.y_dir * snek.x_dir) + snek.x_dir][x + (snek.x_dir * snek.y_dir) - snek.y_dir] == 1):
        input[2] = 2
    input[3] = snek.y_dir
    input[4] = snek.x_dir
    input[5] = y / len(board)
    input[6] = x / len(board)
    input[7] = np.sqrt((x - px)**2 + (y - py)**2) / np.sqrt(2 * (len(board))**2)
    input[8] = np.arctan2(py - y, px - x) / np.pi
    input[9] = 1

    return np.vstack(input)

class Snake:
    def __init__(self):
        self.y_dir = 0
        self.x_dir = 1
        self.length = 5
        self.coords = [(int(np.floor(board_size/2)), 2 + i) for i in range(self.length)]  # (y, x)
        self.dead = False

    def update_direction(self, turn):   # TURN LEFT = -1. TURN RIGHT = 1
        if turn:
            new_y_dir = (self.y_dir * self.x_dir) + (self.x_dir * turn)
            new_x_dir = (self.x_dir * self.y_dir) - (self.y_dir * turn)
            self.y_dir = new_y_dir
            self.x_dir = new_x_dir

    def move(self, board):
        y = self.coords[-1][0]
        x = self.coords[-1][1]
        
        # Check for death
        if (x == 0 and self.x_dir == -1) or (x == board_size - 1 and self.x_dir == 1) or (y == 0 and self.y_dir == -1) or (y == board_size - 1 and self.y_dir == 1):
            self.dead = True
            return
        if len(self.coords) != len(set(self.coords)):
            self.dead = True
            return

        # Check for pellet
        if board[y + self.y_dir][x + self.x_dir] == 2:
            self.length += 1

        # Update Coordinates
        self.coords.append((y + self.y_dir, x + self.x_dir))
        while len(self.coords) > self.length:
            self.coords = self.coords[1:]

    def reset(self):
        self.y_dir = 0
        self.x_dir = 1
        self.length = 5
        self.coords = [(int(np.floor(board_size/2)), 2 + i) for i in range(self.length)]  # (y, x)
        self.dead = False

# Evolutionary Algorithm Implementation
print('Starting Simulation\n')
snake = Snake()
for generation in range(max_generation):
    print('Current Generation: ' + str(generation + 1))
    tracker = 0     # Tracks which no. bird is currently being evaluated
    for bird in population.birds:
        board = np.zeros([board_size, board_size], dtype=int)

        # Create a pellet that isn't immediately in front of the initialized snake
        (py, px) = (int(np.floor(board_size/2)), 1 + snake.length)
        while py == int(np.floor(board_size/2)):
            (py, px) = generate_pellet(board)

        # No. of pellets collected by snake
        pellets = 0

        tracker += 1
        print('Current Bird: ' + str(tracker) + '/' + str(size) + '   ', end='\r')
        bird.fitness = 0.1

        # Reference point to determine if the snake has eaten
        progress = snake.length + 1 - 1
        stalemate = 0
        while not snake.dead:
            # Kills snake if it hasn't eaten in a long time
            if progress == snake.length:
                stalemate += 1
            else:
                progress = snake.length + 1 - 1
                stalemate = 0
            if stalemate > board_size**2 + 2 * board_size:
                break

            board = update_board(board_size, py, px, snake)
            # If there's no pellet, create a new one. Also update fitness.
            if not 2 in board:
                (py, px) = generate_pellet(board)
                if py == -1:
                    break
                bird.fitness += (350 / (1 + np.exp(-pellets))) - 150
                pellets += 1

            # Evaluate network and act on output
            input = get_input(board, py, px, snake)
            output = bird.eval(input)
            decision = output.tolist().index(max(output)) - 1
            snake.update_direction(decision)
            snake.move(board)
        snake.reset()
    
    # Collect statistical data on generation fitness
    ranked = sorted(population.birds, key=lambda x: x.fitness)
    champ = ranked[-1]
    median = ranked[int(np.floor(len(ranked)/2))]
    sped = ranked[0]
    mean = 0
    for i in population.birds:
        mean += i.fitness
    mean /= size

    space = ' '
    print(40 * space, end='\r')

    print('Highest Fitness: ' + str(np.round(champ.fitness, 4)))
    print('Lowest  Fitness: ' + str(np.round(sped.fitness, 4)))
    print('Average Fitness: ' + str(np.round(mean, 4)))
    print('Median  Fitness: ' + str(np.round(median.fitness, 4)))

    champ.save(fname='./hall-of-fame/champ-' + str(generation) + '.json')

    # Initialize next generation
    print('Storing...',end='\r')
    population.store(imm)
    print('Breeding...',end='\r')
    population.breed()
    print('Mutating...',end='\r')
    population.mutate(m_r8, step_ratio, reinit=reinit_r)
    print('Retrieving...',end='\r')
    population.retrieve()

    print(40 * space)