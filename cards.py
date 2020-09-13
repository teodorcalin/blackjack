#!/usr/bin/env python3
# coding=utf-8

from enum import Enum, IntEnum, auto

class Suite(Enum):
    DIAMOND = 'DIAMOND', 9830
    CLUB = 'CLUB', 9827
    HEART = 'HEART', 9829
    SPADE = 'SPADE', 9824

    def __new__(cls, name, unicode_code):
        obj = object.__new__(cls)
        obj._name = name
        obj._symbol = chr(unicode_code)
        return obj

    def __str__(self):
        return self._symbol

    def __repr__(self):
        return self._name

class Value(IntEnum):
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 12
    QUEEN = 13
    KING = 14
    ACE = 11

    def __str__(self):
        if self <= 10: 
            return str(self.value)
        else:
            return self.name[0]

    def __repr__(self):
        if self <= 10:
            return str(self.value)
        else:
            return self.name


class Card:
    def __init__(self, suite : Suite, value : Value):
        self.suite = suite
        self.value = value

    @property
    def suite(self):
        return self._suite

    @property
    def value(self):
        return self._value

    @suite.setter
    def suite(self, suite : Suite):
        if suite not in Suite:
            raise ValueError
        self._suite = suite

    @value.setter
    def value(self, value : Value):
        if value not in Value:
            raise ValueError
        self._value = value

    def __repr__(self):
        return f'<Card {repr(self.value)} of {repr(self.suite)}S>'

    def __str__(self):
        s = str(self.value) + str(self.suite)
        if len(s) < 3:
            s = ' '+s
        return s

class CardList:
    def __init__(self, cards : list):
        self.cards = cards
    def __str__(self):
        return '[' + ', '.join([str(c) for c in self.cards]) + ']'
    def __repr__(self):
        return str(self)

class Deck(CardList):
    def __init__(self):
        super().__init__([Card(s, v) for s in Suite for v in Value])


