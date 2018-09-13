''' Brian Goldsberry
    beg12 '''

from __future__ import print_function
from PyQt5 import QtWidgets, QtCore
import sys, random, time, os, enchant, time
class boggleWindow(QtWidgets.QMainWindow):
    def __init__(self):
        self.startNew = True
        QtWidgets.QWidget.__init__(self)
        self.open = QtWidgets.QMessageBox()
        self.open.setText('Would you like to start a new game or load a saved game?')
        self.open.addButton('Start New Game', 0)
        self.open.addButton('Load Game', 1)
        self.open.buttonClicked.connect(self.newOrLoad)
        self.open.exec_()
        self.boggle_game = BoggleGame(self)
        self.setCentralWidget(self.boggle_game)
        menu_bar = self.menuBar()
        menu_bar.setNativeMenuBar(False)
        game_menu = menu_bar.addMenu('Game')
        new_action = QtWidgets.QAction('New', self)
        new_action.triggered.connect(self.boggle_game.newGame)
        load_action = QtWidgets.QAction('Load', self)
        load_action.triggered.connect(self.boggle_game.loadGame)
        save_action = QtWidgets.QAction('Save', self)
        save_action.triggered.connect(self.boggle_game.saveGame)
        game_menu.addAction(new_action)
        game_menu.addAction(load_action)
        game_menu.addAction(save_action)
        self.show()

    def newOrLoad(self, i):
        if i.text() == 'Load Game':
            self.startNew = False
        else:
            self.startNew = True

class BoggleGame(QtWidgets.QWidget):
    def __init__(self, parent):
        QtWidgets.QWidget.__init__(self, parent)
        self.open = QtWidgets.QMessageBox(self)
        self.grid = QtWidgets.QGridLayout()
        self.setLayout(self.grid)
        self.secondTimer = QtCore.QTimer(self)
        self.secondTimer.setInterval(1000)
        self.totalTime = 180
        self.textBox = QtWidgets.QTextEdit(self)
        self.textBox.setReadOnly(True)
        self.grid.addWidget(self.textBox, 1, 5, 4, 4)
        self.lineBox = QtWidgets.QLineEdit(self)
        self.grid.addWidget(self.lineBox, 5, 1, 1, 6)
        self.timerBox = QtWidgets.QLCDNumber(self)
        self.grid.addWidget(self.timerBox, 5, 7, 1, 2)
        self.lineBox.returnPressed.connect(self.return_pressed)
        self.secondTimer.timeout.connect(self.print_time)
        if not parent.startNew:
            self.loadGame()
        else:
            self.setup()

    def setup(self):
        self.labels = []
        self.textBox.clear()
        self.lineBox.clear()
        self.timeLeft = self.totalTime
        self.dice = self.get_dice()
        i = 0
        j = 1
        for row in self.dice:
            for die in row:
                if die == 'Q':
                    dieLabel = QtWidgets.QLabel('Qu', self)
                else:
                    dieLabel = QtWidgets.QLabel(die, self)
                self.labels.append(dieLabel)
                self.grid.addWidget(dieLabel, j, i%4+1)
                i += 1
                if i == 4:
                    j = 2
                elif i == 8:
                    j = 3
                elif i == 12:
                    j = 4
                else:
                    pass
        self.secondTimer.start()

    def end_game(self):
        self.end_message = QtWidgets.QMessageBox(self)
        total = self.get_score()
        self.end_message.setText('Time\'s up!\nScore: ' + str(total) +'\nWould you like to play again?')
        self.end_message.addButton('Yes', 5)
        self.end_message.addButton('No', 6)
        self.grid.addWidget(self.end_message)
        self.end_message.buttonClicked.connect(self.end_selection)

    def get_score(self):
        words = self.textBox.toPlainText().split('\n')
        wordList = list(words)
        #variables for total score, a list for already scored words, and dictionary
        total = 0
        scoredWords = []
        d = enchant.Dict("en_US")

        #start checking words
        for i in wordList:
            i = i.upper()
            print(i)
            #variable to store coordinates
            sameDiceCheck = []
            #first make sure word hasn't been scored already
            if str(i) in scoredWords:
                print ("The word", i, "has already been used.")
                continue
            #check to see if word is too short
            if len(i) < 3:
                print ("The word", i, "is too short.")
                continue
            #check if entry is actually a word
            if not d.check(str(i)):
                print ("The word", i, "is ... not a word.")
                continue
            #check if word can be found on grid
            if not self.grid_check(str(i), self.dice, sameDiceCheck):
                #check if word reuses the same die
                if not self.dice_check(sameDiceCheck):
                    print ("the word", i, "reuses the same die.")
                else:
                    print ("The word", i, "is not present.")
                continue
            #calculate total points and let user know
            points = self.get_points(len(i))
            total = total + points
            scoredWords.append(i)
        return total


    def saveGame(self):
        saveFile = open(time.strftime("%c"), "w")
        saveFile.write(str(time.time()) + '\n')
        for die in self.labels:
            saveFile.write(die.text() + '\n')
        saveFile.write(str(self.timeLeft) + '\n')
        saveFile.write(self.textBox.toPlainText())
        saveFile.close()

    def loadGame(self):
        self.loadMenu = QtWidgets.QListWidget(self)
        files = [f for f in os.listdir('.') if os.path.isfile(f)]
        for fi in files:
            if fi.endswith('.py'):
                files.remove(fi)
        fileDict = {}
        for i in files:
            load = open(i, 'r')
            key = load.readline()
            load.close()
            fileDict[key] = i
        sortedKeys = sorted(fileDict, reverse=True)
        for key in sortedKeys:
            self.loadMenu.addItem(fileDict[key])
        self.loadMenu.itemClicked.connect(self.loadFile)
        self.grid.addWidget(self.loadMenu)

    def loadFile(self, item):
        for i in self.labels:
                i.setHidden(True)
        self.labels = []
        i = 0
        j = 1
        load = open(item.text(), 'r')
        time = load.readline()
        self.dice = []
        row = []
        for i in range(16):
            die = load.readline()
            die = die.strip('\n')
            row.append(die)
            dieLabel = QtWidgets.QLabel(die, self)
            self.labels.append(dieLabel)
            self.grid.addWidget(dieLabel, j, i%4+1)
            i += 1
            if i == 4:
                j = 2
                self.dice.append(row)
                row = []
            elif i == 8:
                self.dice.append(row)
                row = []
                j = 3
            elif i == 12:
                self.dice.append(row)
                row = []
                j = 4
            elif i == 16:
                self.dice.append(row)
            else:
                pass
        self.timeLeft = int(load.readline())
        self.textBox.clear()
        self.lineBox.clear()
        self.textBox.setText(load.read())
        self.secondTimer.start()
        self.loadMenu.setHidden(True)
        load.close()

    def end_selection(self, i):
        if i.text() == 'Yes':
            self.newGame()
        else:
            sys.exit()

    def newGame(self):
        for i in self.labels:
                i.setHidden(True)
        self.setup()

    def print_time(self):
        self.timerBox.display(self.timeLeft)
        if self.timeLeft > 0:
            self.timeLeft -= 1
        else:
            self.secondTimer.stop()
            self.end_game()

        
    def get_dice(self):
        #variables for dice
        DIE1 = ['A', 'E', 'A', 'N', 'E', 'G']
        DIE2 = ['A', 'H', 'S', 'P', 'C', 'O']
        DIE3 = ['A', 'S', 'P', 'F', 'F', 'K']
        DIE4 = ['O', 'B', 'J', 'O', 'A', 'B']
        DIE5 = ['I', 'O', 'T', 'M', 'U', 'C']
        DIE6 = ['R', 'Y', 'V', 'D', 'E', 'L']
        DIE7 = ['L', 'R', 'E', 'I', 'X', 'D']
        DIE8 = ['E', 'I', 'U', 'N', 'E', 'S']
        DIE9 = ['W', 'N', 'G', 'E', 'E', 'H']
        DIE10 = ['L', 'N', 'H', 'N', 'R', 'Z']
        DIE11 = ['T', 'S', 'T', 'I', 'Y', 'D']
        DIE12 = ['O', 'W', 'T', 'O', 'A', 'T']
        DIE13 = ['E', 'R', 'T', 'T', 'Y', 'L']
        DIE14 = ['T', 'O', 'E', 'S', 'S', 'I']
        DIE15 = ['T', 'E', 'R', 'W', 'H', 'V']
        DIE16 = ['N', 'U', 'I', 'H', 'M', 'Q']

        #starts off with list of dice and empty grid
        dice = [DIE1, DIE2, DIE3, DIE4, DIE5, DIE6, DIE7,
            DIE8, DIE9, DIE10, DIE11, DIE12, DIE13, DIE14, DIE15, DIE16]

        grid = []

        #randomly select a die and a side and store in a row
        #after 4 iterations, store row in grid creating 2x2 matrix
        for i in range(0, 4):
            row = []
            for j in range(0, 4):
                randDie = dice[random.randint(0, len(dice)-1)]
                randSide = randDie[random.randint(0, 5)]
                row.append(randSide)
                dice.remove(randDie)
            grid.append(row)
        return grid

    def return_pressed(self):
        word = self.lineBox.text()
        self.lineBox.clear()
        self.textBox.append(word)
        
    #function that finds first letter that matches given word
    #to see if it is in the grid
    def grid_check(self, entry, grid, die_check):
        #grid is a 2x2 matrix, so run through all elements
        for i in range(0, 4):
            for j in range(0, 4):
                if entry[0] == grid[i][j]:
                    #if a word can be made and it doesn't repeat die, return true
                    if self.make_word(i, j, entry, grid, 0, die_check):
                        if self.dice_check(die_check):
                            return True
                       #if it does make a word, but reuses a die, then keep checking
                        else:
                            die_check = []
                    #if word can't be made, keep checking
                    else:
                        die_check = []
        #if all elements are checked, return false
        return False

    #function builds words out of the grid to see if it matches given word
    #index is the character that is being checked in given word and dieCheck
    #is a list of grid coordinates that make up the word
    def make_word(self, row, column, word, grid, index, die_check):
        #assume the user inputs a 'u' after 'q' and skip to next letter to be checked
        if grid[row][column] == 'Q':
            index = index+1
        #adds coordinates to list
        die_check.append([row, column])
        #if we reach the end of the word, return true
        if index == (len(word) - 1):
            return True
        index = index+1
        #check top
        if row != 0:
            if grid[row-1][column] == word[index]:
                if not self.make_word(row-1, column, word, grid, index, die_check):
                    pass
                else:
                    return True
        #check bottom
        if row != 3:
            if grid[row+1][column] == word[index]:
                if not self.make_word(row+1, column, word, grid, index, die_check):
                    pass
                else:
                    return True
        #check left
        if column != 0:
            if grid[row][column-1] == word[index]:
                if not self.make_word(row, column-1, word, grid, index, die_check):
                    pass
                else:
                    return True
            #check right
        if column != 3:
            if grid[row][column+1] == word[index]:
                if not self.make_word(row, column+1, word, grid, index, die_check):
                    pass
                else:
                    return True
        #check top left
        if row != 0 and column != 0:
            if grid[row-1][column-1] == word[index]:
                if not self.make_word(row-1, column-1, word, grid, index, die_check):
                    pass
                else:
                    return True
        #check top right
        if row != 0 and column != 3:
            if grid[row-1][column+1] == word[index]:
                if not self.make_word(row-1, column+1, word, grid, index, die_check):
                    pass
                else:
                    return True
        #check bottom left
        if row != 3 and column != 0:
            if grid[row+1][column-1] == word[index]:
                if not self.make_word(row+1, column-1, word, grid, index, die_check):
                    pass
                else:
                    return True
        #check bottom right
        if row != 3 and column != 3:
            if grid[row+1][column+1] == word[index]:
                if not self.make_word(row+1, column+1, word, grid, index, die_check):
                    pass
                else:
                    return True
        return False

    #function returns number of points based on length of word
    def get_points(self, num):
        if num == 3 or num == 4:
            return 1
        elif num == 5:
            return 2
        elif num == 6:
            return 3
        elif num == 7:
            return 5
        else:
            return 11

    #checks a list of coordinates to see if any are repeated
    def dice_check(self, position_list):
        for i in range(0, len(position_list)-1):
            for j in range(i+1, len(position_list)):
                if position_list[i] == position_list[j]:
                    return False
        return True

app = QtWidgets.QApplication(sys.argv)
main_window = boggleWindow()
app.exec_()
