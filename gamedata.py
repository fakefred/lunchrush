from player import Player
from map import Map
from pyglet import resource
from utils import center_image

DEBUG = True

resource.path = ['./res']
resource.reindex()


""" MAPS SETUP """
# 6 tracks, each 200px wide
lanes_x = range(460, 1461, 200)
corridor = Map(lane=6, lanes_x=lanes_x, length=1000, npc_density=1/1000.0)
maps = [corridor, corridor]

""" PLAYER SETUP: DONE IN initplayer.py """

""" NPCS SETUP: DONE IN initnpc.py """
