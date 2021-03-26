import matplotlib.pyplot as plt
import PyQt5.QtWidgets as QW
import PyQt5.QtGui as QG
import PyQt5.QtCore as QC
import numpy as np
import itertools as itr
import sys
import functools as fts

blocks=np.reshape([
        [0,1,0,1,0,1,0,1],
        [1,1,0,1,0,1,0,0],
        [0,1,1,1,0,1,0,0],
        [0,1,0,1,1,1,0,0],
        [1,1,1,1,0,0,0,0],
        [0,1,1,1,1,0,0,0],
        [1,0,1,1,0,1,0,0]],(7,4,2))

class Tetris:
    def __init__(self,H,W):
        self.W=W
        self.H=H
        self.board=np.zeros((H,W))
        self.points=0
        self.next_block=blocks[np.random.randint(7)]
        self.add_block()
        self.over=False
        self.started=False

    def start(self):
        self.started=True

    def add_block(self):
        self.block=self.next_block[:]
        self.next_block=blocks[np.random.randint(7)]
        self.pos=(0,self.W//2)

    def data(self):
        nr,nc=self.block.shape
        r,c=self.pos
        data=self.board.copy()
        data[r:r+nr,c:c+nc]=self.block.copy()
        return data

    def rotCW(self):
        self.block=self.block[::-1].T

    def rotCCW(self):
        self.block=self.block.T[::-1]

    def moveRight(self):
        r,c=self.pos
        if not self.invalid_block(r,c+1):
            self.pos=r,c+1

    def moveLeft(self):
        r,c=self.pos
        if not self.invalid_block(r,c-1):
            self.pos=r,c-1

    def check_status(self):
        full_line_args=np.argwhere(np.all(self.board,axis=1))
        L=len(full_line_args)
        self.points+=10*2**L
        self.board[L:]=np.delete(self.board,full_line_args,axis=0)

    def invalid_block(self,r,c):
        nr,nc=self.block.shape
        return r+nr>=self.H or c<0 or c+nc>=self.W or np.any(self.block*self.board[r:r+nr,c:c+nc])

    def update(self):
        nr,nc=self.block.shape
        r,c=self.pos
        if self.invalid_block(r+1,c):
            self.board[r:r+nr,c:c+nc]=self.block[:]
            self.check_status()
            self.add_block()
            if self.invalid_block(*self.pos):
                self.over=True
        else:
            self.pos=r+1,c


class View:
    def __init__(self,game):
        self.fig,self.ax=plt.subplots()
        self.fig.canvas.mpl_disconnect(self.fig.canvas.manager.key_press_handler_id)

        self.fig.canvas.mpl_connect("key_press_event",self.handle_key_presses)


        self.ax.grid(color="white",linewidth=2)
        for iax in (self.ax.xaxis,self.ax.yaxis):
            for tic in iax.get_major_ticks():
                for t in (tic.tick1line,tic.tick2line,tic.label1,tic.label2):
                    t.set_visible(False)
        self.game=game

        self.board = self.ax.imshow(self.game.data(),cmap="gray_r",vmin=-0.2,vmax=1)
        self.ax.set_yticks(np.arange(-0.5,game.H,1))
        self.ax.set_xticks(np.arange(-0.5,game.W,1))
        self.ax.set_xlim(-0.5,game.W-0.5)
        self.ax.set_ylim(game.H-0.5,-0.5)
        self.timer = self.fig.canvas.new_timer(interval=500)
        self.timer.add_callback(self.update)
        self.timer.start()

        self.cmds=dict(right= self.game.moveRight,
                       left = self.game.moveLeft,
                       up   = self.game.rotCW,
                       down = self.game.update)


    def handle_key_presses(self,event):
        key=event.key
        cmd=self.cmds.get(event.key)
        if cmd: cmd()
        self.draw()

    def draw(self):
        self.game.update()
        self.board.set_array(self.game.data())
        self.fig.canvas.draw()

    def update(self):
        if not self.game.started:
            return
        if self.game.over:
            self.timer.stop()
        self.draw()

    def show(self):
        self.fig.show()




if __name__=="__main__":

    new_game=Tetris(20,10)

    view=View(new_game)
    view.show()

    new_game.start()