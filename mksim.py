"""
Pong game algorithm simulation
Author: Igor Kim
E-mail: igor.skh@gmail.com

(c) January, 2017
"""
from sys import stdout
from time import sleep
from subprocess import call


def get_bin(x, n): return format(x, 'b').zfill(n)


def get_bit(b, n): return (b & (1 << n)) >> n


class MKSim:
    # number of rows and columns
    rows = 0
    cols = 0
    table = []
    # frame rate for updating command line
    frame_rate = 0.5
    # set to true if the tables was showed at least once in cmd
    showed = False
    # set this to true if you want data to be transferred via i2c
    i2c_enabled = False
    # i2c bus number
    bus_number = 1
    # i2c device address
    address = 0x60

    # clear n rows of stdout and wait frame rate time
    def clear(self, n=None):
        if n is None:
            n = self.rows
        stdout.write("\033[F\033[K" * n)
        sleep(self.frame_rate)

    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        # fill table with zeros
        for row in range(self.rows):
            self.table.append(0)

    # show all content of the table
    def show_table(self):
        if self.showed:
            self.clear()
        for row in range(self.rows):
            print(get_bin(self.table[row], self.cols))
        self.showed = True

    def recv(self, address, byte):
        if self.i2c_enabled:
            # smbus is usually not installed then use i2cset utility
            call(["i2cset", "-y", str(self.bus_number), str(self.address), hex(address), hex(byte)])
        # first 4 bits is a line number
        line = (address & 0xF0) >> 4
        # last 4 address bits are 4 MSB of data
        data = 0b000000000000
        # then 8 LSB of data
        data |= (address & 0x0F) << 8
        data |= byte
        # save data to table
        self.table[line] = data
