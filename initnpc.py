from npc import NPC
from pyglet import resource, graphics
from map import Map
from gamedata import maps
from random import randint, random
from utils import center_image

def initiate_npcs(maps: Map, batch):
    # initiate series of npcs
    npcs = []
    for thismap in maps:
        for _ in range(round(thismap.npc_density * thismap.length)):
            # NPCs that have been running midway since game started
            npcs.append(NPC(img=center_image(resource.image('player/blackhat.png')),
                            track=thismap, lane=randint(0, 5), y=randint(0, thismap.length),
                            batch=batch, v=60.0, wait=0.0))

            # NPCs that will begin running after a period of time
            npcs.append(NPC(img=center_image(resource.image('player/cueball.png')),
                            track=thismap, lane=randint(0, 5), y=-25,
                            batch=batch, v=60.0, wait=random() * thismap.length / 240))
    return npcs

npc_batch = graphics.Batch()
npcs = initiate_npcs(maps, npc_batch)
