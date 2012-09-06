import numpy as np
import pelita 
from pelita import datamodel as dm

from pelita.game_master import GameMaster
from pelita.player import StoppingPlayer, RandomPlayer, NQRandomPlayer, SimpleTeam
from pelita.viewer import AsciiViewer




layout = (
""" ##################                                                  
    #0#.  .  # .     #                                                  
    #2#####    #####1#                                                  
    #     . #  .  .#3#                                                  
    ################## """)
gm = GameMaster(layout, 4, 200)
gm.register_team(SimpleTeam(StoppingPlayer(), NQRandomPlayer()))
gm.register_team(SimpleTeam(NQRandomPlayer(), NQRandomPlayer()))



w = gm.universe.maze.width
h = gm.universe.maze.height

mp = np.zeros((w,h))

