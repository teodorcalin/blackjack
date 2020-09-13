#!/usr/bin/env python3
# coding=utf-8

from cards import *
from blackjack import *

c1 = Card(Suite.HEART, Value.NINE)
print(c1)
c2 = Card(Suite.SPADE, Value.QUEEN)
print(c2)
ph = PlayerHand()
ph.update(c1)
ph.update(c2)
print(f'Player hand: {ph}')
gd = GameDeck(1)
print(f'Initial game deck: {gd}')
c3 = gd.dealCard()
print(f'Dealt card: {c3}')
dh = DealerHand()
dh.update(gd.dealCard())
dh.update(gd.dealCard())
print(f'Dealt dealer hand: {dh}')
print(f'Game deck after dealing: {gd}')
