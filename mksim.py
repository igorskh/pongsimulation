"""
Pong game algorithm simulation
Author: Igor Kim
E-mail: igor.skh@gmail.com

(c) January, 2017
"""
from sys import stdout
from time import sleep


def get_bin(x, n): return format(x, 'b').zfill(n)


def get_bit(b, n): return (b & (1 << n)) >> n


class MKSim:
    rows = 0
    cols = 0
    table = []
    frame_rate = 0.5
    showed = False

    # clear n rows of stdout
    def clear(self, n=None):
        if n is None:
            n = self.rows
        stdout.write("\033[F\033[K" * n)
        sleep(self.frame_rate)

    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        for row in range(self.rows):
            self.table.append(0)

    def show_table(self):
        if self.showed:
            self.clear()
        for row in range(self.rows):
            print(get_bin(self.table[row], self.cols))
        self.showed = True

    def recv(self, address, byte):
        line = (address & 0xF0) >> 4
        data = 0b000000000000
        data |= (address & 0x0F) << 8
        data |= byte
        self.table[line] = data
