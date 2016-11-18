from tkinter import *
from random import randint

class Tetris(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master.resizable(width=False, height=False)
        self.interval = 400
        self.cell_size = 25
        self.rows = 20
        self.cols = 10
        self.figures = [[[1,1], [1,1]], [[0,1,0], [1,1,1]], [[0,1,1], [1,1,0]], [[1,1,0], [0,1,1]], [[1,0,0], [1,1,1]], [[0,0,1], [1,1,1]], [[1,1,1,1]]]
        self.colors = ['yellow', 'purple', 'lime', 'red', 'blue', 'orange', 'cyan']
        self.rects = None
        self.currentFigure = None
        self.t = None
        self.old_interval = self.interval
        self.pack()
        self.createCanvas()
        self.initializeGame()

    def createCanvas(self):
        self.canvas = Canvas(self, width=self.cell_size*self.cols+1, height=self.cell_size*self.rows+1, bd=0, highlightthickness=0, relief='ridge', bg='#FFFFFF')
        self.canvas.pack()
        self.canvas.focus_set()
        self.canvas.bind('<Right>', self.move(1, 0))
        self.canvas.bind('<Left>', self.move(-1, 0))
        self.canvas.bind('<Up>', self.rotate)
        self.canvas.bind('<Down>', self.move(0, 1))
        self.canvas.bind('n', self.initializeGame)
        self.down = self.move(0, 1)

    def initializeGame(self, ev=None):
        self.score = 0
        self.interval = self.old_interval
        self.master.title('Score: ' + str(self.score))
        self.deleteRects()
        self.deleteCurrentFigure()
        self.rects = [[None for i in range(self.cols)] for j in range(self.rows)]
        self.currentFigure = None
        if self.t != None: self.after_cancel(self.t)
        self.spawnRandomFigure()
        self.tick()
    
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
        if not self.down(): return self.pinFigure()
        self.t = self.after(self.interval, self.tick)

    def pinFigure(self):
        for row in self.currentFigure:
            for col in row:
                if col == -1: continue
                coords = [int(a/self.cell_size) for a in self.canvas.coords(col)]
                self.rects[coords[1]][coords[0]] = col
        self.checkLines()
        if self.spawnRandomFigure():
            self.tick()
        else:
            for row in self.currentFigure:
                for col in row:
                    if col != -1:
                        self.canvas.delete(col)
            self.currentFigure = None
            messagebox.showinfo('Game over', 'You scored ' + str(self.score))

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
    
    def spawnRectangle(self, i, j, color):
        return self.canvas.create_rectangle(j*self.cell_size, i*self.cell_size, (j+1)*self.cell_size, (i+1)*self.cell_size, outline='#000000', fill=color)

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
    
    def rotate(self, ev=None):
        if self.currentFigure == None: return
        self._rotate()
        if not self.canStay(0, 0):
            for _ in range(3): self._rotate()
    
    def move(self, dx, dy):
        def _move(ev = None):
            if self.currentFigure == None or not self.canStay(dx, dy): return False
            for row in self.currentFigure:
                for col in row:
                    if col == -1: continue
                    self.canvas.move(col, dx*self.cell_size, dy*self.cell_size)
            return True
        return _move
    
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
