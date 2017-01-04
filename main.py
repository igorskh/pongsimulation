"""
Pong game algorithm simulation
Author: Igor Kim
E-mail: igor.skh@gmail.com

(c) January, 2017
"""
from pong import PongGame

if __name__ == '__main__':
    game = PongGame(10, 12)
    while game.started:
        game.step2()
        if game.started:
            game.show_table()