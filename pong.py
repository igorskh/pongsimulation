"""
Pong game algorithm simulation
Author: Igor Kim
E-mail: igor.skh@gmail.com

(c) January, 2017
"""
from random import choice
from mksim import MKSim
from pongai import PongAI


def get_bin(x, n): return format(x, 'b').zfill(n)


class Racket:
    pos = 0
    size = 0
    cols = 0
    destination = 0
    direction = 0
    score = 0

    def __init__(self, cols, size):
        self.pos = (cols // 2) - size//2
        self.size = size
        self.cols = cols
        self.score = 0

    def set_destination(self, dest):
        self.destination = dest
        if self.destination > self.pos + self.size -1:
            self.direction = 1
        elif self.destination < self.pos:
            self.direction = -1
        else:
            self.direction = 0

    def move(self):
        if self.destination >= self.pos and self.destination <= self.pos +self.size-1:
            return False
        if self.pos + self.direction > -1 and self.pos + self.size - 1 + self.direction < self.cols:
            self.pos += self.direction

    def get_pos(self):
        line = int('1'*self.size + '0'*(self.cols-self.size), 2) >> self.pos
        return get_bin(line,self.cols)


class Ball:
    pos = [0,0]
    direction = [0,0]
    cols = 0
    rows = 0

    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.reset()

    def next_pos2(self):
        return [self.pos[0] + self.direction[0],self.pos[1] + self.direction[1]]

    def reset(self, auto_move=True):
        new_position = [self.rows//2, self.cols//2]
        self.direction[1] = 0
        self.direction[0] = choice([-1,1])
        if auto_move:
            self.pos = [new_position[0], new_position[1]]
        else:
            return new_position

    def bounce(self, player=False, wall=False):
        if wall:
            self.direction[1] *= -1
        if player:
            self.direction[0] *= -1
            self.direction[1] = choice([0,-1,1])
        return self.next_pos2()

    def move(self, defined_pos = None):
        if defined_pos is None:
            defined_pos = self.next_pos2()
        old_pos = (self.pos[0], '0'*self.cols)
        self.pos = defined_pos
        return old_pos, self.get_pos()

    def get_pos(self, defined_pos=None):
        if defined_pos is None:
            defined_pos = self.pos
        # TODO: Sometimes defined_pos[1]  goes to negative, why??
        line = int('1' + '0' * (self.cols - 1), 2) >> defined_pos[1]
        return defined_pos[0], get_bin(line, self.cols)


class PongGame:
    rows = 0
    cols = 0
    mk = None
    pongai = None

    racket1 = None
    racket2 = None
    ball = None

    buffer = []
    started = False
    destination_column = 0
    frame_rate = 0.5

    # prepares data to be sent via i2c
    @staticmethod
    def prepare(line, data):
        return [int(get_bin(line, 4) + data[0:4], 2), int(data[4:], 2)]

    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.mk = MKSim(rows, cols)
        self.new_game()
        self.pongai = PongAI(rows, cols, 2)

    def new_game(self):
        # initialize rackets, second arg is a size
        self.racket1 = Racket(self.cols, 2)
        self.racket2 = Racket(self.cols, 2)
        # initialize ball
        self.ball = Ball(self.rows, self.cols)
        # set destination column of ball
        self.destination_column = self.ball.pos[1]
        # add init positions to buffer
        self.add_buffer(self.ball.get_pos())
        self.add_buffer((0, self.racket1.get_pos()))
        self.add_buffer((self.rows-1, self.racket2.get_pos()))
        # send initialize positions of rackets and ball
        self.send()
        self.started = True

    def step2(self):
        # calculate next position of the ball
        ball_new_position = self.ball.next_pos2()
        # move rackets to new position
        self.racket1.move()
        self.racket2.move()
        # check if new position is one of side walls
        if ball_new_position[1] in (-1, self.cols):
            # change direction, bounce out of wall
            ball_new_position = self.ball.bounce(False, True)
        # check if new position is a line of racket
        if ball_new_position[0] in (0, self.rows - 1):
            ball_row = int(self.ball.get_pos(ball_new_position)[1], 2)
            racket_row = int(self.racket1.get_pos(), 2) if ball_new_position[0] == 0 else int(self.racket2.get_pos(), 2)
            # check if racket meets ball
            if racket_row & ball_row:
                # change direction
                ball_new_position = self.ball.bounce(True, False)
            else:
                # goal
                if ball_new_position[0] == 0:
                    self.racket2.score += 1
                else:
                    self.racket1.score += 1
                # throw ball to the center
                ball_new_position = self.ball.reset(False)
            # update balls destination
            self.destination_column = self.pongai.calculate_destination(ball_new_position, self.ball.direction)
            # check if it towards player one or two
            if self.ball.direction[0] == 1:
                self.racket2.set_destination(self.destination_column)
            else:
                self.racket1.set_destination(self.destination_column)
        # calculate old cleared position and new position
        ball_positions = self.ball.move(ball_new_position)
        # clear old ball position to buffer
        self.add_buffer(ball_positions[0])
        # add new positions of ball and rackets to send buffer
        self.add_buffer(ball_positions[1])
        self.add_buffer((0, self.racket1.get_pos()))
        self.add_buffer((self.rows - 1, self.racket2.get_pos()))
        # send new positions to mk
        self.send()

    def add_buffer(self, data):
        prepared_data = self.prepare(data[0], data[1])
        self.buffer.append([prepared_data[0], prepared_data[1]])

    def send(self):
        # TODO: rewrite to .pop() method
        for el in self.buffer:
            self.mk.recv(el[0], el[1])
        self.buffer = []

    def show_table(self):
        self.mk.show_table()