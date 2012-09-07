#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pelita.player import *
import random
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
