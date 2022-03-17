import json
import random
from os.path import exists
import threading
from multiprocessing import Process, Queue

# genetic algorithm variables
POPSIZE = 10
MUTATE = 15
MAXITERATIONS = 100
OUTPUT = 5
EPISODES = 100

def randrange_float(start, stop, step):
    return random.randint(0, int((stop - start) / step)) * step + start


def initPopulation(popsize):
    population = []

    for x in range(popsize):
        child = {
            "hitreward" : 0,            # a reward value, lets stick to anything                between 1 and 50
            "badReward" : 0,            # penatly for hitting a spot we have already shot at,   keep between -15 and -1
            "missreward" : 0,           # penatly for missing,                                  keep between -15 and -1
            "wallreward" : 0,           # penatly for attempting to shoot a wall,               keep between -15 and -1
            "epsilon" : 0,              # percent chance to do something random,                keep between 1 and 50%
            "epsilonFactor" : 0,        # how much we want to decrease the epsilon value        keep between 0.1 and 1
            "epsilonDecay" : 0,         # how often we want to decrease the epsilon value       keep between 1 and 100 in multiples of 10
            "eta" : 0.2,                # learning rate               (CANT MODIFY THIS)        keep between 0.1 and 1
            "gamma" : 0.9,              # gamma rate                  (CANT MODIFY THIS)        keep between 0.1 and 1
            "fitness" : 0               # fitness rating                                        do not modify this
        }

        child["hitreward"] = random.randrange(1, 50, 1)
        child["missreward"] = random.randrange(-15, -1, 1)
        child["badReward"] = random.randrange(-15, -1, 1) + child["missreward"]     # need to make sure that shooting somewhere we have already shot it is bad
        child["wallreward"] = random.randrange(-15, -1, 1) + child["missreward"]    # need to make sure that shooting at a wall is worse than missing
        child["epsilon"] = random.randrange(5, 30, 5)
        child["epsilonFactor"] = randrange_float(0.1, 1, 0.01)
        child["epsilonDecay"] = random.randrange(10, 100, 10)
        #child["eta"] = randrange_float(0.1, 1, 0.1)
        #child["gamma"] = randrange_float(0.1, 1, 0.1)

        # child["fitness"] = random.randrange(0, 100)       # for debugging the sort function

        population.append(child)
    
    return population

# sorts a population by its fitness value, higher fitness first
def sortPopulation(population):
    sortPopulation = sorted(population, key=lambda i: (i['fitness']), reverse=True)
    return sortPopulation

# picks a single parent, tending towards the fittest parent first
def parentSelection(population):
    sigmaF = 0

    for i in range(len(population)):
        sigmaF += population[i]["fitness"]
    
    while True:
        for i in range(len(population)):
            tempFit = population[i]["fitness"] / sigmaF
            randFloat = round(random.uniform(0.0,1.0), 2) # get a random 2 decimal number between 0 and 1

            if randFloat < tempFit:
                return population[i]


# mutate child function
def mutate(child):
    changeChance = random.randrange(0, 100)
    if changeChance < MUTATE:
        mutantChild = {
            "hitreward" : 0,            # a reward value, lets stick to anything                between 1 and 100
            "badReward" : 0,            # penatly for hitting a spot we have already shot at,   keep between -100 and -1
            "missreward" : 0,           # penatly for missing,                                  keep between -100 and -1
            "wallreward" : 0,           # penatly for attempting to shoot a wall,               keep between -100 and -1
            "epsilon" : 0,              # percent chance to do something random,                keep between 1 and 100%
            "epsilonFactor" : 0,        # how much we want to decrease the epsilon value        keep between 0 and 1
            "epsilonDecay" : 0,         # how often we want to decrease the epsilon value       keep between 1 and 100
            "eta" : 0,                  # learning rate                                         keep between 0.1 and 1
            "gamma" : 0,                # gamma rate                                            keep between 0.1 and 1
            "fitness" : 0               # fitness rating                                        do not modify this
        }

        mutantChild["hitreward"] = random.randrange(1, 100, 1)
        mutantChild["badReward"] = random.randrange(-100, -1, 1)
        mutantChild["missreward"] = random.randrange(-100, -1, 1)
        mutantChild["wallreward"] = random.randrange(-100, -1, 1)
        mutantChild["epsilon"] = random.randrange(1, 100, 1)
        mutantChild["epsilonFactor"] = randrange_float(0, 1, 0.1)
        mutantChild["epsilonDecay"] = random.randrange(1, 100, 1)
        #mutantChild["eta"] = randrange_float(0.1, 1, 0.1)
        #mutantChild["gamma"] = randrange_float(0.1, 1, 0.1)

        randMutation = random.randrange(0,7)

        mutantChildValues = mutantChild.values()
        mutantChildList = list(mutantChildValues)

        newChildValues = child.values()
        newChildList = list(newChildValues)

        newChildList[randMutation] = mutantChildList[randMutation]

        child = {
            "hitreward" : newChildList[0],            # a reward value, lets stick to anything                between 1 and 100
            "badReward" : newChildList[1],            # penatly for hitting a spot we have already shot at,   keep between -100 and -1
            "missreward" : newChildList[2],           # penatly for missing,                                  keep between -100 and -1
            "wallreward" : newChildList[3],           # penatly for attempting to shoot a wall,               keep between -100 and -1
            "epsilon" : newChildList[4],              # percent chance to do something random,                keep between 1 and 100%
            "epsilonFactor" : newChildList[5],        # how much we want to decrease the epsilon value        keep between 0 and 1
            "epsilonDecay" : newChildList[6],         # how often we want to decrease the epsilon value       keep between 1 and 100
            "eta" : newChildList[7],                  # learning rate                                         keep between 0.1 and 1
            "gamma" : newChildList[8],                # gamma rate                                            keep between 0.1 and 1
            "fitness" : 0                             # fitness rating                                        do not modify this
        }

        return child

    else:
        return child

# pick children
def makeChildren(parentA, parentB):
    newPop = []

    for i in range(2):
        crossover = random.randrange(9)

        # convert the dictionary into lists
        parentAValues = parentA.values()
        parentAList = list(parentAValues)

        parentBValues = parentB.values()
        parentBList = list(parentBValues)

        childValues = []

        for x in range(crossover):
            childValues.append(parentAList[x]) 
        for y in range(crossover, 9):
            childValues.append(parentBList[y])

        child = {
            "hitreward" : childValues[0],            # a reward value, lets stick to anything                between 1 and 100
            "badReward" : childValues[1],            # penatly for hitting a spot we have already shot at,   keep between -100 and -1
            "missreward" : childValues[2],           # penatly for missing,                                  keep between -100 and -1
            "wallreward" : childValues[3],           # penatly for attempting to shoot a wall,               keep between -100 and -1
            "epsilon" : childValues[4],              # percent chance to do something random,                keep between 1 and 100%
            "epsilonFactor" : childValues[5],        # how much we want to decrease the epsilon value        keep between 0 and 1
            "epsilonDecay" : childValues[6],         # how often we want to decrease the epsilon value       keep between 1 and 100
            "eta" : childValues[7],                  # learning rate                                         keep between 0.1 and 1
            "gamma" : childValues[8],                # gamma rate                                            keep between 0.1 and 1
            "fitness" : 0                            # fitness rating                                        do not modify this
        }

        child = mutate(child)
        newPop.append(child)
    
    return newPop
  
def playBattleship(episodes, population):
    newPop = []

    for x in range(len(population)):
        qMatrix = [[0] * 6 for x in range(1024)]
        moveList = initMoveList()
        print("Starting battleship...")
        print(str(population[x]))
        fitness = qTraining(episodes, population[x]["epsilon"], population[x]["epsilonFactor"], qMatrix, moveList, 10, population[x]["epsilonDecay"], population[x]["eta"], population[x]["gamma"], population[x]["hitreward"], population[x]["badReward"], population[x]["missreward"], population[x]["wallreward"])
        print("Session over...")
        population[x]["fitness"] = fitness
        newPop.append(population[x])
        print(fitness)

    return newPop

# multithreaded version
def playBattleshipThreaded(episodes, population):
    newPop = []
    threads = []
    #qTraining(episodes, epsilon, epsilonFactor, qMatrix, moveList, reportValue, epsilonDecay, eta, gamma, hitreward, badReward, missreward, wallreward)
    # start a thread for each child of the original population
    for x in range(len(population)):
        qMatrix = [[0] * 6 for x in range(1024)] # this will create a blank qMatrix that is 1024 X 6
        moveList = initMoveList()
        fits = []
        thread = threading.Thread(target=qTraining, args=(episodes, population[x]["epsilon"], population[x]["epsilonFactor"], qMatrix, moveList, 0, population[x]["epsilonDecay"], population[x]["eta"], population[x]["gamma"], population[x]["hitreward"], population[x]["badReward"], population[x]["missreward"], population[x]["wallreward"], True, fits, x))
        threads.append(thread)

    for x in range(len(threads)):
        print("Starting new thread: " + str(x))
        threads[x].start()
    
    for x in range(len(threads)):
        threads[x].join()
        print("Thread " + str(x) + " Has finished")
    print("All threads have finished.")
    
    fits = sorted(fits, key=lambda i: (i['thread']))

    for x in range(len(fits)):
        population[x]["fitness"] = fits[x]["fitness"]
        newPop.append(population[x])

    return newPop

# multicored version  
def playBattleshipMultiCore(episodes, population):
    newPop = []
    #if __name__ == '__main__':
    cores = []
    queue = Queue()
    rets = []
    #qTraining(episodes, epsilon, epsilonFactor, qMatrix, moveList, reportValue, epsilonDecay, eta, gamma, hitreward, badReward, missreward, wallreward)
    # start a thread for each child of the original population
    for x in range(len(population)):
        print("Starting new process: " + str(x))
        qMatrix = [[0] * 6 for x in range(1024)] # this will create a blank qMatrix that is 1024 X 6
        moveList = initMoveList()
        core = Process(target=qTraining, args=(episodes, population[x]["epsilon"], population[x]["epsilonFactor"], qMatrix, moveList, 0, population[x]["epsilonDecay"], population[x]["eta"], population[x]["gamma"], population[x]["hitreward"], population[x]["badReward"], population[x]["missreward"], population[x]["wallreward"], queue))
        cores.append(core)
        core.start()

    for x in range(len(cores)):
        ret = queue.get()
        rets.append(ret)
        cores[x].join()
        population[x]["fitness"] = rets[x]
        newPop.append(population[x])
        print("Process " + str(x) + " Has finished")
    
    print("All process have finished.")
    
    return newPop

# attempt to solve for the best qMatrix  
def geneticQ():
    population = initPopulation(POPSIZE)
    newPop = []

    if __name__ == '__main__':
        for i in range(MAXITERATIONS):
            print("Starting training...")
            #newPop = playBattleship(EPISODES, population)
            #newPop = playBattleshipThreaded(EPISODES, population)
            newPop = playBattleshipMultiCore(EPISODES, population)
            print("Training ended...")
            newPop = sortPopulation(newPop)

            if i % OUTPUT == 0:
                avgFit = 0

                for x in range(len(newPop)):
                    avgFit += newPop[x]["fitness"]
                avgFit = avgFit / len(newPop)

                print("Best Child: " + str(newPop[0]) + "\nBest Child fitness: " + str(newPop[0]["fitness"]) + "\nAverage Fitness: " + str(avgFit))

            population = []

            halfLen = round(len(newPop) / 2)
            
            for y in range(halfLen):
                parentA = parentSelection(newPop)
                parentB = parentSelection(newPop)

                children = makeChildren(parentA, parentB)

                population.append(children[0])
                population.append(children[1])

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
        coinFlip = random.randrange(0, 100, 1)

        if coinFlip > 70:
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
def qTraining(episodes, epsilon, epsilonFactor, qMatrix, moveList, reportValue, epsilonDecay, eta, gamma, hitreward, badReward, missreward, wallreward, queue):
    averageReward = []
    averageIterations = []

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
        if e % epsilonDecay == 0 and e != 0 and epsilon > 5:
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
                    iterations += 1
                elif enemyBoard[x][y] == 'X':   # give reward for hits
                    guessBoard[x][y] = 'H'
                    enemyBoard[x][y] = 'H'
                    reward =  hitreward
                    report += hitreward
                    iterations += 1
                
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
                    iterations += 1
                    x -= 1
                elif enemyBoard[x-1][y] == 'X':
                    guessBoard[x-1][y] = 'H'
                    enemyBoard[x-1][y] = 'H'
                    reward =  hitreward
                    report += hitreward
                    iterations += 1
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
                    iterations += 1
                    y += 1
                elif enemyBoard[x][y+1] == 'X':
                    guessBoard[x][y+1] = 'H'
                    enemyBoard[x][y+1] = 'H'
                    reward =  hitreward
                    report += hitreward
                    iterations += 1
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
                    iterations += 1
                    x += 1
                elif enemyBoard[x+1][y] == 'X':
                    guessBoard[x+1][y] = 'H'
                    enemyBoard[x+1][y] = 'H'
                    reward =  hitreward
                    report += hitreward
                    iterations += 1
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
                    iterations += 1
                    y -= 1
                elif enemyBoard[x][y-1] == 'X':
                    guessBoard[x][y-1] = 'H'
                    enemyBoard[x][y-1] = 'H'
                    reward =  hitreward
                    report += hitreward
                    iterations += 1
                    y -= 1

            if option == 5:     # this means that we are shooting a new random location
                x, y = randomShot(guessBoard, enemyBoard) # this will always be a valid location, no walls possible
                if guessBoard[x][y] == 'M':
                    reward =  missreward
                    report += missreward
                    iterations += 1
                else:
                    reward =  hitreward
                    report += hitreward
                    iterations += 1

            current, north, east, south, west = scan(x, y, guessBoard)
            newPerm = getPermutation(moveList, current, north, east, south, west)
            nextAction = pickGreedy(qMatrix, newPerm, epsilon)

            qMatrix[perm][option] += eta * (reward + gamma * qMatrix[newPerm][nextAction] - qMatrix[perm][option])

            finished = checkWin(enemyBoard) # this will stop the while loop once we have finished hitting all of the enemy ships

            # FOR DEBUGGING ONLY!
            #printBoard(enemyBoard)
            #printBoard(guessBoard)
            #print("Turn: " + str(iterations + 1) + " Total reward is: " + str(report)) # output what the reward is for the current turn
        averageReward.append(report)
        averageIterations.append(iterations)
        
        if reportValue != 0 and e % reportValue == 0 and e != 0:
            print("Episode: " + str(e))
            print("Turns to finish: " + str(iterations) + " Total reward is: " + str(report)) # output what the reward is for the current turn
    """
    if threaded == True:
        fit = {
            "thread" : thread,
            "fitness" : sum(averageReward) / len(averageReward)
        }

        fits.append(fit)
    """
    
    #queue.put(sum(averageReward) / len(averageReward))
    #return sum(averageReward) / len(averageReward)
    queue.put((1 / (sum(averageIterations) / len(averageIterations))) * 1000)
    return sum(averageIterations) / len(averageIterations)


def validPos (x:int) -> bool:
    return False if abs(x) > 9 else True


def adjacentShot (x:int, y:int, guess, enemyBoard) -> int:
    '''
        Shoot all tiles adjacent to x,y parameter until another hit
        then continue firing in that 'orientation'
        Once 2 misses on both ends, then ship is sunk and return
        
        Return: iterations passed
    '''

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

    current, north, east, south, west = scan(x, y, guess)

    iterations = 0

    if east == 0 and guess[x][y+1] == ' ': # check if we have already tried to shoot here
        iterations += 1
        if enemyBoard[x][y+1] == ' ': # if there was no ship, record miss, no new info
            guess[x][y+1] = 'M'
        else:                         # if there was a ship, record the hit, orientation now known
            guess[x][y+1] = 'H'
            enemyBoard[x][y+1] = 'H'  
            misses = 0                # AI doesn't know if a ship is sunk, so after 2 misses in either end of orientation, go back to random guess
            i = 2
            while misses != 2:
                iterations += 1
                offset = (-1) ** misses * i   # determines which end of the boat to shoot after a miss
                if validPos(y+offset):
                    if enemyBoard[x][y+offset] == ' ': 
                        guess[x][y+offset] = 'M'
                        misses += 1              # After miss, switch to opposite end
                        i = 1                   # reset distance from initial hit
                    else:                         
                        guess[x][y+offset] = 'H'
                        enemyBoard[x][y+offset] = 'H'
                        i += 1
                else:
                        misses += 1
            return iterations

    if west == 0 and guess[x][y-1] == ' ':   
        iterations += 1
        if enemyBoard[x][y-1] == ' ': 
            guess[x][y-1] = 'M'
        else:                         
            guess[x][y-1] = 'H'
            enemyBoard[x][y-1] = 'H'  
            misses = 0                
            i = 2
            while misses != 2:
                iterations += 1
                offset = (-1) ** misses * i   
                if validPos(y-offset):
                    if enemyBoard[x][y-offset] == ' ': 
                        guess[x][y-offset] = 'M'
                        misses += 1
                        i = 1
                    else:                         
                        guess[x][y-offset] = 'H'
                        enemyBoard[x][y-offset] = 'H'
                        i += 1
                else:
                    misses += 1
            return iterations

    if south == 0 and guess[x+1][y] == ' ': 
        iterations += 1
        if enemyBoard[x+1][y] == ' ': 
            guess[x+1][y] = 'M'
        else:                        
            guess[x+1][y] = 'H'
            enemyBoard[x+1][y] = 'H'  
            misses = 0                
            i = 2
            while misses != 2:
                iterations += 1
                offset = (-1) ** misses * i   
                if validPos(x+offset):
                    if enemyBoard[x+offset][y] == ' ': 
                        guess[x+offset][y] = 'M'
                        misses += 1
                        i = 1
                    else:                         
                        guess[x+offset][y] = 'H'
                        enemyBoard[x+offset][y] = 'H'
                        i += 1
                else:
                    misses += 1
            return iterations    

    if north == 0 and guess[x-1][y] == ' ': 
        iterations += 1
        if enemyBoard[x-1][y] == ' ': 
            guess[x-1][y] = 'M'
        else:                         
            guess[x-1][y] = 'H'
            enemyBoard[x-1][y] = 'H'  
            misses = 0                
            i = 2
            while misses != 2:
                iterations += 1
                offset = (-1) ** misses * i   
                if validPos(x-offset):
                    if enemyBoard[x-offset][y] == ' ': 
                        guess[x-offset][y] = 'M'
                        misses += 1
                        i = 1
                    else:                         
                        guess[x-offset][y] = 'H'
                        enemyBoard[x-offset][y] = 'H'
                        i += 1
                else:
                    misses += 1
            return iterations
    
    return iterations

        


def randomSmartPlay () -> int:
    '''
    Heuristic closest to actual play
    AI attacks random until hit then goes for adjacent tiles until orientation of enemy ship known
    Once ship sunk, repeat
    '''
     # generate a new battle ship board
    enemyBoard = [[' '] * 10 for x in range(10)]
    placeShips(enemyBoard)
    guessBoard = [[' '] * 10 for x in range(10)]

    finished = False       # keeps track of when the computer has finished sinking all ships
    iterations = 0         # this will keep track of how long it took for the AI to sink all of the ships

    attackingAdj = False   # Keeps track of whether next move should be random or one of four possible adjacent tiles

    while not finished:
        iterations += 1
        x, y = randomShot(guessBoard, enemyBoard) # this will always be a valid location, no walls possible
        if guessBoard[x][y] == 'H':
            iterations += adjacentShot(x, y, guessBoard, enemyBoard)

        finished = checkWin(enemyBoard) # this will stop the while loop once we have finished hitting all of the enemy ships

    return iterations


def randomSmartPlayAvg (iterations:int) -> int:
    '''
    Run random smart heuristic param times
    Return average
    '''

    totals = []
    for i in range(iterations):
            totals.append(randomSmartPlay())
    average = sum(totals) / iterations
    print(f'Informed Random: Average over _{iterations}_ iterations: _{average}_')

    # Write to file
    write  = False
    if write:
        with open('SmartRandomResults.csv', 'w') as f:
            iters = range(1,iterations+1)
            data = list(zip(iters, totals))
            for i in data:
                f.write(f"{i}\n")

    return average



def pureRandomPlay () -> int :
    '''
        Complete random play, even if hit, keep doing selecting tiles at random
        return average over param iterations
    '''
 # generate a new battle ship board
    enemyBoard = [[' '] * 10 for x in range(10)]
    placeShips(enemyBoard)
    guessBoard = [[' '] * 10 for x in range(10)]

    finished = False       # keeps track of when the computer has finished sinking all ships
    iterations = 0         # this will keep track of how long it took for the AI to sink all of the ships

    while not finished:
        iterations += 1
        x, y = randomShot(guessBoard, enemyBoard) # this will always be a valid location, no walls possible
    
        finished = checkWin(enemyBoard) # this will stop the while loop once we have finished hitting all of the enemy ships

    return iterations



def pureRandomPlayAvg (iterations: int) -> int :
    '''
    Run complete random param times
    Return average
    '''
    totals = []
    for i in range (iterations):
            totals.append(pureRandomPlay())
    average = sum(totals) / iterations
    print(f'Pure Random: Average over _{iterations}_ iterations: _{average}_')

    # Write to file
    write  = False
    if write:
        with open('pureRandomResults.csv', 'w') as f:
            iters = range(1,iterations+1)
            data = list(zip(iters, totals))
            for i in data:
                f.write(f"{i}\n")


    return average




# population = initPopulation(100)
# print(population)
# population = sortPopulation(population)
# print(population)

iter = 100000
randomSmartPlayAvg(iter)
pureRandomPlayAvg(iter)
#geneticQ()

"""
# qLearning variables
hitreward = 4
badReward = -4
missreward = -12
wallreward = -20




moveList = initMoveList()

file_exists = exists("qMatrix.json")
if file_exists == True:
    f = open("qMatrix.json") 
    qMatrix = json.load(f)
    print("LOADING")
else:
    qMatrix = [[0] * 6 for x in range(1024)] # this will create a blank qMatrix that is 1024 X 6
    print("MAKING NEW MATRIX")

qTraining(100, 25, 0.89, qMatrix, moveList, 10, 10, 0.2, 0.9, hitreward, badReward, missreward, wallreward)
#qTraining(100, 10, 0.8, qMatrix, moveList, 10, 20, 0.2, 0.9, 50, -15, -15, -15)

jsonQMatrix = json.dumps(qMatrix)
with open('qMatrix.json', 'w') as outfile:
    outfile.write(jsonQMatrix)

"""