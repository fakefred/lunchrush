class Map():
    def __init__(self, lane=1, lanes_x=(0,), length=10000, npc_density=0.0, npcs=[]):
        self.lane = lane
        self.lanes_x = lanes_x
        self.length = length
        # npc_density: number of npcs / length
        self.npc_density = npc_density
        self.npcs = npcs

    def add_NPC(self, npc):
        self.npcs.append(npc)
