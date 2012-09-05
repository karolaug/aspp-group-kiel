#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pelita.player import AbstractPlayer
#from pelita.datamodel import north, south, west, east, stop


# use relative imports for things inside your module
from .utils import decision

class MyPlayer0(AbstractPlayer):
    """ Basically a clone of the StoppingPlayer. """
    def get_move(self):
        move = decision(self.legal_moves)
        return move


class MyPlayer1(AbstractPlayer):
    """ Second Player. """
    def get_move(self):
        move = decision(self.legal_moves)
        return move
