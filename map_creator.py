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


def create_map(universe):

    return 1




#create empty map
w = gm.universe.maze.width
h = gm.universe.maze.height
n_values = 4
mp = np.zeros((w,h,n_values))

bot_pos = []
for b in gm.universe.bots:
    print b, b.in_own_zone, b.is_destroyer
    if b.in_own_zone and b.is_destroyer:
        bot_pos.append(b.current_pos)

foo_pos = gm.universe.food_list


for i in xrange(w):
    for j in xrange(h):
        if (i,j) in bot_pos:
            mp[i][j][0]=-1
        else:
            tmp = np.zeros(len(bot_pos))
            for idx,p in enumerate(bot_pos):
                tmp[idx]=np.sqrt(((i-p[0])**2)+((j-p[1])**2))
            try:
                mp[i][j][1]=np.min(tmp)
            except:
                print i,j
        if (i,j) in foo_pos:
            mp[i][j][2]=1
        else:
            tmp = np.zeros(len(foo_pos))
            for idx,p in enumerate(foo_pos):
                tmp[idx]=np.sqrt(((i-p[0])**2)+((j-p[1])**2))
            try:
                mp[i][j][3]=np.min(tmp)
            except:
                print i,j
        
print bot_pos
print mp

