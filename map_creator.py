
#!/usr/bin/python                                                               

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



mz = dm.Maze(10,10)

bt = dm.Bot(1, (0,0), 0, 0)

tm = dm.Team(0,'teamA',0)

un = dm.CTFUniverse(mz, tm, bt)




