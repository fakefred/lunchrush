from pyglet.sprite import Sprite
from map import Map


class Player(Sprite):
    # Player: the actual player of this game
    # inherits pyglet.sprite.Sprite
    # switches lanes; does not move vertically on the screen
    def __init__(self, maps: list or tuple, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.y = 80
        self.maps = maps
        # start from #0
        self.map_no = 0
        self.map = maps[0]
        # absolute_y: distance from map starting line
        self.absolute_y = 0
        # NPCs will move at NPC.v relative to Player.v
        self.init_v = 0.0
        self.v = self.init_v
        # delta_t = time since last step
        self.delta_t = 0.0
        self.lane = (maps[0].lane // 2 - 1)
        self.reached_cafeteria = False

    @property
    def lane(self):
        return self._lane

    @lane.setter
    def lane(self, lane_num):
        self._lane = lane_num
        self.x = self.map.lanes_x[lane_num]

    def left(self):
        if self.lane > 0 and not self.reached_cafeteria:
            self.lane -= 1

    def right(self):
        if self.lane < self.map.lane - 1 and not self.reached_cafeteria:
            self.lane += 1

    def update(self, dt):
        if not self.reached_cafeteria:
            self.delta_t += dt
            # decrease self.v over time after each step until player stops
            if self.v > 0:
                self.v = max(0, self.init_v - 20 * self.delta_t ** 2)
            # print(self.v)
            # move self on map
            self.absolute_y += self.v * dt
            if self.track_finished():
                self.next_map()

    def step(self):
        if not self.reached_cafeteria:
            self.init_v = 36 / (self.delta_t + 0.01)  # prevent div-by-zero
            self.v = self.init_v
            self.delta_t = 0

    def next_map(self):
        if self.map_no < len(self.maps) - 1:
            total_lanes_on_prev_map = self.map.lane
            self.map_no += 1
            self.map = self.maps[self.map_no]
            self.absolute_y = 0
            self.lane = round(
                self.lane / total_lanes_on_prev_map * self.map.lane)
        else:
            self.reached_cafeteria = True
            self.v = 0

    def track_finished(self):
        if self.absolute_y >= self.map.length:
            return True
        return False
