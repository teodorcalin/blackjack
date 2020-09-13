#!/usr/bin/env python3
# coding=utf-8

from blackjack import *


if __name__ == '__main__':
    c = Casino()
    g = c.newGame(1, 4)
    g.playRound()
