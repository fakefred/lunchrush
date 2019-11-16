import pyglet
from readmaps import read
from utils import dualdigit, format_time, center_image, \
    calc_lanes_x, map_type_hash, calc_selecs_x
from random import random, randint
keys = pyglet.window.key

DEBUG = True

""" ALL THE CLASSES """


class Player(pyglet.sprite.Sprite):
    # Player: the actual player of this game
    # inherits pyglet.sprite.Sprite
    # switches lanes; does not move vertically on the screen
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.y = 80
        # start from #0
        self.map = route[0]
        # absolute_y: distance from map starting line
        self.absolute_y = 0
        # NPCs will move at NPC.v relative to Player.v
        self.init_v = 0.0
        self.v = self.init_v
        # delta_t = time since last step
        self.delta_t = 0.0
        # center self
        self.lane = (route[0].lanes // 2 - 1)
        self.reached_cafeteria = False
        # choices
        self.approaching_EOM = False
        self.show_choices = False
        self.exit_choices = self.map.exits
        self.exit_choice_idx = 0
        self.exit_choices_labels = []
        self.exit_choices_labels_batch = pyglet.graphics.Batch()
        if len(self.exit_choices) > 1:
            # it is necessary to select a designated exit
            self.generate_exit_choices_labels()

        maplabel.text = f'map: {self.map.name}'

        if not self.map.exits[0] == '':
            # unless there's no exit, assume default exit
            route.append(maps[self.map.exits[0]])

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
        if self.lane < self.map.lanes - 1 and not self.reached_cafeteria:
            self.lane += 1

    def update(self, dt):
        if not self.reached_cafeteria:
            self.delta_t += dt
            # decrease self.v over time after each step until player stops
            if self.v > 0:
                self.v = max(0.0, self.init_v - 20 * self.delta_t ** 2)
            # move self on map
            self.absolute_y += self.v * dt
            self.check_if_hit_npc()
            self.check_if_is_approaching_EOM()
            if self.map_finished():
                self.next_map()

    def step(self):
        if not self.reached_cafeteria:
            self.init_v = 36 / (self.delta_t + 0.01)  # prevent div-by-zero
            self.v = self.init_v
            self.delta_t = 0

    def next_map(self):
        global map_idx

        self.approaching_EOM = False
        self.show_choices = False

        if map_idx < len(route) - 1:
            total_lanes_on_prev_map = self.map.lanes
            # literally next map
            map_idx += 1
            self.map = route[map_idx]
            maplabel.text = f'map: {self.map.name}'
            # default selection
            if not self.map.exits[0] == '':
                # assume
                route.append(maps[self.map.exits[0]])
            # reset exit choices
            self.exit_choices = self.map.exits
            self.exit_choice_idx = 0
            if len(self.exit_choices) > 1:
                # it is necessary to select a designated exit
                self.generate_exit_choices_labels()
            # the `soft-reset` procedure
            self.absolute_y = 0
            self.lane = int(
                self.lane / total_lanes_on_prev_map * self.map.lanes)
        else:
            self.reached_cafeteria = True
            # stop running
            self.v = 0
            # remove all npcs in final map
            route[map_idx].npcs = []

    def map_finished(self):
        if self.absolute_y >= self.map.length:
            return True
        return False

    def check_if_is_approaching_EOM(self):
        if self.map.length - self.absolute_y <= 500 and not self.approaching_EOM:
            self.approaching_EOM = True
            if len(self.map.exits) > 1:
                # show choices if applicable
                self.show_choices = True

    def generate_exit_choices_labels(self):
        self.exit_choices_labels = []
        self.exit_choices_labels_batch = pyglet.graphics.Batch()
        x_axis = calc_selecs_x(width, 25, 200, len(self.exit_choices))
        exit_x_assignment_idx = 0
        for exit in self.exit_choices:
            self.exit_choices_labels.append(pyglet.text.Label(
                text=exit, x=x_axis[exit_x_assignment_idx], y=(height - 80),
                width=300, height=100, align='center', color=(0, 0, 0, 255),
                anchor_x='center', font_size=32,
                batch=self.exit_choices_labels_batch))
            exit_x_assignment_idx += 1
        self.exit_choices_labels[0].color = (255, 0, 0, 255)

    def alter_exit(self, idx):
        prev_idx = self.exit_choice_idx
        self.exit_choice_idx = idx
        route.pop()
        route.append(maps[self.map.exits[idx]])
        # emphasize new choice
        self.exit_choices_labels[prev_idx].color = (0, 0, 0, 255)
        self.exit_choices_labels[idx].color = (255, 0, 0, 255)

    def check_if_hit_npc(self):
        for npc in self.map.npcs:
            if self.lane == npc.lane and abs(self.y - npc.y) < 45:
                npc.on_hit()


class NPC(pyglet.sprite.Sprite):
    # NPC: non-player characters
    # inherits pyglet.sprite.Sprite
    # includes other students, faculty, random bonuses (aka boni)
    # does not switch lanes
    def __init__(self, track, lane=0, v=0.0, wait=0.0, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.map = track
        self.initiating = True
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

        if self.initiating:
            self.x = self.dest_x
            self.initiating = False

        if not self.x == self.dest_x:
            # fancy animations
            self.x = round((self.dest_x + self.x) / 2)

    @property
    def lane(self):
        return self._lane

    @lane.setter
    def lane(self, lane_num):
        self._lane = lane_num
        # set destination x
        self.dest_x = self.map.lanes_x[lane_num]

    def left(self):
        if self.lane > 0:
            self.lane -= 1

    def right(self):
        if self.lane < self.map.lanes - 1:
            self.lane += 1

    def on_hit(self):
        # player gets blocked
        player.v = 0

    def switch_lane_when_necessary(self, _):
        switch_threshold = 1
        for npc in self.map.npcs:
            if npc is not self and npc.lane == self.lane:
                if (0 < self.y - npc.y < 100 and self.v < npc.v) or \
                        (-100 < self.y - npc.y < 0 and self.v > npc.v):
                        # going to hit from the (back) or (front)
                    switch_threshold -= 0.005

                if abs(npc.v - self.v) < 50:
                    # *already* hit, additionally reduce thres by .2
                    switch_threshold -= 0.005

        if (0 < self.y - player.y < 100 and self.v < player.v) or \
                (-100 < self.y - player.y < 0 and self.v > player.v):
            switch_threshold -= 0.02

        if abs(player.v - self.v) < 50:
            switch_threshold -= 0.04

        if random() > switch_threshold:
            # peek for transferable lanes
            left_ok = True if self.lane != 0 else False
            right_ok = True if self.lane < self.map.lanes else False
            for npc in self.map.npcs:
                if (0 < self.y - npc.y < 80 and self.v < npc.v) or \
                        (-80 < self.y - npc.y < 0 and self.v > npc.v):
                    # approaching self from either direction
                    if npc.lane == self.lane - 1:
                        left_ok = False
                    elif npc.lane == self.lane + 1:
                        right_ok = False

            if left_ok and right_ok:
                if random() > 0.5:
                    self.left()
                else:
                    self.right()
            elif left_ok:
                self.left()
            elif right_ok:
                self.right()


class Map():
    def __init__(self, name='', type_abbr='co', lanes=1, length=10000, npc_density=0.0, exits=[]):
        self.name = name
        self.type = map_type_hash[type_abbr]
        self.lanes = lanes
        self.lanes_x = calc_lanes_x(width, lane_width, lanes)
        self.length = length
        # npc_density: number of npcs / length
        self.npc_density = npc_density
        self.initiate_npcs()
        self.exits = exits

    def add_NPC(self, npc):
        self.npcs.append(npc)

    def initiate_npcs(self):
        npcs = []
        batch = pyglet.graphics.Batch()
        for _ in range(round(self.npc_density * self.length * self.lanes)):
            # add new NPCs to `batch`
            # NPCs that have been running midway since game started
            npcs.append(NPC(img=center_image(pyglet.resource.image('player/blackhat.png')),
                            track=self, lane=randint(0, self.lanes - 1), y=randint(0, self.length),
                            batch=batch, v=60.0, wait=0.0))

            # NPCs that will be dispatched after a period of time
            npcs.append(NPC(img=center_image(pyglet.resource.image('player/cueball.png')),
                            track=self, lane=randint(0, self.lanes - 1), y=-25,
                            batch=batch, v=60.0, wait=random() * self.length / 60))
        self.npcs = npcs
        self.npc_batch = batch


""" GRAPHICS SETUP """
# (nearly) fullscreen
width, height = 1360, 736
window = pyglet.window.Window(width=width, height=height)
lane_width = 100
# solid white bg
white = pyglet.image.SolidColorImagePattern(
    (255, 255, 255, 255)).create_image(width, height)

pyglet.resource.path = ['./res']
pyglet.resource.reindex()

""" SCORING SETUP """
# displayed and updated over time
time = [12, 0, 0]

time_label = pyglet.text.Label(
    text=format_time(time), x=20, y=(height - 68), color=(0, 0, 0, 255), font_size=48)

vlabel = pyglet.text.Label(
    text='v=0.00', x=20, y=(height - 120), color=(0, 0, 0, 255), font_size=32)

ylabel = pyglet.text.Label(
    text='y=0.00/0', x=20, y=(height - 160), color=(0, 0, 0, 255), font_size=32)

maplabel = pyglet.text.Label(
    text='map: ---', x=20, y=(height - 200), color=(0, 0, 0, 255), font_size=32)

""" MAPS INITIATION """
# 6 maps, each 100px wide
# lanes_x = range(430, 931, 100)
# corridor = Map(lane=6, lanes_x=lanes_x, length=500, npc_density=1/50.0)
# load all maps listed in efzmaps.csv
# TODO: dynamic loading under poor performance
raw_maps = read(width, lane_width)  # read() provided by ./readmaps.py
maps = {}
for map_key in raw_maps:
    map_dict = raw_maps[map_key]
    maps[map_key] = Map(name=map_key, lanes=map_dict['lanes'], length=map_dict['length'],
                        npc_density=map_dict['npc_density'], exits=map_dict['exits'])

route = [maps['n303w']]
map_idx = 0


""" PLAYER INITIATION """
player = Player(img=center_image(
    pyglet.resource.image('player/megan.png')))

""" START GRAPHICS """
@window.event
def on_draw():
    # cover window with white bg
    # equivalent of clearing canvas
    white.blit(0, 0)

    # update time label, unless reached cafeteria
    if not player.reached_cafeteria:
        time_label.text = format_time(time)
    time_label.draw()
    maplabel.draw()

    if player.show_choices:
        player.exit_choices_labels_batch.draw()

    if DEBUG:
        vlabel.text = f'v={player.v: .2f}'
        vlabel.draw()
        ylabel.text = f'y={player.absolute_y: .2f}/{player.map.length}'
        ylabel.draw()

    route[map_idx].npc_batch.draw()
    player.draw()


@window.event
def on_key_press(symbol, mods):
    if symbol == keys.SPACE:
        player.step()
    elif symbol == keys.LEFT:
        player.left()
    elif symbol == keys.RIGHT:
        player.right()
    elif symbol == keys._1:
        player.alter_exit(0)
    elif symbol == keys._2:
        player.alter_exit(1)
    elif symbol == keys._3:
        player.alter_exit(2)


def refresh_NPCs(dt):
    for npc in route[map_idx].npcs:
        npc.update(dt)


def NPC_switch_lane(_):
    for npc in route[map_idx].npcs:
        npc.switch_lane_when_necessary(_)


def clocktick(_):
    # time = [h, m, s]
    time[2] += 1
    # running time > 12 hours not handled
    for i in (2, 1):
        if time[i] == 60:
            time[i] = 0
            time[i - 1] += 1


pyglet.clock.schedule_interval(clocktick, 1)
pyglet.clock.schedule_interval(refresh_NPCs, 0.05)
pyglet.clock.schedule_interval(NPC_switch_lane, 0.5)
pyglet.clock.schedule_interval(player.update, 0.05)
pyglet.app.run()
