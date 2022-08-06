import copy
import numpy as np
from numpy import infty
import pygame, random, math, sys
from pygame.locals import *
from collections import defaultdict, deque

#Monte Carlo Search Tree is abbreviated MCST
clock=pygame.time.Clock()
#eventually try and implement shifting show available feature with stack if suitable
pygame.init()
ROWS=COLUMNS=10
WINDOW_LENGTH=400
BOARD_COLOR="ORANGE"
gap=WINDOW_LENGTH/ROWS
WINDOW_SIZE=(WINDOW_LENGTH,WINDOW_LENGTH)
screen=pygame.display.set_mode(WINDOW_SIZE, 0, 32)
pygame.display.set_caption("Lines of Action Game")


neighbors_white=defaultdict(set)
neighbors_grey=defaultdict(set)
colors=defaultdict(str)
curr=defaultdict(set)
#tuple[0], tuple[1] ~ white, grey
row_count=defaultdict(lambda: 0) 
col_count=defaultdict(lambda: 0)
main_diag=defaultdict(lambda : 0)
sec_diag=defaultdict(lambda : 0)

available=[]
cell_clicked=(0,0)
clicked=False
visited=None
color="WHITE"
AI=False
AI_1, AI_2 = None, None #possible AIs for players 1 and 2

class Board_State: #for the game board simulation
    total_visits=0 #class variable
    max_child=None
    sec_child=None
    white_components=0
    grey_components=0
    def __init__(self, colors, parent, neighbors_white, neighbors_grey, row_c, col_c, main_c, sec_c, level=0):#colors symbolizes board state
        self.colors=colors
        self.val=0
        self.visited=0
        self.parent=parent
        self.white=neighbors_white
        self.grey=neighbors_grey
        #tuple[0], tuple[1] ~ white, grey
        self.row_count=row_c 
        self.col_count=col_c
        self.main_diag=main_c
        self.sec_diag=sec_c
        self.UGI=float(infty)
        self.level=level
    
    def set_UGI(self):
        if(self.visited !=0):
            self.UGI=self.val/self.visited+2*math.sqrt(np.log(Board_State.total_visits)/self.visited)

    def add_level(self):
        self.level+=1
    
    def clear_dicts(self):
        self.white.clear()
        self.grey.clear()
        self.colors.clear()
        self.row_count.clear()
        self.col_count.clear()
        self.main_diag.clear()
        self.sec_diag.clear()

    def __lt__(self, other):
        return False

states=defaultdict(list)
moves=defaultdict(list)

def pretty_print():
    for row in range(1, ROWS+1):
        line=""
        for col in range(1, COLUMNS+1):
            if (row, col) in neighbors_white.keys():
                line+=("W  ")
            elif (row, col) in neighbors_grey.keys():
                line+=("G  ")
            else:
                line+=("O  ")
        print(line)
    print("")


def remove_grid(a, b): #a is row and b is column
        row_count[a]=row_count[a]-1
        col_count[b]=col_count[b]-1
        main_diag[a-b]=main_diag[a-b]-1
        sec_diag[a+b]=sec_diag[a+b]-1

def add_grid(a, b):
    row_count[a]=row_count[a]+1
    col_count[b]=col_count[b]+1
    main_diag[a-b]=main_diag[a-b]+1
    sec_diag[a+b]=sec_diag[a+b]+1

def fill(row, col, color, AI=False): #for AI does nothing
    if color != "RED":
        colors[(row, col)]=color
    if color=="WHITE" or color=="GREY":
        add_grid(row, col)
    if(AI):
        return
    rect=Rect((col-1)*gap, (row-1)*gap, gap, gap)
    screen.fill(Color(color), rect)
    pygame.display.flip()
    pygame.draw.line(screen, "BLACK", ((col-1)*gap, (row-1)*gap), ((col)*gap, (row-1)*gap))
    pygame.draw.line(screen, "BLACK", ((col-1)*gap, (row-1)*gap), ((col-1)*gap, (row)*gap))

def cell_values(cell_tuple): #returns row and column position of each cell
    return cell_tuple[0], cell_tuple[1]

def show_available(row, col, color, AI=False): #show available squares in red after player clicks team's square

    #checks valid spaces in row

    if(col>row_count[row]):
        for c in range(col-1, col-row_count[row]-1, -1):
            if (colors[(row, c)] == color):
                break
            if c==col-row_count[row]:
                fill(row, c, "RED", AI)
                available.append((row,c))
    if(col<=ROWS-row_count[row]):
        for c in range(col+1, col+row_count[row]+1):
            if(colors[(row, c)] == color):
                break
            if c==col+row_count[row]:
                fill(row, c, "RED", AI)
                available.append((row, c))
    
    # checks valid spaces in column

    if(row>col_count[col]):
        for r in range(row-1, row-col_count[col]-1, -1):
            if (colors[(r, col)] == color):
                break
            if r==row-col_count[col]:
                fill(r, col, "RED", AI)
                available.append((r,col))
    if(row<=COLUMNS-col_count[col]):
        for r in range(row+1, row+col_count[col]+1):
            if(colors[(r, col)] == color):
                break
            if r==row+col_count[col]:
                fill(r, col, "RED", AI)
                available.append((r, col))
    
    #checks valid spaces in main diagnol 

    if (col>main_diag[row-col]): #left
        if(row>main_diag[row-col]): #up
            for r in range(row-1, row-main_diag[row-col]-1, -1): 
                if(colors[(r, col-row+r)]==color):
                    break
                if r==row-main_diag[row-col]:
                    fill(r, col-row+r, "RED", AI)
                    available.append((r, col-row+r))
    if (col<=COLUMNS-main_diag[row-col]): #right
        if(row<=ROWS-main_diag[row-col]): #down
            for r in range(row+1, row+main_diag[row-col]+1):
                if(colors[(r, col-row+r)]==color):
                    break
                if r==row+main_diag[row-col]:
                    fill(r, col-row+r, "RED", AI)
                    available.append((r, col-row+r))

    #checks valid spaces in secondary diagnol

    if (col>sec_diag[row+col]): #left     
        if(row<=ROWS-sec_diag[row+col]): #down
            for r in range(row+1, row+sec_diag[row+col]+1):
                if(colors[(r, row+col-r)] == color):
                    break
                if(r == row+sec_diag[row+col]):
                    fill(r, row+col-r, "RED", AI)
                    available.append((r, row+col-r))
    if (col<=COLUMNS-sec_diag[row+col]): #right
        if(row>sec_diag[row+col]): #up
            for r in range(row-1, row-sec_diag[row+col]-1, -1):
                if(colors[(r, row+col-r)] == color):
                    break
                if(r == row-sec_diag[row+col]):
                    fill(r, row+col-r, "RED", AI)
                    available.append((r, row+col-r))

def BFS(color, vertex, avoid=None): #used for component_number
    marked=set()
    marked.add(vertex)
    queue=deque()
    queue.append(vertex)
    if color=="WHITE":
        curr=neighbors_white
    elif color=="GREY":
        curr=neighbors_grey 
    while queue:
        current=queue.popleft()
        for neighbor in curr[current]:
            if avoid is not None:
                if avoid==neighbor:
                    continue
            if neighbor not in marked:
                queue.append(neighbor)
                marked.add(neighbor)
    return marked

def component_number(color, cells, avoid=None): #finds the number of connected components of color parameter 'color' in our grid
    cell_set=set()
    cells_op=set(cells)
    res=0
    while cells_op:
        vertex=cells_op.pop()
        if vertex in cell_set:
            continue
        traversal=BFS(color, vertex, avoid)
        cell_set.update(traversal)
        res+=1
    return res

def BFS_find(vertex, neighbors_find): #For bot: prevents overcounting number of connected components of current color cells
    marked=set()
    marked.add(vertex)
    queue=deque()
    queue.append(vertex)
    if color=="WHITE":
        curr=neighbors_white
    elif color=="GREY":
        curr=neighbors_grey 
    while queue:
        current=queue.popleft()
        for neighbor in curr[current]:
            if neighbor in marked:
                continue
            if neighbor in neighbors_find:
                return True
            marked.add(neighbor)
            queue.append(neighbor)
    return False
 
def simulate(color: str): #Simulates a move (Board_State) for the MCST
    global available
    if color=="WHITE":
        curr=neighbors_white
    elif color=="GREY":
        curr=neighbors_grey
    #case: curr is empty
    cell_clicked=random.choice(list(curr))
    show_available(cell_clicked[0], cell_clicked[1], color, True)
    if not available:
        return 0, 0, False
    next=random.choice(available)
    val_color, val_other = update(cell_clicked[0], cell_clicked[1], next[0], next[1], color, True)
    cell_clicked=(0,0)
    available=[]
    return val_color, val_other, True

def Rollout(color: str, board_state: Board_State): #here there will be repeated simulations
    initial=color
    if color=="WHITE":
        val_color=board_state.white_components
        val_other=board_state.grey_components
    elif color=="GREY":
        val_color=board_state.grey_components
        val_other=board_state.white_components
    for i in range(10):
        add_color, add_other, next = simulate(color)
        if not next:
            break
        val_color=val_color+add_color if color==initial else val_color+add_other
        val_other=val_other+add_other if color==initial else val_other+add_color
        color = "WHITE" if color == "GREY" else "GREY"
    board_state.val=val_color-val_other
    board_state.visited+=1
    Board_State.total_visits+=1
    board_state.set_UGI()

def find_maxes(boards: list, max:Board_State, sec:Board_State): #finds child node of current node with highest UGI (valuation) value

    for board in boards:
        board.set_UGI() 
        if max is not None and sec is not None:
            if max.UGI==sec.UGI==float(infty):
                break
            if board.UGI>max.UGI:
                sec=max
                max=board
                continue
            elif(board.UGI>sec.UGI):
                sec=board
                continue
        if max is not None and sec is None:
            if board.UGI>max.UGI:
                sec=max
                max=board
                continue
            else:
                sec=board
        if max is None and sec is not None:
            if board.UGI>sec.UGI:
                max=board
            else:
                max=sec
                sec=board
                continue
        if max is None and sec is None:
            max=board
            continue
    
    return max, sec

def find_max_visited(children: list): #finds the child board game state of the initial state with the greatest number of visits in the MCST.
    max=children[0]
    for child in children:
        if(child.visited>max.visited):
            max=child
    return max

def update_parents(current: Board_State): #deletes dicionaries associated with "internal nodes" of MCST, thereby saving memory. Updates the visited values
                                            #of each node passed by MCST, and total visits, by 1.
    val=current.val
    while current.parent is not None:
        current=current.parent
        current.val = current.val+val
        current.visited+=1
        current.set_UGI()
        if current.level==0:
            return
        current.clear_dicts()

def backtrack(current: Board_State): #resets global variables 
    global colors, neighbors_white, neighbors_grey, colors, row_count, col_count, main_diag, sec_diag

    neighbors_white=copy.deepcopy(current.white)
    neighbors_grey=copy.deepcopy(current.grey)
    colors=current.colors.copy()
    row_count=current.row_count.copy()
    col_count=current.col_count.copy()
    main_diag=current.main_diag.copy()
    sec_diag=current.sec_diag.copy()

def Expansion(color: str, current: Board_State): #Initializes children of current Board_State node
    global curr, colors, row_count, col_count, main_diag, sec_diag, neighbors_white, neighbors_grey, available

    if color=="WHITE":
        curr=copy.deepcopy(current.white)
    elif color=="GREY":
        curr=copy.deepcopy(current.grey)
    
    for move in curr.keys(): 
        show_available(move[0], move[1], color, True) 
        while available:
            choice=available.pop()
            val_color, val_other = update(move[0], move[1], choice[0], choice[1], color, True) #changes curr, colors
            next=Board_State(copy.copy(colors), current, copy.deepcopy(neighbors_white), copy.deepcopy(neighbors_grey), copy.copy(row_count), copy.copy(col_count), copy.copy(main_diag), copy.copy(sec_diag), current.level+1)
            if color=="WHITE":
                next.white_components=current.white_components+val_color
                next.grey_components=current.grey_components+val_other
            elif color=="GREY":
                if color=="WHITE":
                    next.white_components=current.white_components+val_other
                    next.grey_components=current.grey_components+val_color
            moves[next]=[(move[0], move[1]), (choice[0], choice[1])]
            states[current].append(next)
            backtrack(current)

def AI_move(color, initial: Board_State): #bot functionality
    global colors, neighbors_white, neighbors_grey, row_count, col_count, main_diag, sec_diag
    initial_color=color
    current=initial

    while Board_State.total_visits<=5: #when actually run, make this (ROWS-2)*1.5
        if color=="WHITE":
            other_color="GREY"
        elif color=="GREY":
            other_color="WHITE"
        if(not states[current]):
            if(current.visited != 0 or current.level==0):
                Expansion(color, current) 
                current.max_child, current.sec_child = find_maxes(states[current], current.max_child, current.sec_child)
                current, color = current.max_child, other_color
                continue
            else:
                Rollout(color, current)
                update_parents(current)
                backtrack(initial) 
                current, color = initial, initial_color 
        if(states[current]):
            #max_child, sec_child ~infty*2
            current.max_child, current.sec_child = find_maxes(states[current], current.max_child, current.sec_child)
            if current.max_child is not None:
                current=current.max_child
                update(moves[current][0][0], moves[current][0][1], moves[current][1][0], moves[current][1][1], color, True)
                color=other_color
    
    neighbors_white=copy.deepcopy(initial.white) 
    neighbors_grey=copy.deepcopy(initial.grey)
    row_count=copy.copy(initial.row_count)
    col_count=copy.copy(initial.col_count) 
    main_diag=copy.copy(initial.main_diag)
    sec_diag=copy.copy(initial.sec_diag)
    colors=initial.colors.copy() 
    return find_max_visited(states[initial])

    
def remove_available_spaces(AI): #resets list of available spaces to [] after player/bot moves
    global available
    if(AI):
        available=[]
    while available:
        cell=available.pop()
        row, col = cell[0], cell[1]
        rect = Rect((col-1)*gap, (row-1)*gap, gap, gap)
        screen.fill(Color(colors[cell]), rect)
        pygame.draw.line(screen, "BLACK", ((col-1)*gap, (row-1)*gap), (col*gap, (row-1)*gap))
        pygame.draw.line(screen, "BLACK", ((col-1)*gap, (row-1)*gap), ((col-1)*gap, row*gap))

def del_neighbors(color, a, b): #deletes cell at location, and deletes it from neighbors list
    if(color=="WHITE"):
        curr=neighbors_white
    elif(color=="GREY"):
        curr=neighbors_grey 
    
    for element in curr[(a,b)]:
        curr[element].remove((a,b))
    curr.pop((a,b))
    remove_grid(a, b)

def update(a, b, c, d, color, AI=False): #updates the grid after a move
    val_color, val_other = 0,0
    if(color=="WHITE"):
        curr=neighbors_white
        other, other_color=neighbors_grey, "GREY"
    elif(color=="GREY"):
        curr=neighbors_grey
        other, other_color=neighbors_white, "WHITE"
    initial_color_neighbors=curr[(a,b)] 
    final_color_neighbors=set()
    for elements in curr.keys():
        row, col=cell_values(elements)
        if(row==c and col==d):
            continue
        if(abs(row-c)<=1 and abs(col-d)<=1):
            final_color_neighbors.add(elements)
    if (a,b) in final_color_neighbors:
        final_color_neighbors.remove((a,b))
    if AI:
        if BFS_find((a,b), final_color_neighbors):
            val_color-=(component_number(color, final_color_neighbors)-1)
        else:
            val_color-=(component_number(color, final_color_neighbors))
    fill(a,b,BOARD_COLOR, AI)
    del_neighbors(color, a, b) 
    fill(c,d, color, AI)
    if (c,d) in other.keys():
        if AI:
            val_other+=(component_number(other_color, other[(c,d)], (c,d))-1)
        del_neighbors(other_color, c, d)
    curr[(c,d)]=set()
    #problem
    for element in final_color_neighbors:
        curr[(c,d)].add(element)
        curr[element].add((c,d))
    if AI:
        if BFS_find((c,d), initial_color_neighbors):
            val_color+=(component_number(color, initial_color_neighbors)-1)
        else:
            val_color+=(component_number(color, initial_color_neighbors))
    return val_color, val_other
#initialize
for row in range(2, ROWS):
    for col in range(2, COLUMNS):
        fill(row, col, "ORANGE")
fill(1, 1, "ORANGE")
fill(1, COLUMNS, "ORANGE")
fill(ROWS, 1, "ORANGE")
fill(ROWS, COLUMNS, "ORANGE")
for i in range(COLUMNS-2):
    fill(1, i+2, "WHITE")
    fill(ROWS, i+2, "WHITE")
for i in range(ROWS-2):
    fill(i+2, 1, "GREY")
    fill(i+2,COLUMNS, "GREY")

for r in range(2, ROWS):
    if (r>2):
        neighbors_grey[(r,1)].add((r-1,1))
        neighbors_grey[(r,COLUMNS)].add((r-1,COLUMNS))
    if(r<ROWS-1):
        neighbors_grey[(r,1)].add((r+1,1))
        neighbors_grey[(r,COLUMNS)].add((r+1,COLUMNS))
for c in range(2, COLUMNS):
    if (c>2):
        neighbors_white[(1,c)].add((1,c-1))
        neighbors_white[(ROWS,c)].add((ROWS,c-1))
    if(c<COLUMNS-1):
        neighbors_white[(1,c)].add((1,c+1))
        neighbors_white[(ROWS,c)].add((ROWS,c+1))

while True:
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            pygame.quit()
            sys.exit()
        if (color=="WHITE"):
            other_color="GREY"
            if neighbors_grey.keys():
                if component_number("GREY", neighbors_grey.keys())==1:
                    print("Grey Wins!")
                    pygame.quit()
                    sys.exit()
            else:
                print("Grey Wins!")
                pygame.quit()
                sys.exit()
        elif (color=="GREY"):
            other_color="WHITE"
            if neighbors_white.keys():
                if component_number("WHITE", neighbors_white.keys())==1:
                    print("White Wins!")
                    pygame.quit()
                    sys.exit()
            else:
                print("White Wins!")
                pygame.quit()
                sys.exit()
            if event.type==QUIT:
                pygame.quit()
                sys.exit()
        
        if event.type==pygame.KEYDOWN:
            if event.key==pygame.K_SPACE:    
                if AI_1 is None:
                    AI_1=color
                elif AI_2 is None:
                    if AI_1 != color:
                        AI_2=color
        
        if color==AI_1 or color==AI_2:
            board=Board_State(copy.copy(colors), None, copy.deepcopy(neighbors_white), copy.deepcopy(neighbors_grey), copy.copy(row_count), copy.copy(col_count), copy.copy(main_diag), copy.copy(sec_diag))
            board.white_components=component_number("WHITE", board.white.keys())
            board.grey_components=component_number("GREY", board.grey.keys())
            max_child=AI_move(color, board)  #increases row_count
            pygame.time.wait(1000)
            update(moves[max_child][0][0], moves[max_child][0][1], moves[max_child][1][0], moves[max_child][1][1], color)
            #update increases row_count
            states=defaultdict(list)
            moves=defaultdict(list)
            Board_State.total_visits=0
            color=other_color

        if color != AI_1 and color != AI_2:    
            if event.type==pygame.MOUSEBUTTONDOWN:
                if pygame.mouse.get_pressed()[0]: 
                    x , y = pygame.mouse.get_pos()
                    row, col = y//gap+1, x//gap+1
                    row, col = int(row), int(col)
                    if (not clicked):
                        cell_clicked=(row, col)
                        if(colors[cell_clicked]==color):
                            #pretty_print_colors(colors, 1)
                            visited=(row, col)
                            show_available(row, col, color)
                            clicked=True
                    elif (clicked):
                        if (row,col) in available:
                            update(visited[0], visited[1], row, col, color)
                            remove_available_spaces(AI)
                            visited = None
                            cell_clicked=(0,0)
                            clicked=False
                            color=other_color
                if pygame.mouse.get_pressed()[2]:
                    if (clicked):
                        x, y = pygame.mouse.get_pos()
                        row, col = y//gap+1, x//gap+1
                        row, col = int(row), int(col)
                        if cell_clicked==(row,col):
                            remove_available_spaces(AI)
                            visited = None
                            cell_clicked=(0,0)
                            clicked=False

    pygame.display.update()
