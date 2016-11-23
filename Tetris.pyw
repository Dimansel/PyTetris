from tkinter import *
from random import randint

class Tetris(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master.resizable(width=False, height=False)
        self.interval = 400        #speed of active tetrominoe falling (one step per 400ms)
        self.cell_size = 25        #width (height) of one cell in pixels
        self.rows = 20             #number of rows
        self.cols = 10             #number of columns
        #list of tetrominoes. each element is a list that has lists - rows of tetrominoe (0 is an empty space, 1 is filled rectangle)
        self.figures = [[[1,1], [1,1]], [[0,1,0], [1,1,1]], [[0,1,1], [1,1,0]], [[1,1,0], [0,1,1]], [[1,0,0], [1,1,1]], [[0,0,1], [1,1,1]], [[1,1,1,1]]]
        #list of colors of tetrominoes. has to be the same length as the self.figures
        self.colors = ['yellow', 'purple', 'lime', 'red', 'blue', 'orange', 'cyan']
        self.rects = None                   #list of rectangles of all fallen tetrominoes (not active)
        self.currentFigure = None           #active tetrominoe
        self.t = None                       #here will be stored result of calling function "after". needed for cancelling next calls and stopping "timer" as the result
        self.old_interval = self.interval   #saving initial interval, because "self.interval" is decreasing when line is fully filled by rectangles
        self.pack()                         #using "pack" layout manager
        self.createCanvas()                 #creating Canvas and binding events to it
        self.initializeGame()               #setting all variables to initial values and deleting all the things on Canvas

    def createCanvas(self):
        self.canvas = Canvas(self, width=self.cell_size*self.cols+1, height=self.cell_size*self.rows+1, bd=0, highlightthickness=0, relief='ridge', bg='#FFFFFF')
        self.canvas.pack()
        self.canvas.focus_set()                           #setting focus to get key events working
        self.canvas.bind('<Right>', self.move(1, 0))      #bind "right arrow" key for moving active tetrominoe right
        self.canvas.bind('<Left>', self.move(-1, 0))      #bind "left arrow" key for moving active tetrominoe left
        self.canvas.bind('<Up>', self.rotate)             #bind "up arrow" key for rotating active tetrominoe by 90deg CCW
        self.canvas.bind('<Down>', self.move(0, 1))       #bind "down arrow" key for moving active tetrominoe down
        self.canvas.bind('n', self.initializeGame)        #bind "N" key to start new game
        self.down = self.move(0, 1)                       #function moves down active tetrominoe

    def initializeGame(self, ev=None):
        self.score = 0                                           #stores user's score
        self.interval = self.old_interval
        self.master.title('Score: ' + str(self.score))
        self.deleteRects()                                       #deleting rectangles of all inactive tetrominoes
        self.deleteCurrentFigure()                               #deleting rectangles of active tetrominoe
        self.rects = [[None for i in range(self.cols)] for j in range(self.rows)]
        self.currentFigure = None
        if self.t != None: self.after_cancel(self.t)             #stops the "timer"
        self.spawnRandomFigure()                                 #choosing random tetrominoe and making it active
        self.tick()                                              #starting the "timer"
    
    def deleteRects(self):
        if self.rects == None: return
        for row in self.rects:
            for col in row:
                if col != None: self.canvas.delete(col)

    def deleteCurrentFigure(self):
        if self.currentFigure == None: return
        for row in self.currentFigure:
            for col in row:
                if col != -1: self.canvas.delete(col)
    
    def tick(self):
        #self.down returns True if active tetrominoe was able to make one step down, otherwise we have to make it inactive and generate another
        if not self.down(): return self.pinFigure()
        self.t = self.after(self.interval, self.tick)    #this will call tick() after 'self.interval' milliseconds. that's a way to make a "timer"
    
    #makes active tetrominoe inactive and generates a new one. if there is no space to place it game is over
    def pinFigure(self):
        for row in self.currentFigure:
            for col in row:
                if col == -1: continue
                coords = [int(a/self.cell_size) for a in self.canvas.coords(col)]
                self.rects[coords[1]][coords[0]] = col
        self.checkLines()        #checks if there are fully filled lines. if there is - remove it and increase score
        #spawnRandomFigure returns True if generated tetrominoe has been successfully placed, otherwise we have to over the game
        if self.spawnRandomFigure():
            self.tick()
        else:        #deleting last generated tetrominoe and show "game over" messagebox
            for row in self.currentFigure:
                for col in row:
                    if col != -1:
                        self.canvas.delete(col)
            self.currentFigure = None
            messagebox.showinfo('Game over', 'You scored ' + str(self.score))
    
    #checks if game field has a fully filled horizontal lines of rectangles
    #if it has - remove it, increase score and move down all the rectangles above the line
    def checkLines(self):
        for i in range(self.rows):
            solid = True
            for j in range(self.cols):
                if self.rects[i][j] == None:
                    solid = False
                    break
            if solid:
                self.score += self.cols
                self.interval -= 1
                self.master.title('Score: ' + str(self.score))
                for j in range(self.cols):
                    self.canvas.delete(self.rects[i][j])
                    self.rects[i][j] = None
                for k in range(i-1, -1, -1):
                    for j in range(self.cols):
                        if self.rects[k][j] == None: continue
                        self.rects[k+1][j] = self.rects[k][j]
                        self.rects[k][j] = None
                        self.canvas.move(self.rects[k+1][j], 0, self.cell_size)
    
    #returns a new rectangle created at (j, i) coordinates of so called "grid"
    def spawnRectangle(self, i, j, color):
        return self.canvas.create_rectangle(j*self.cell_size, i*self.cell_size, (j+1)*self.cell_size, (i+1)*self.cell_size, outline='#000000', fill=color)
    
    #randomly chooses tetrominoe from "self.figures" and places it approximately at center of the the first row (highest)
    def spawnRandomFigure(self):
        i = randint(0, len(self.figures)-1)
        matrix = self.figures[i]
        self.currentFigure = []
        for row in range(len(matrix)):
            self.currentFigure.append([])
            for col in range(len(matrix[row])):
                if matrix[row][col] == 0: self.currentFigure[-1].append(-1)
                else:
                    if self.rects[row][col+self.cols//2-1] != None: return False
                    self.currentFigure[-1].append(self.spawnRectangle(row, col+self.cols//2-1, self.colors[i]))
        return True

    def _rotate(self):
        newFigure = []
        for col in range(len(self.currentFigure[0])-1, -1, -1):
            newFigure.append([])
            for row in range(len(self.currentFigure)):
                newFigure[-1].append(self.currentFigure[row][col])
                self.canvas.move(self.currentFigure[row][col], (row-col)*self.cell_size, (len(newFigure)-row-1)*self.cell_size)
        self.currentFigure = newFigure
    
    #rotates active tetrominoe by 90 degrees counterclockwise
    def rotate(self, ev=None):
        if self.currentFigure == None: return
        self._rotate()
        if not self.canStay(0, 0):
            for _ in range(3): self._rotate()
    
    #returns the function that moves active tetrominoe by "dx", "dy" in the "grid"
    def move(self, dx, dy):
        def _move(ev = None):
            if self.currentFigure == None or not self.canStay(dx, dy): return False
            for row in self.currentFigure:
                for col in row:
                    if col == -1: continue
                    self.canvas.move(col, dx*self.cell_size, dy*self.cell_size)
            return True
        return _move
    
    #checks if active tetrominoe can "legally" stay in it's place with "dx", "dy" offset and returns the corresponding result
    def canStay(self, dx, dy):
        for row in self.currentFigure:
            for col in row:
                if col == -1: continue
                coords = [int(a/self.cell_size) for a in self.canvas.coords(col)]
                if coords[0]+dx < 0 or coords[0]+dx >= self.cols: return False
                if coords[1]+dy < 0 or coords[1]+dy >= self.rows: return False
                if self.rects[coords[1]+dy][coords[0]+dx] != None: return False
        return True

tetris = Tetris()
tetris.mainloop()
