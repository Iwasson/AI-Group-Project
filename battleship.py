import json
import random
from os.path import exists

hitreward = 10
badReward = -2
missreward = -2
wallreward = -2

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

    fireX = 0
    fireY = 0

    iterations = 0
    while shoot == False and iterations < 100:
        fireX = random.randrange(0, 10, 1) # pick a random starting x
        fireY = random.randrange(0, 10, 1) # pick a random starting y

        if guess[fireX][fireY] == ' ': # check if we have already tried to shoot here
            if enemyBoard[fireX][fireY] == ' ': # if there was no ship, record miss
                guess[fireX][fireY] = 'M'
            else:                               # if there was a ship, record the hit
                guess[fireX][fireY] = 'H'
                enemyBoard[fireX][fireY] = 'H'  # update the enemy board to reflect the hit
            shoot = True

        iterations += 1
    return fireX, fireY

# creates the move list with all of the possible perms
# returns a moveList
def initMoveList():
    moveList = [[0] * 5 for x in range(1024)]
    index = 0
    for a in range(4):
        for b in range(4):
            for c in range(4):
                for d in range(4):
                    for e in range(4):
                        action = 0
                        moveList[index][action] = a
                        action += 1
                        moveList[index][action] = b
                        action += 1
                        moveList[index][action] = c
                        action += 1
                        moveList[index][action] = d
                        action += 1
                        moveList[index][action] = e
                        index += 1

    return moveList

# scans the current state of the board from any x or y position
def scan(x, y, guessBoard):
    # scan current tile
    if guessBoard[x][y] == 'M':     # check if we have shot at this space before
        current = 1
    elif guessBoard[x][y] == 'H':   # check if we have missed this space before
        current = 2
    else:
        current = 0

    # scan north
    if x == 0:                      # if we are at x = 0 then north is a wall
        north = 3
    elif guessBoard[x-1][y] == 'M':
        north = 1
    elif guessBoard[x-1][y] == 'H':
        north = 2
    else:
        north = 0

    # scan east
    if y == 9:                      # if we are at y = 9 then east is a wall
        east = 3
    elif guessBoard[x][y+1] == 'M':
        east = 1
    elif guessBoard[x][y+1] == 'H':
        east = 2
    else:
        east = 0
    # scan south
    if x == 9:                      # if we are at x = 9 then south is a wall
        south = 3
    elif guessBoard[x+1][y] == 'M':
        south = 1
    elif guessBoard[x+1][y] == 'H':
        south = 2
    else:
        south = 0
    # scan west
    if y == 0:                      # if we are at y = 0 then west is a wall
        west = 3
    elif guessBoard[x][y-1] == 'M':
        west = 1
    elif guessBoard[x][y-1] == 'H':
        west = 2
    else:
        west = 0

    return current, north, east, south, west

# scans the moves list to get this permutation
def getPermutation(moveList, current, north, east, south, west):
    option = 0

    # scan through the entire range of possible scenarios
    # this is 4^5 because we have 4 possible states, and 5 different
    # locations that we are concerned about
    for x in range(1024):
        if current == moveList[x][0] and north == moveList[x][1] and east == moveList[x][2] and south == moveList[x][3] and west == moveList[x][4]:
            option = x

    return option

# greed first choice of what move to do next
def pickGreedy(qMatrix, perm, epsilon):
    randomChance = random.randrange(0, 100, 1)

    # chance to shoot a random location
    # or pick the worst move
    if randomChance <= epsilon:
        coinFlip = random.randrange(0, 1, 1)

        if coinFlip == 0:
            minimum = qMatrix[perm][0]
            options = []

            for i in range(5):
                if qMatrix[perm][i] == minimum:
                    options.append(i)
                elif minimum > qMatrix[perm][i]:
                    options = []
                    minimum = qMatrix[perm][i]
                    options.append(i)
            
            randChoice = random.randrange(0, len(options), 1)
            return options[randChoice]
        else:
            return 5 # option 5 is to shoot a new random location

    # will generally pick the best option
    else:
        maximum = qMatrix[perm][0]
        options = []

        for i in range(5):
            if qMatrix[perm][i] == maximum:
                options.append(i)
            elif maximum < qMatrix[perm][i]:
                options = []
                maximum = qMatrix[perm][i]
                options.append(i)
        if qMatrix[perm][5] == maximum:
            options.append(5)
        elif maximum < qMatrix[perm][5]:
            options = []
            maximum = qMatrix[perm][i]
            options.append(5)

        randChoice = random.randrange(0, len(options), 1)
        return options[randChoice]

# checks to see if the game is over. This will happen if we have
# no 'X' left on the enemyBoard, in other words, all X are now H
def checkWin(enemyBoard):
    for x in range(10):
        for y in range(10):
            if enemyBoard[x][y] == 'X':
                return False
    return True

# training function. This will train the qMatrix
# can store and load a qMatrix from storage, allowing us to
# preserve the current state of the AI 
def qTraining(episodes, epsilon, epsilonFactor, qMatrix, moveList, reportValue):
    
    # begin training over x episodes
    for e in range(episodes):
        # generate a new battle ship board
        enemyBoard = [[' '] * 10 for x in range(10)]
        placeShips(enemyBoard)
        guessBoard = [[' '] * 10 for x in range(10)]

        x = random.randrange(0, 10, 1)
        y = random.randrange(0, 10, 1)

        option = 0
        
        # will store the states of the adjacent tiles
        # our states are: 
        #   0 == has not been shot at
        #   1 == missed
        #   2 == hit
        #   3 == wall/out of bounds
        current = 0
        north = 0
        east = 0
        south = 0
        west = 0

        # get the current state of where we are going to try our first shot
        current, north, east, south, west = scan(x, y, guessBoard)

        # decrease the epsilon rate every 50 epocs or so
        if e % 50 == 0 and e != 0 and epsilon > 0:
            epsilon -= epsilonFactor
        
        finished = False    # keeps track of when the computer has finished sinking all ships
        iterations = 0      # this will keep track of how long it took for the AI to sink all of the ships
        report = 0          # keeps track of how large of a reward the AI has accumulated

        while finished == False:
            perm = getPermutation(moveList, current, north, east, south, west)
            option = pickGreedy(qMatrix, perm, epsilon)

            reward = 0

            # check which option we are going to take
            if option == 0:     # shoot our current location
                #check if we have already shot at this location before
                if current == 1 or current == 2:
                    reward =  badReward
                    report += badReward

                # check if we hit or miss
                elif enemyBoard[x][y] == ' ':     # give penalty for misses
                    guessBoard[x][y] = 'M'
                    reward =  missreward
                    report += missreward
                elif enemyBoard[x][y] == 'X':   # give reward for hits
                    guessBoard[x][y] = 'H'
                    enemyBoard[x][y] = 'H'
                    reward =  hitreward
                    report += hitreward
                
            if option == 1:     # shoot north
                # check if north is a wall, penalize if so
                if north == 3:
                    reward =  wallreward
                    report += wallreward
                # check if we have shot at this before
                elif north == 1 or north == 2:
                    reward =  badReward
                    report += badReward
                elif enemyBoard[x-1][y] == ' ':
                    guessBoard[x-1][y] = 'M'
                    reward =  missreward
                    report += missreward
                    x -= 1
                elif enemyBoard[x-1][y] == 'X':
                    guessBoard[x-1][y] = 'H'
                    enemyBoard[x-1][y] = 'H'
                    reward =  hitreward
                    report += hitreward
                    x -= 1

            if option == 2:     # shoot east
                if east == 3:
                    reward =  wallreward
                    report += wallreward
                # check if we have shot at this before
                elif east == 1 or east == 2:
                    reward = -5
                    report -= 5
                elif enemyBoard[x][y+1] == ' ':
                    guessBoard[x][y+1] = 'M'
                    reward =  missreward
                    report += missreward
                    y += 1
                elif enemyBoard[x][y+1] == 'X':
                    guessBoard[x][y+1] = 'H'
                    enemyBoard[x][y+1] = 'H'
                    reward =  hitreward
                    report += hitreward
                    y += 1
                
            if option == 3:     # shoot south
                if south == 3:
                    reward =  wallreward
                    report += wallreward
                # check if we have shot at this before
                elif south == 1 or south == 2:
                    reward =  badReward
                    report += badReward
                elif enemyBoard[x+1][y] == ' ':
                    guessBoard[x+1][y] = 'M'
                    reward =  missreward
                    report += missreward
                    x += 1
                elif enemyBoard[x+1][y] == 'X':
                    guessBoard[x+1][y] = 'H'
                    enemyBoard[x+1][y] = 'H'
                    reward =  hitreward
                    report += hitreward
                    x += 1

            if option == 4:     # shoot west
                if west == 3:
                    reward =  wallreward
                    report += wallreward
                # check if we have shot at this before
                elif west == 1 or west == 2:
                    reward =  badReward
                    report += badReward
                elif enemyBoard[x][y-1] == ' ':
                    guessBoard[x][y-1] = 'M'
                    reward =  missreward
                    report += missreward
                    y -= 1
                elif enemyBoard[x][y-1] == 'X':
                    guessBoard[x][y-1] = 'H'
                    enemyBoard[x][y-1] = 'H'
                    reward =  hitreward
                    report += hitreward
                    y -= 1

            if option == 5:     # this means that we are shooting a new random location
                x, y = randomShot(guessBoard, enemyBoard) # this will always be a valid location, no walls possible
                if guessBoard[x][y] == 'M':
                    reward =  missreward
                    report += missreward
                else:
                    reward =  hitreward
                    report += hitreward

            current, north, east, south, west = scan(x, y, guessBoard)
            newPerm = getPermutation(moveList, current, north, east, south, west)

            nextAction = pickGreedy(qMatrix, newPerm, epsilon)
            qMatrix[current][option] += 0.2 * (reward + 0.9 * qMatrix[newPerm][nextAction] - qMatrix[current][option])

            
            iterations += 1
            finished = checkWin(enemyBoard) # this will stop the while loop once we have finished hitting all of the enemy ships

            # FOR DEBUGGING ONLY!
            #printBoard(enemyBoard)
            #printBoard(guessBoard)
            #print("Turn: " + str(iterations + 1) + " Total reward is: " + str(report)) # output what the reward is for the current turn
        
        if e % reportValue == 0 and e != 0:
            print("Episode: " + str(e))
            print("Turns to finish: " + str(iterations + 1) + " Total reward is: " + str(report)) # output what the reward is for the current turn


moveList = initMoveList()

file_exists = exists("qMatrix.json")
if file_exists == True:
    f = open("qMatrix.json") 
    qMatrix = json.load(f)
else:
    qMatrix = [[0] * 6 for x in range(1024)] # this will create a blank qMatrix that is 1024 X 6

qTraining(1000, 20, 0.5, qMatrix, moveList, 100)

jsonQMatrix = json.dumps(qMatrix)
with open('qMatrix.json', 'w') as outfile:
    outfile.write(jsonQMatrix)