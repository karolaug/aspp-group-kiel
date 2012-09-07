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
        #self.current_path = self.bfs_food()

        self.current_strategy = 0
        self.round_index = None
        self.score_history = zeros([2, 300])
        if self.me.team_index == 0:
            self.enemy_index = 1
        else:
            self.enemy_index = 0
        
        self.path = self.path_to_border
        self.tracking_idx = None
        self.strategy_1 = self.defense_player
        self.strategy_2 = self.ofense_player
        self.counter = 0
        self.counter2 = 0


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
#        print 'This is my index ', self.me.team_index


        if self.current_pos == self.initial_pos or self.other_team_bots[0].current_pos == self.other_team_bots[0].initial_pos:
            self.strategy_1, self.strategy_2 = self.strategy_2, self.strategy_1


        if self.me.index == 1 or self.me.index == 2:
            return self.strategy_1()
        else:
            return self.strategy_2()



    def get_move_stopping(self):
        return datamodel.stop

    def get_move_random(self):
        return self.rnd.choice(self.legal_moves.keys())  

    def ofense_player(self):
        """ Breadth first search for food.

        Returns
        -------
        path : a list of tuples (int, int)
            The positions (x, y) in the path from the current position to the
            closest food. The first element is the final destination.

        """
        e_food = self.enemy_food
        try:
            food_path =  self.adjacency.bfs(self.current_pos, self.enemy_food)
        except NoPathException:
            return datamodel.stop
        possible_targets = [enemy for enemy in self.enemy_bots
                            if self.team.in_zone(enemy.current_pos) == False and enemy.noisy == False]
        if possible_targets:
            possible_paths = [(enemy, self.adjacency.a_star(self.current_pos, enemy.current_pos))
                              for enemy in possible_targets]
            closest_enemy, enemy_path = min(possible_paths,
                                            key=lambda enemy_path: len(enemy_path[1]))
            #print len(enemy_path)
            if len(enemy_path) < 3:
                legal_moves = self.legal_moves
                del legal_moves[datamodel.stop]
                del legal_moves[diff_pos(self.current_pos, enemy_path[-1])]
                for move in legal_moves:
                    f_pos = (self.current_pos[0]+move[0], self.current_pos[1]+move[1])
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

    @property
    def path_to_border(self):
        """ Path to the closest border position. """
        try:
            return self.adjacency.bfs(self.current_pos, self.group_consecutives(self.team_border))
            #return self.adjacency.bfs(self.current_pos, self.team_border)
        except NoPathException:
            return None
    
    def group_consecutives(self,border_positions):
        try:
            import operator,itertools
        except:
            return border_positions
        list_consecutives = []
        y_coordinates = [p[1] for p in border_positions]
        x = border_positions[0][0]
        for k, g in itertools.groupby(enumerate(y_coordinates), lambda (i,x):i-x):
            list_consecutives.append([(x,y) for y in map(operator.itemgetter(1), g)])
        
        return sorted(list_consecutives,key=len).pop()
                
    
    @property
    def path_to_target(self):
        """ Path to the target we are currently tracking. """
        try:
            return self.adjacency.a_star(self.current_pos,
                    self.tracking_target.current_pos)
        except NoPathException:
            return None

    @property
    def tracking_target(self):
        """ Bot object we are currently tracking. """
        #self.say("come here! Dont run away you chicken")
        self.say('Niut!')
        return self.current_uni.bots[self.tracking_idx]

    #def get_move_defense(self):
    def defense_player(self):
        
        # if we were killed, for whatever reason, reset the path
        self.path = None
        if self.current_pos == self.initial_pos or self.path is None:
            self.path = self.path_to_border

        # First we need to check, if our tracked enemy is still
        # in our zone
        if self.tracking_idx is not None:
            # if the enemy is no longer in our zone
            if not self.team.in_zone(self.tracking_target.current_pos):
                self.tracking_idx = None
                self.path = self.path_to_border
            # otherwise update the path to the target
            else:
                self.path = self.path_to_target

        # if we are not currently tracking anything
        # (need to check explicity for None, because using 'if 
        # self.tracking_idx' would evaluate to True also when we are tracking
        # the bot with index == 0)
        if self.tracking_idx is None:
            # check the enemy positions
            possible_targets = [enemy for enemy in self.enemy_bots
                    if self.team.in_zone(enemy.current_pos)]
            if possible_targets:
                # get the path to the closest one
                try:
                    possible_paths = [(enemy, self.adjacency.a_star(self.current_pos, enemy.current_pos))
                                      for enemy in possible_targets]
                except NoPathException:
                    possible_paths = []
            else:
                possible_paths = []

            if possible_paths:
                closest_enemy, path = min(possible_paths,
                                          key=lambda enemy_path: len(enemy_path[1]))

                # track that bot by using its index
                self.tracking_idx = closest_enemy.index
                self.path = path
            else:
                # otherwise keep going if we aren't already underway
                if not self.path:
                    self.path = self.path_to_border

        # if something above went wrong, just stand still
        if not self.path:
            return datamodel.stop
        else:
            return diff_pos(self.current_pos, self.path.pop())

