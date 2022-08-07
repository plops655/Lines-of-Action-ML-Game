# Lines-of-Action-ML-Game
The project allows for player v. player, player v. bot, and bot v. bot games, the latter two via machine learning, and more specifically, the Monte Carlo Search Tree Algorithm.

# Motivation
The project attempts to imitate the basic functionality of machine learning algorithms common in board games like chess and Go. The Monte Carlo Search Tree (MCST) algorithm is a probabilistic,
heuristic based algorithm which uses a valuation function to decide the optimal strategy.

# Rules of the Game
The game begins with an **n** by **n** grid with white cells in filling rows 1 and n and black cells filling columns 1 and n with the exception of the corners of the grid.




![image](https://user-images.githubusercontent.com/107969255/183268718-7e91d127-e379-4cd6-902a-192765c0df17.png)


An example of an initial configuration on an 8 by 8 grid.


The white player moves first. A player may move any token of their given color vertically, horizontally, or diagonally. However, they may only move a square a number of positions
equal to the number of tokens on the line along which it moves. For example, suppose the grey player intends to move diagonally along its main diagnol (left/up to right/down). 
Then the token may only move **x** positions along the main diagnol where **x** is the number of tokens, grey and white, along the main diagnol. A token may not jump over a token
of the same color, and may not exit the board. However, a token may jump, or even replace a token of the opposite color. 

Two tokens of the same color are neighbors if they share a vertex, and are connected if there exists a path of neighbors which starts with one of the tokens, and ends with the other.
Then, the goal of the game is to form a connected component of tokens; i.e., to have any two token's of the players color connected first. 

# Game functionality

Assume the player is white WLOG.
- Left-clicking a white cell when no other white cell has been clicked highlights the available positions the white cell can move to in red.
- Right-clicking a left-clicked white cell undoes the above operation.
- Clicking an available position of a left-clicked white cell moves the white cell to that position and sets the current player to grey.

To assign a bot to a color, press space. 

# Monte Carlo Search Tree

The Monte Carlo Search Tree consists of 4 operations: Expansion, Rollout, and Backpropogation. The additional operation, simulation, is part of Rollout. Nodes of the search
tree are board game states, and a node is a child of another if it can be obtained from the latter.

- Expansion: Initializes the children of the current node when the node has not been visited, or the node corresponds to the very first board game state.
- Rollout: Random consecutive board game states are simulated, and the visited and UGI values of each node visited up till the current node are updated (backpropagation).
The valuation of a board game state is the number of components of cells the other state color minus the number of components of cells of the current state color.

