import json
import random

# how to define a new board
Player1_Board = [[' '] * 10 for x in range(10)]
Player1_Guess = [[' '] * 10 for x in range(10)]
Player2_Board = [[' '] * 10 for x in range(10)]
Player2_Guess = [[' '] * 10 for x in range(10)]

# debug function to check what the state of a board currently is
def printBoard(board):
    print('      1   2   3   4   5   6   7   8   9   10')
    print('============================================')
    letter = 'A'
    for row in board:
        print('  ' + letter + ' | ', end="")
        for column in row:
            print(column + ' | ', end="")
        print()
        letter = chr(ord(letter) + 1)

# takes in a board, and places all of the classic battleship pieces, 5 in total
# Carrier (5 tiles), Battleship (4 tiles), Cruiser (3 tiles), Submarine (3 tiles), Destroyer (2 tiles)
def placeShips(board):
    # place the carrier
    orientation = random.choice([0,1]) # 0 = horizontal   1 = vertical
    
    startX = random.randrange(0, 10, 1) # pick a random starting x
    startY = random.randrange(0, 10, 1) # pick a random starting y

    # if we are horizontal, check whether or not we have enough room
    # check left then right
    if orientation == 0:
        if startY >= 4:
            for z in range(5):
                board[startX][startY - z] = 'X'
        else:
            for z in range(5):
                board[startX][startY + z] = 'X'
    else:
        if startX >= 4:
            for z in range(5):
                board[startX - z][startY] = 'X'
        else:
            for z in range(5):
                board[startX + z][startY] = 'X'

    # place the battleship
    placed = False
    
    # will need to make sure that we do not overlap the battleship with the carrier
    for ship in [4, 3, 3, 2]:
        while placed == False:
            conflict = False
            orientation = random.choice([0,1]) # 0 = horizontal   1 = vertical
            startX = random.randrange(0, 10, 1) # pick a random starting x
            startY = random.randrange(0, 10, 1) # pick a random starting y

            if orientation == 0:
                if startY >= ship - 1:
                    conflict = False
                    for z in range(ship): # scan the range to see if there is a conflict
                        if board[startX][startY - z] == 'X':
                            conflict = True
                    if conflict == False:
                        for z in range(ship):
                            board[startX][startY - z] = 'X'
                        placed = True
                else:
                    conflict = False
                    for z in range(ship): # scan the range to see if there is a conflict
                        if board[startX][startY + z] == 'X':
                            conflict = True
                    # if there is no conflict, place the piece
                    if conflict == False:
                        for z in range(ship):
                            board[startX][startY + z] = 'X'
                        placed = True
            else:
                if startX >= ship - 1:
                    for z in range(ship): # scan the range to see if there is a conflict
                        if board[startX - z][startY] == 'X':
                            conflict = True
                    if conflict == False:
                        for z in range(ship):
                            board[startX - z][startY] = 'X'
                        placed = True
                else:
                    for z in range(ship): # scan the range to see if there is a conflict
                        if board[startX + z][startY] == 'X':
                            conflict = True
                    if conflict == False:
                        for z in range(ship):
                            board[startX + z][startY] = 'X'
                        placed = True
        placed = False


# will perform a random shot, takes in a "guess board"
def randomShot(guess, enemyBoard):
    shoot = False

    while shoot == False:
        fireX = random.randrange(0, 10, 1) # pick a random starting x
        fireY = random.randrange(0, 10, 1) # pick a random starting y

        if guess[fireX][fireY] == ' ': # check if we have already tried to shoot here
            if enemyBoard[fireX][fireY] == ' ': # if there was no ship, record miss
                guess[fireX][fireY] = 'M'
            else:                               # if there was a ship, record the hit
                guess[fireX][fireY] = 'H'
                enemyBoard[fireX][fireY] = 'H'  # update the enemy board to reflect the hit
            shoot = True




placeShips(Player1_Board)

for x in range(10):
    randomShot(Player2_Guess, Player1_Board)

printBoard(Player2_Guess)
printBoard(Player1_Board)