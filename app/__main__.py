import pygame
import random
import config

from services.block_set import BlockSet

pygame.font.init()

# SHAPE FORMATS
shapes = [config.S, config.Z, config.I, config.O, config.J, config.L, config.T]
qops_shape = []
shape_colors = [(0, 255, 0), (255, 0, 0), (0, 255, 255), (255, 255, 0), (255, 165, 0), (0, 0, 255), (128, 0, 128)]

quantum_operator = ["X","Y","Z","Rx","Ry","Rz","H","I"]

possible_colors = {
    'X': (0, 255, 0),
    'Y': (255, 0, 0),
    'Z': (0, 255, 255),
    'Rx': (255, 255, 0),
    'Ry': (255, 165, 0),
    'Rz': (0, 0, 255),
    'H': (128, 0, 128),
    'I': (128, 128, 0),
}

def colours_to_qgates(colours_list):
    qgates = []
    key_list = list(possible_colors.keys())
    val_list = list(possible_colors.values())
    for i in range(len(colours_list)):
        if (colours_list[i] in val_list):
            position = val_list.index(colours_list[i])
            qgates.append(key_list[position])
    return qgates

class Piece(object):
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.operator = config.qops[shapes.index(shape)]
        self.color = shape_colors[shapes.index(shape)]
        self.rotation = 0
        self.BlockSet = BlockSet()


def create_grid(locked_pos={}):  # *
    grid = [[(0,0,0) for _ in range(10)] for _ in range(20)]

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if (j, i) in locked_pos:
                c = locked_pos[(j,i)]
                grid[i][j] = c
    return grid


def convert_shape_format(shape):
    positions = []
    format = shape.shape[shape.rotation % len(shape.shape)]

    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                positions.append((shape.x + j, shape.y + i))

    for i, pos in enumerate(positions):
        positions[i] = (pos[0] - 2, pos[1] - 4)

    return positions


def valid_space(shape, grid):
    accepted_pos = [[(j, i) for j in range(10) if grid[i][j] == (0,0,0)] for i in range(20)]
    accepted_pos = [j for sub in accepted_pos for j in sub]

    formatted = convert_shape_format(shape)

    for pos in formatted:
        if pos not in accepted_pos:
            if pos[1] > -1:
                return False
    return True


def check_lost(positions):
    for pos in positions:
        x, y = pos
        if y < 1:
            return True

    return False


def get_shape():
    return Piece(5, 0, random.choice(shapes))


def draw_text_middle(surface, text, size, color):
    font = pygame.font.SysFont("comicsans", size, bold=True)
    label = font.render(text, 1, color)

    surface.blit(label, (config.top_left_x + config.play_width /2 - (label.get_width()/2), config.top_left_y + config.play_height/2 - label.get_height()/2))


def draw_grid(surface, grid):
    sx = config.top_left_x
    sy = config.top_left_y

    for i in range(len(grid)):
        pygame.draw.line(surface, (128,128,128), (sx, sy + i*config.block_size), (sx+config.play_width, sy+ i*config.block_size))
        for j in range(len(grid[i])):
            pygame.draw.line(surface, (128, 128, 128), (sx + j*config.block_size, sy),(sx + j*config.block_size, sy + config.play_height))


def clear_row_combinations(grid, locked):

    inc = 0
    for i in range(len(grid)-1, -1, -1):
        row = grid[i]
        if (0,0,0) not in row:
            qgates = colours_to_qgates(row)
            check_combinations_length = execute_qc(qgates) #find combinations from maximum to minimum
            
            inc += 1
            index = i
            for j in range(len(row)):
                try:
                    del locked[(j,i)]
                except:
                    continue

    if inc > 0:
        for key in sorted(list(locked), key=lambda x: x[1])[::-1]:
            x, y = key
            if y < ind:
                newKey = (x, y + inc)
                locked[newKey] = locked.pop(key)

    return inc


def draw_next_shape(shape, surface):
    font = pygame.font.SysFont('comicsans', 30)
    label = font.render('Next Shape', 1, (255,255,255))

    sx = config.top_left_x + config.play_width + 50
    sy = config.top_left_y + config.play_height/2 - 100
    format = shape.shape[shape.rotation % len(shape.shape)]
    
    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                index = shape.BlockSet.operators[j].index
                surface.blit(config.qops[index], pygame.Rect(sx + j*config.block_size, sy + i*config.block_size, config.block_size, config.block_size))
    
    surface.blit(label, (sx + 10, sy - 30))    
    

def update_score(nscore):
    score = max_score()

    with open('scores.txt', 'w') as f:
        if int(score) > nscore:
            f.write(str(score))
        else:
            f.write(str(nscore))


def max_score():
    with open('scores.txt', 'r') as f:
        lines = f.readlines()
        score = lines[0].strip()

    return score


def draw_window(surface, grid, score=0, last_score = 0):
    surface.fill((0, 0, 0))

    pygame.font.init()
    font = pygame.font.SysFont('comicsans', 60)
    label = font.render('Tetris', 1, (255, 255, 255))

    surface.blit(label, (config.top_left_x + config.play_width / 2 - (label.get_width() / 2), 30))

    # current score
    font = pygame.font.SysFont('comicsans', 30)
    label = font.render('Score: ' + str(score), 1, (255,255,255))

    sx = config.top_left_x + config.play_width + 50
    sy = config.top_left_y + config.play_height/2 - 100

    surface.blit(label, (sx + 20, sy + 160))
    # last score
    label = font.render('High Score: ' + last_score, 1, (255,255,255))

    sx = config.top_left_x - 250
    sy = config.top_left_y + 200

    surface.blit(label, (sx + 20, sy + 160))

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            pygame.draw.rect(surface, grid[i][j], (config.top_left_x + j*config.block_size, config.top_left_y + i*config.block_size, config.block_size, config.block_size), 0)

    pygame.draw.rect(surface, (255, 0, 0), (config.top_left_x, config.top_left_y, config.play_width, config.play_height), 5)

    draw_grid(surface, grid)
    #pygame.display.update()


def main(win):  # *
    last_score = max_score()
    locked_positions = {}
    grid = create_grid(locked_positions)

    change_piece = False
    run = True
    current_piece = get_shape()
    next_piece = get_shape()
    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 0.27
    level_time = 0
    score = 0

    while run:
        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        level_time += clock.get_rawtime()
        clock.tick()

        if level_time/1000 > 5:
            level_time = 0
            if level_time > 0.12:
                level_time -= 0.005

        if fall_time/1000 > fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not(valid_space(current_piece, grid)) and current_piece.y > 0:
                current_piece.y -= 1
                change_piece = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.display.quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not(valid_space(current_piece, grid)):
                        current_piece.x += 1
                if event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not(valid_space(current_piece, grid)):
                        current_piece.x -= 1
                if event.key == pygame.K_DOWN:
                    current_piece.y += 1
                    if not(valid_space(current_piece, grid)):
                        current_piece.y -= 1
                if event.key == pygame.K_UP:
                    current_piece.rotation += 1
                    if not(valid_space(current_piece, grid)):
                        current_piece.rotation -= 1

        shape_pos = convert_shape_format(current_piece)

        for i in range(len(shape_pos)):
            x, y = shape_pos[i]
            if y > -1:
                grid[y][x] = current_piece.color

        if change_piece:
            for pos in shape_pos:
                p = (pos[0], pos[1])
                locked_positions[p] = current_piece.color
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False
            score += clear_row_combinations(grid, locked_positions) * 10

        draw_window(win, grid, score, last_score)
        draw_next_shape(next_piece, win)
        pygame.display.update()

        if check_lost(locked_positions):
            draw_text_middle(win, "YOU LOST!", 80, (255,255,255))
            pygame.display.update()
            pygame.time.delay(1500)
            run = False
            update_score(score)


def main_menu(win):  # *
    run = True
    while run:
        win.fill((0,0,0))
        draw_text_middle(win, 'Press Any Key To Play', 60, (255,255,255))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                main(win)

    pygame.display.quit()


win = pygame.display.set_mode((config.s_width, config.s_height))
pygame.display.set_caption('Tetris')
main_menu(win)

row = [(255, 165, 0), (0, 255, 0), (255, 255, 0), 
       (255, 255, 0), (128, 0, 128), (128, 0, 128), 
       (128, 0, 128), (0, 255, 0), (0, 255, 0), (128, 0, 128)]

possible_colors = {
    'X': (0, 255, 0),
    'Y': (255, 0, 0),
    'Z': (0, 255, 255),
    'Rx': (255, 255, 0),
    'Ry': (255, 165, 0),
    'Rz': (0, 0, 255),
    'H': (128, 0, 128),
    'I': (128, 128, 0),
}
def colours_to_qgates(colours_list):
    qgates = []
    key_list = list(possible_colors.keys())
    val_list = list(possible_colors.values())
    for i in range(len(colours_list)):
        if (colours_list[i] in val_list):
            position = val_list.index(colours_list[i])
            qgates.append(key_list[position])
    return qgates
t = colours_to_qgates(row)
