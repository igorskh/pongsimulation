"""
Pong game AI algorithm
Author: Igor Kim
E-mail: igor.skh@gmail.com

(c) January, 2017
"""


class PongAI:
    rows = 0
    size = 0
    cols = 0

    def __init__(self, rows, cols, size):
        # field size
        self.rows = rows-2
        self.cols = cols
        # racket size
        self.size = size

    # return column number
    def calculate_destination(self, ball_position, direction):
        # flights in straight direction
        if direction[1] == 0:
            return ball_position[1]
        # flights with an angle
        # TODO: something wrong with direction with an angle
        else:
            check = ball_position[1] + direction[1]*(self.rows - 1)
            # will bounce out of right border
            if check >= self.cols:
                check -= self.cols-1
                check = self.cols - check
                return check
            # will bounce out of left border
            elif check < 0:
                return abs(check)
            # won't bounce during the flight
            else:
                return check
