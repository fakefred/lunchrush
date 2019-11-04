from pyglet.sprite import Sprite
from pyglet.resource import image
from map import Map
from initplayer import player


class NPC(Sprite):
    # NPC: non-player characters
    # inherits pyglet.sprite.Sprite
    # includes other students, faculty, random bonuses (aka boni)
    # does not switch lanes
    def __init__(self, track: Map, lane=0, v=0.0, wait=0.0, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.track = track
        self.lane = lane
        # init_v is static
        self.init_v = v
        self.v = v if wait == 0.0 else 0.0
        self.wait = wait

    def update(self, dt):
        if self.wait > 0:
            self.wait -= dt
            if self.wait <= 0:
                # depart
                self.v = self.init_v

        # move on each frame refresh
        self.y += (self.v - player.v) * dt

    @property
    def lane(self):
        return self._lane

    @lane.setter
    def lane(self, lane_num):
        self._lane = lane_num
        self.x = self.track.lanes_x[lane_num]

    def left(self):
        if self.lane > 0:
            self.lane -= 1

    def right(self):
        if self.lane < self.track.lanes - 1:
            self.lane += 1

