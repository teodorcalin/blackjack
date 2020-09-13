#!/usr/bin/env python3
# coding=utf-8

from cards import Card, Suite, Value, Deck, CardList
from enum import Enum, Flag, auto
from random import shuffle, sample, choice

# Pip values of cards in Blackjack
pip = { v : 11 if v == Value.ACE else ( v.value if v < 10 else 10)
        for v in Value
      }

# BLACKJACK = ACE + Face Card or TEN (value 21)

# BUST = value over 21 (at least 3 cards)
# SOFT = hand with ACE valued at 11
# PAIR = hand with two cards of same pip
class Eval(Flag):
    ''' Evaluation flags for a player's hand'''
    HAS_ACE = auto()
    HAS_10 = auto()
    BUST = auto()
    SOFT = auto()
    PAIR = auto()


class PlayerHand(CardList):
    ''' Player hand in Blackjack'''
    def __init__(self):
        super().__init__([])
        self.pips = []
        self.value = 0
        self.flags = Eval(0)

    def update(self, c: Card):
        self.cards.append(c)
        if len(self.cards) >= 2:
            self.evaluate()

    def split(self):
        return self.cards.pop()

    def evaluate(self):
        self.pips = [pip[c.value] for c in self.cards]
        self.value = sum(self.pips)
        self.flags = Eval(0)

        if len(self.pips) == 2 and self.pips[0] == self.pips[1]:
            self.flags |= Eval.PAIR

        if 11 in self.pips:
            self.flags |= Eval.HAS_ACE
            if self.minValue() < 21:
                self.flags |= Eval.SOFT

        if self.bestValue() > 21:
            self.flags |= Eval.BUST

        if 10 in self.pips:
            self.flags |= Eval.HAS_10

    def isBlackjack(self):
        return bool(len(self.cards) == 2 and
            self.flags & Eval.HAS_10 and self.flags & Eval.HAS_ACE)

    def isBust(self):
        return bool(self.flags & Eval.BUST)

    def isSoft(self):
        return bool(self.flags & Eval.SOFT)

    def __str__(self):
        ''' String representation'''
        valueStr = f' Value={self.bestValue():2}'
        flagStr = ' '*12
        if self.isBlackjack():
            flagStr = ' (BLACKJACK)'
        elif self.isBust():
            flagStr = ' (BUST     )'
        elif self.isSoft():
            flagStr = ' (SOFT     )'
        return super().__str__() + valueStr + flagStr

    def allValues(self):
        ''' Iterate on the possible values of a hand containing aces '''
        currentValue = self.value
        yield currentValue
        if not self.flags & Eval.HAS_ACE:
            return
        for p in self.pips:
            if p != 11:
                continue
            currentValue -= 10
            yield currentValue

    def minValue(self):
        ''' Minimum value: when all aces are worth 1'''
        return min(self.allValues())

    def bestValue(self):
        ''' Best value: the one closest to but not larger than 21'''
        return max((v for v in self.allValues() if v <= 21), default=self.value)


class DealerHand(PlayerHand):
    ''' Dealer's hand has 1 visible and 1 hidden card'''
    def __init__(self):
        super().__init__()
        self.hiddenIndex = 1

    def __str__(self):
        cardStrs = ['(hidden)' if i==self.hiddenIndex else f'{c}'
                    for i,c in enumerate(self.cards)
                    ]
        valueStr = 'Value='+('(hidden)'
            if self.hiddenIndex==1 else f'{self.bestValue()}')
        return '[' + ', '.join(cardStrs) + '] ' + valueStr

class GameDeck(CardList):
    ''' Game deck that can contain one or more 52-card decks'''
    def __init__(self, nDecks : int):
        d = Deck()
        self.nDecks = nDecks
        self.cards = d.cards * nDecks
        shuffle(self.cards)

    def dealCard(self):
        return self.cards.pop()

# Hit = Take another card
# Stand = Take no more cards
# Double down = Increase initial bet
# Split = Split hand into two hands, to play independently
# Surrender = Surrender hand, losing only half of bet
class Choice(Enum):
    ''' A player's choices at Backjack'''
    HIT = auto()
    STAND = auto()
    DOUBLEDOWN = auto()
    SPLIT = auto()
    SURRENDER = auto()
    INVALID = auto()

    @classmethod
    def listValid(cls):
        valid = list(cls)
        valid.remove(cls.INVALID)
        return valid

class Player:
    ''' A player at the Blackjack table'''
    def __init__(self, name, bet = 0):
        self.name = name
        self.bet = bet
        self.hand = PlayerHand()
        self.choice = None

    def __str__(self):
        choiceStr = 'Choice='+('?' if not self.choice else f'{self.choice.name}')
        handStr = f'Hand={self.hand} '
        betStr = f'Bet={self.bet:<5} '
        return f'{self.name:25}: ' + handStr + betStr + choiceStr

    def isDone(self):
        return self.choice in (Choice.DOUBLEDOWN, Choice.STAND, Choice.SURRENDER)

    def isBust(self):
        return self.hand.isBust()

    def isBlackjack(self):
        return self.hand.isBlackjack()

    def isSurrendered(self):
        return self.choice == Choice.SURRENDER

    def updateHand(self, c:Card):
        '''Update hand with a new card'''
        self.hand.update(c)
        if self.isBust() or self.isBlackjack():
            self.choice = Choice.STAND

    def split(self):
        '''Split the hand of this player in two.
           Reset this player. Return new player.'''
        p2 = Player(self.name+".split2", self.bet)
        self.name +=".split1"
        self.choice = None
        p2.updateHand(self.hand.split())
        return p2


class Dealer(Player):
    ''' The dealer at Blackjack'''
    def __init__(self):
        super().__init__('Dealer')
        self.hand = DealerHand()
        self.hidden = True

    def updateHand(self, c:Card, hidden = False):
        self.hand.update(c)
        if self.hand.bestValue() >= 17:
            self.choice = Choice.STAND
        else:
            self.choice = Choice.HIT

    def isDone(self):
        return self.choice == Choice.STAND

    def reveal(self):
        self.hidden = False
        self.hand.hiddenIndex = -1

    def __str__(self):
        return f'{self.name:25}: Hand={self.hand}'


class BlackjackGame:
    ''' A one-round game of Blackjack'''
    def __init__(self, betRange, nDecks = 1, nPlayers = 4):
        self.deck = GameDeck(nDecks)
        self.players = [Player('Player'+chr(65+i)) for i in range(nPlayers)]
        self.dealer = Dealer()
        self.casinoBetRange = betRange

    def print(self):
        ''' Display the game : all known hands, bets and choices'''
        print('-'*20)
        for p in self.players:
            print(p)
        print(self.dealer)
        print('-'*20)

    def takeNewBet(self, p : Player, betRange : range = None):
        ''' Take a valid bet from the given player'''
        if not betRange:
            betRange = self.casinoBetRange
        bet = betRange.stop
        while not bet in betRange:
            try:
                bet = int(input(f'Place bet between {betRange.start} '
                    f'and {betRange.stop-1} for {p.name} : '))
            except Exception as e:
                print(f'Not a valid bet: {e}')
        p.bet += bet

    @staticmethod
    def resolveChoice(p: Player):
        ''' Take the decision of the given player'''
        if p.isBlackjack():
            return Choice.STAND

        validChoices = Choice.listValid()

        # Split allowed for pairs
        if not p.hand.flags & Eval.PAIR:
            validChoices.remove(Choice.SPLIT)

        # Double down and surrender allowed only as first decision
        if len(p.hand.cards) > 2:
            validChoices.remove(Choice.DOUBLEDOWN)
            validChoices.remove(Choice.SURRENDER)

        choiceValue = Choice.INVALID.value
        while choiceValue not in (c.value for c in validChoices):
            try:
                choiceValue = int(input(f'{p.name} choice {validChoices}: '))
            except Exception as e:
                print(f'Not a valid choice {choiceValue} {e}')
        return Choice(choiceValue)

    def resolveHand(self, p : Player):
        ''' Resolve a player's hand - take their decision repeatedly'''
        while not p.isDone():
            p.choice = self.resolveChoice(p)
            if p.choice in (Choice.HIT, Choice.DOUBLEDOWN):
                p.updateHand(self.deck.dealCard())
                print(p)
            if p.choice == Choice.DOUBLEDOWN:
                p.bet *= 2
                print(p)
            if p.choice == Choice.SPLIT:
                p2 = p.split()
                p.updateHand(self.deck.dealCard())
                p2.updateHand(self.deck.dealCard())
                self.players.insert(self.players.index(p)+1, p2)
                self.print()

    def resolveBets(self):
        ''' Resolve bets for all players at the end of a round'''
        dealerBust = self.dealer.isBust()
        if dealerBust:
            print('The house busted !')
        dealerBlackjack = self.dealer.isBlackjack()
        dealerHandValue = self.dealer.hand.bestValue()

        wins = dict()
        print('Wins:')
        for p in self.players:
            if p.isBust():
                wins[p] = -p.bet
                outcome = 'lost'
            elif p.isBlackjack() > dealerBlackjack:
                wins[p] = int(1.5 * p.bet)
                outcome = 'blackjack'
            elif p.isSurrendered():
                wins[p] = -int(0.5 * p.bet)
                outcome = 'surrendered'
            elif dealerBust or p.hand.bestValue() > dealerHandValue:
                wins[p] = p.bet
                outcome = 'won'
            elif p.hand.bestValue() < dealerHandValue or p.isBlackjack() < dealerBlackjack:
                wins[p] = -p.bet
                outcome = 'lost'
            else:
                wins[p] = 0
                outcome = 'push'
            print(f'{p.name:16} : {outcome:>12} => {wins[p]:+d}')
        houseWin = -sum(w for (p, w) in wins.items())
        print(f'House            :                 {houseWin:+d}')


    def playRound(self):
        ''' Play one round'''
        # Take initial bets
        for p in self.players:
            self.takeNewBet(p)

        # Deal initial hands
        for p in self.players:
            p.updateHand(self.deck.dealCard())
        self.dealer.updateHand(self.deck.dealCard())
        for p in self.players:
            p.updateHand(self.deck.dealCard())
        self.dealer.updateHand(self.deck.dealCard(), True)
        self.print()

        # Resolve hands for all plauers
        for p in self.players:
            while not p.isDone():
                self.resolveHand(p)
                self.print()

        # Complete the dealer's hand
        self.dealer.reveal()
        while not self.dealer.isDone():
            self.dealer.updateHand(self.deck.dealCard())
        self.print()

        # Resolve players' bets
        self.resolveBets()


class Casino:
    ''' Casino that offers to play Blackjack'''
    def __init__(self):
        self.min_bet = 5
        self.max_bet = 500

    def newGame(self, num_decks, num_players):
        return BlackjackGame(
            range(self.min_bet, self.max_bet+1),
            num_decks,
            num_players
        )
