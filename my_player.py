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
        self.sayings = ["You're going down ... DOWNTOWN!",
                        "Is that all you got?",
                        "My grandma can do better than that!",
                        "You should consider changing jobs",
                        "Man, those pellets are tasty!",
                        "Start praying ...",
                        "Come, I'll show you how to do this"]
        self.position_tracker = []

        self.adjacency = AdjacencyList(self.current_uni)
        self.current_path = self.bfs_food()

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
        
        # First 10 rounds are random, avoid having same starting point for the two agents
        if self.round_index < 10 and self.me.index == 0:
            self.current_strategy = 0
            return 

        # Play the first N rounds aggresively
        if self.round_index < 20:
            self.current_strategy = 1
            return

        # If the game is over round N, start taking decisions
        diff_score_evolution = self.score_history[self.me.team_index, :] - self.score_history[self.enemy_index, :]
        self.enemy_food

        # Compare and decide!
        # Our score is lower
        if diff_score_evolution[self.round_index] < 0:
            self.current_strategy = 1
            return
            #print 'Im hunting you, BITCH!'

        if diff_score_evolution[self.round_index] > 0:
            self.current_strategy = 0
            return
            #print 'Nothing to do here'


    
    def read_score(self):
        self.score_history[0, self.round_index] = self.current_uni.teams[0].score
        self.score_history[1, self.round_index] = self.current_uni.teams[1].score
        #print self.score_history


    def get_move(self):
        #print 'This is my index ', self.me.team_index

        # Track the position
        # If distance between position 0 and position 5 (where 5 is current) is less than 2: pick different strategy
        self.position_tracker.append(self.me.current_pos)
        if len(self.position_tracker) > 8:
            self.position_tracker.pop(0)
        #print self.me.index, self.position_tracker

        
        if self.round_index is None:
            self.round_index = 0
        else:
            self.round_index += 1

        self.read_score()

        old_strategy = self.current_strategy
        self.define_strategy()
        if self.current_strategy != old_strategy:
            print 'The strategy has changed'
            #self.say(self.sayings[self.round_index % 7])
        else:
            # Distance between last move and last - 5 moves
            tracker_dist = datamodel.manhattan_dist(self.position_tracker[0], self.position_tracker[-1])
            if tracker_dist < 2:
                # Change strategy randomly
                self.current_strategy = random.randint(0, 2)# random number between 0 and number of strategies
                print 'Changed randomly to strategy ', self.current_strategy

        if self.current_strategy == 0:
            return self.get_move_random()
        if self.current_strategy == 1:
            return self.bfs_food()
        elif self.current_strategy == 2:
            return self.get_move_stopping()
        elif self.current_strategy == 3:
            pass
        elif self.current_strategy == 4:
            pass
        elif self.current_strategy == 5:
            pass


    def get_move_stopping(self):
        return datamodel.stop

    def get_move_random(self):
        return self.rnd.choice(self.legal_moves.keys())  

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
                del legal_moves[diff_pos(self.current_pos, enemy_path[-1])]
                for move in legal_moves:
                    f_pos = (self.current_pos[0]+move[0], self.current_pos[1]+move[1])
                    print self.current_pos, enemy_path
                    if f_pos != food_path[-1]:
                        e_food.pop()
                        try:
                            food_path = self.adjacency.bfs(self.current_pos, e_food)
                        except NoPathException:
                            break
                    else: 
                        return diff_pos(self.current_pos, food_path[-1])
                return random.choice(legal_moves.keys())

        return diff_pos(self.current_pos, food_path.pop())

