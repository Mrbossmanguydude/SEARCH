import random, pygame

pygame.init()

# Constant Definitions
WIDTH, HEIGHT = 700, 700
FPS = 60

WALL = "0"
PATH = "1"
INITIAL = "A"
END = "B"

FONT = "fonts\\pixel_font-1.ttf"

class Button:
    def __init__(self, x, y, width, height, text, text_size, bordercolor=(0, 0, 0), textcolor=(0, 0, 0), thickness=5):
        self.rect = pygame.Rect(x, y, width, height)
        self.rect.topleft = (x, y)
        self.text = text
        self.text_size = text_size
        self.textcolor = textcolor
        self.bordercolor = bordercolor
        self.thickness = thickness
        self.clicked_ticks = 0
        self.clicked = False

    def get_clicked(self):
        #Check for a left mouse button click.
        if self.clicked_ticks >= FPS:
            mouse_pos = pygame.mouse.get_pos()
            if self.rect.collidepoint(mouse_pos):
                if pygame.mouse.get_pressed()[0]: #Index 0 specifies left mouse button.
                    self.clicked = True #Button is clicked if a collision with mouse and Rect is detected.
        else:
            self.clicked = False #Otherwise, the button is not clicked.

    def draw(self):
        #Draws out the button and its border.
        draw_highlighted_rect(screen, self.rect, self.bordercolor, self.bordercolor, self.thickness, self.thickness)
        draw_text(screen, FONT, self.text, (self.rect.x + 15, self.rect.y), self.text_size, self.textcolor)

class Node:
    def __init__(self, pos, parent_node):
        #Object signifies an individual node, storing its info and more importantly, its parent node and also its type.
        self.parent_node = parent_node
        self.pos = pos
        self.type = ""

class Agent:
    def __init__(self, inital_pos, goal_pos):
        self.initial_pos = inital_pos
        self.goal_pos = goal_pos
        self.frontier = [inital_pos] # coordinates in the maze
        self.path = [] #Backtracking to see which nodes were chosen last, by looking at parent nodes.
        self.explored = [] # coordinates in the maze

    def check_explored(self, nx, ny):
        for node in self.explored:
            if node.pos == (nx, ny):
                return True
            
        return False

    def expand(self, maze, node):
        '''
        Meant to return all the nodes 'seen' by the node in the parameter.
        So, looking up, down, left and right for each node added to the frontier, to see where we may expand towards next.
        '''
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        neighbors = []
        for dx, dy in directions:
            nx, ny = node[0] + dx, node[1] + dy
            # Check if the neighbor is within bounds and is a path
            if 0 <= nx < len(maze) and 0 <= ny < len(maze[0]) and maze[nx][ny] in (PATH, INITIAL, END):
                if (nx, ny) not in self.frontier and not self.check_explored(nx, ny):
                    neighbors.append((nx, ny))
        return neighbors
    
    def BFS(self, maze):
        prev = None
        while self.frontier:
            fnode = self.frontier.pop(0)

            x, y = fnode[0], fnode[1]
            if maze[x][y] == END:
                self.explored.append(Node((x, y), prev))
                return self.explored
            
            else:
                if prev == None:
                    self.explored.append(Node((x, y), None))
                else:
                    self.explored.append(Node((x, y), prev))

                neighbours = self.expand(maze, (x, y))

                for neighbour in neighbours:
                    self.frontier.append(neighbour)
            prev = (x, y)

        return self.explored
    
def draw_highlighted_rect(surface : pygame.surface.Surface, rect : pygame.rect.Rect, border_color : tuple, highlight_color : tuple, border_thickness : int, highlight_thickness : int):
    pygame.draw.rect(surface, border_color, rect, border_thickness)
    inner_rect = pygame.Rect(rect.left + border_thickness, rect.top + border_thickness,rect.width - 2 * border_thickness, rect.height - 2 * border_thickness)
    pygame.draw.rect(surface, highlight_color, inner_rect, highlight_thickness)

def draw_text(surface : pygame.surface.Surface, font : pygame.font.Font, text : str, pos : tuple, fontsize : int, color : tuple):
    font = pygame.font.Font(font, fontsize) # Font is reassigned as a pygame.Font obj to be blit.
    word = font.render(text, True, color)
    surface.blit(word, (pos[0], pos[1])) #word blit at right position in given font.

def reset_buttons(buttons : list):
    for button in buttons:
        button.clicked_ticks = 0
        button.clicked = False

def increment_button_ticks(buttons : list):
    for button in buttons:
        if button.clicked_ticks < FPS: #Uses FPS to ensure only close to a second is there for button delay.
            button.clicked_ticks += 1

def draw_map(width, height, s_width, s_height):
    for i in range(width):
        pygame.draw.line(screen, (255, 255, 255), (i*s_width, 0), (i*s_width, HEIGHT), 3)
    for j in range(height):
        pygame.draw.line(screen, (255, 255, 255), (0, j*s_height), (WIDTH, j*s_height), 3)

def backtrack_path(explored):
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    
    path = []
    current_node = explored[-1]
    path.append(current_node.pos)

    for i in range(len(explored) - 2, -1, -1):
        node = explored[i]
        cx, cy = current_node.pos
        nx, ny = node.pos
        if any((cx + dx == nx and cy + dy == ny) for dx, dy in directions):
            path.append(node.pos)
            current_node = node

            if current_node.parent_node is None:
                break
    path.reverse()
    return path

def color_map(frontier, explored, Map, s_width, s_height):
    for i in range(len(Map)):
        for j in range(len(Map[i])):
            x, y = i * s_width, j * s_height

            if (i, j) in frontier:
                color = (0, 0, 100)
            elif Map[i][j] == WALL:
                color = (0, 0, 0)  # Red for walls
            elif Map[i][j] == PATH:
                color = (0, 0, 255) if check_explored(explored, i, j) else (100, 100, 100)  # Green for paths
            elif Map[i][j] == INITIAL:
                color = (0, 0, 255)  # Blue for initial position
            elif Map[i][j] == END:
                color = (255, 0, 0) if check_explored(explored, i, j) else (100, 100, 100)   # Black for end
            rect = pygame.Rect(x, y, s_width, s_height)
            pygame.draw.rect(screen, color, rect)

def create_maze(width, height, Map):
    # Randomly choose a starting point
    start_x = random.randint(1, width - 2)
    start_y = random.randint(1, height - 2)

    # Initialize the frontier and visited set
    frontier = [(start_x, start_y)]
    visited = set()
    visited.add((start_x, start_y))

    # Directions for moving in the grid (up, down, left, right)
    directions = [(-2, 0), (2, 0), (0, -2), (0, 2)]

    # Minimum number of cells to be explored
    min_visited = (width * height) // 2

    while frontier:
        if len(visited) >= min_visited and not frontier:
            break

        x, y = random.choice(frontier)
        frontier.remove((x, y))

        # Try moving in all directions
        random.shuffle(directions)
        for dx, dy in directions:
            nx, ny = x + dx, y + dy

            # Check if the neighbor is within bounds and is a wall
            if 0 < nx < width - 1 and 0 < ny < height - 1 and (nx, ny) not in visited:
                # Remove wall between current cell and neighbor
                wx, wy = x + dx // 2, y + dy // 2
                # Ensure wx and wy are within bounds before modifying the grid
                if 0 <= wx < width and 0 <= wy < height:
                    Map[wy][wx] = PATH
                Map[ny][nx] = PATH
                frontier.append((nx, ny))
                visited.add((nx, ny))

    visited = list(visited)
    Map[visited[-1][0]][visited[-1][1]] = END
    # Ensure starting point is an open space
    Map[start_y][start_x] = INITIAL

    return Map, (start_y, start_x), (visited[-1][0], visited[-1][1])

def map_maze_to_pygame(maze):
    return [[WALL if cell == '#' else PATH for cell in row] for row in maze]

def check_explored(explored, x, y):
    for i in explored:
        ex, ey = i[0], i[1]
        
        if (ex, ey) == (x, y):
            return True
    return False

def check_neighbours(node, map, explored):
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    neighbors = []

    for dx, dy in directions:
        nx, ny = node[0] + dx, node[1] + dy
        if (nx, ny) not in explored:
            if map[nx][ny] in (PATH, END):
                neighbors.append((nx, ny))

    return neighbors

def highlight_path(path, size):
    for node in path:
        draw_highlighted_rect(screen, pygame.Rect(size * node[0], size * node[1], size, size), (255, 100, 255), (255, 100, 255), 4, 1)

def main(screen):
    clock = pygame.time.Clock()
    running = True

    width, height = 25, 25
    s_width, s_height = WIDTH // width, HEIGHT // height
    Maze = [[WALL for _ in range(width)] for _ in range(height)]

    Map, initial_pos, goal_pos = create_maze(width, height, Maze)
    print(goal_pos)
    player_explored = [initial_pos]
    player_frontier = [neighbour for neighbour in check_neighbours(initial_pos, Map, player_explored)]

    agent = Agent(initial_pos, goal_pos)
    agent_explored = agent.BFS(Map)
    path = backtrack_path(agent_explored)

    player_score = 0
    agent_score = len(agent_explored)
    
    play_button = Button((WIDTH//2) - 125, 100, 250, 100, "Play", 110)
    buttons = [play_button] #add settings later

    state = "Menu"

    while running:
        clock.tick(FPS)  # Framerate is managed.
        pygame.display.set_caption(f"Search - {str(int(clock.get_fps()))}")  # Updates caption based on framerate.
        screen.fill((50, 50, 50))  # Background of the screen.
        increment_button_ticks(buttons)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if state == "Game":
                    if event.key == pygame.K_ESCAPE:
                        state = "Menu"

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and state == 'Game':
                    mouse_pos = pygame.mouse.get_pos()
                    coord = (mouse_pos[0]//s_width, mouse_pos[1]//s_height)
                    
                    if not check_explored(player_explored, coord[0], coord[1]):
                        if coord in player_frontier:
                            new = player_frontier.pop(player_frontier.index(coord))
                            player_explored.append(new)

                            if Map[new[0]][new[1]] == END:
                                player_score = len(player_explored)

                            neighbours = check_neighbours(new, Map, player_explored)
                            for n in neighbours:
                                player_frontier.append(n)

        play_button.get_clicked()
        if play_button.clicked:
            state = "Game"
            reset_buttons(buttons)
            
        if state == "Game":
            color_map(player_frontier, player_explored, Map, s_width, s_height)
            draw_map(width, height, s_width, s_height)
            if player_score != 0:
                highlight_path(path, s_height)
                draw_text(screen, FONT, "Player Score : " + str(width**2 - player_score), ((WIDTH//2) - 320, 50), 75, (255, 100, 255))
                draw_text(screen, FONT, "Computer Score : " + str(width**2 - agent_score), ((WIDTH//2) - 320, 150), 75, (255, 100, 255))

                if (width**2 - agent_score) > (width**2 - player_score):
                    draw_text(screen, FONT, "Computer Wins!", ((WIDTH//2) - 320, 300), 100, (255, 165, 0))

                elif (width**2 - agent_score) < (width**2 - player_score):
                    draw_text(screen, FONT, "Player Wins!", ((WIDTH//2) - 320, 300), 100, (255, 165, 0))

                else:
                    draw_text(screen, FONT, "Draw!", ((WIDTH//2) - 320, 300), 100, (255, 165, 0))

                pygame.display.flip()
                pygame.time.delay(5000)
                running = False
        
        elif state == "Menu":
            draw_text(screen, FONT, "Search", ((WIDTH//2) - 120, 0), 75, (100, 100, 100))
            pygame.draw.line(screen, (0, 0, 0), (0, 75), (WIDTH, 75), 9)
            play_button.draw()
            
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    main(screen)