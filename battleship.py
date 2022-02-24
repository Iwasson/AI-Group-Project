import json

Player1_Board = [['X'] * 10 for x in range(10)]
Player2_Board = [[' '] * 10 for x in range(10)]

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

printBoard(Player1_Board)
    