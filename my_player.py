#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pelita.player import *
import random
#from pelita.datamodel import north, south, west, east, stop
from numpy import mod, array, zeros
import time
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


class IdentityCrisis(AbstractPlayer):
    """ A Player which makes a decision dependent on the round index
    in a dict or list. (Or anything which responds to moves[idx].)

    Parameters
    ----------
    moves : list or dict of moves
        the moves to make, a move is determined by moves[round]
    """
    # Set the team name to Group0

    def set_initial(self):
        self.current_strategy = 0
        self.round_index = None
        self.score_history = zeros([2, 300])
        if self.me.team_index == 0:
            self.enemy_index = 1
        else:
            self.enemy_index = 0
        

    # round_index is part of AbstractPlayer
    # _current_game_state
    # universe_states
    # .say('Now, prepare to die!')
    # .say('Another one bites the dust!')
    #. 

    def define_strategy(self):

        # Calculate the function that tells you which strategy
        #if self.round_index % 20 == 0:
        #    self.current_strategy = mod(self.current_strategy+1, 2)
        #    self.say('You are done,  BITCH!')
        #return     

        if self.round_index < 20:
            # Aggresive to start with
            self.current_strategy = 0
            return

        # If the game is over round 20, start taking decisions
        #self.score_history[self.enemy_index, self.round_index]
        #self.score_history[self.me.team_index, self.round_index]

        if self.score_history[self.enemy_index, self.round_index] > self.score_history[self.me.team_index, self.round_index]:
            self.current_strategy = 0
            #print 'Im hunting you, BITCH!'
        else:
            self.current_strategy = 1
            #print 'Nothing to do here'


    
    def read_score(self):
        self.score_history[0, self.round_index] = self.current_uni.teams[0].score
        self.score_history[1, self.round_index] = self.current_uni.teams[1].score
        #print self.score_history

    # For the first 70 moves, go aggresive (but not so much)
    # If the move is above 70, check the score
    # Track the score changes. Calculate the derivative and decide on that.

    def get_move(self):
        #print 'This is my index ', self.me.team_index
        
        if self.round_index is None:
            self.round_index = 0
        else:
            self.round_index += 1

        self.read_score()

        self.define_strategy()

        if self.current_strategy == 0:
            return self.get_move_random()
        elif self.current_strategy == 1:
            return self.get_move_stopping()
        elif self.current_strategy == 2:
            pass
        elif self.current_strategy == 3:
            pass
        elif self.current_strategy == 4:
            pass

    def get_move_stopping(self):
        return datamodel.stop

    def get_move_random(self):
        return self.rnd.choice(self.legal_moves.keys())  


class BSFPlayer(AbstractPlayer):
    """ This player uses breadth first search to always go to the closest food.

    This player uses an adjacency list [1] to store the topology of the
    maze. It will then do a breadth first search [2] to search for the
    closest food. When found, it will follow the determined path until it
    reaches the food. This continues until all food has been eaten or the
    enemy wins.

    The adjacency lits representation (AdjacencyList) and breadth first search
    (AdjacencyList.bfs) are imported from pelita.graph.

    * [1] http://en.wikipedia.org/wiki/Adjacency_list
    * [2] http://en.wikipedia.org/wiki/Breadth-first_search

    """
    def set_initial(self):
        # Before the game starts we initialise our adjacency list.
        self.adjacency = AdjacencyList(self.current_uni)
        self.current_path = self.bfs_food()

    def bfs_food(self):
        """ Breadth first search for food.

        Returns
        -------
        path : a list of tuples (int, int)
            The positions (x, y) in the path from the current position to the
            closest food. The first element is the final destination.

        """
        e_food = self.enemy_food
        food_path =  self.adjacency.bfs(self.current_pos, self.enemy_food)

        possible_targets = [enemy for enemy in self.enemy_bots
                            if self.team.in_zone(enemy.current_pos) == False and enemy.noisy == False]
        if possible_targets:
            possible_paths = [(enemy, self.adjacency.a_star(self.current_pos, enemy.current_pos))
                              for enemy in possible_targets]
            closest_enemy, enemy_path = min(possible_paths,
                                            key=lambda enemy_path: len(enemy_path[1]))
            #print len(enemy_path)
            if len(enemy_path) < 4:
                legal_moves = self.legal_moves
                del legal_moves[datamodel.stop]
                del legal_moves[diff_pos(self.current_pos, enemy_path.pop())]
                for move in legal_moves:
                    f_pos = (self.current_pos[0]+move[0], self.current_pos[1]+move[1])
                    if f_pos == diff_pos(self.current_pos, food_path.pop()):
                        return f_pos
                    print e_food
                    e_food.pop()
                    food_path = self.adjacency.bfs(self.current_pos, self.enemy_food)
                    
                return random.choice(legal_moves.keys())

        return diff_pos(self.current_pos, food_path.pop())

    def get_move(self):
        self.current_path = self.bfs_food()
        try:
            return self.current_path
        except ValueError:
            # If there was a timeout, and we are no longer where we think we
            # were, calculate a new path.
            return self.get_move()
