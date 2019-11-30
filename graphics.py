#!/usr/bin/python3.8
import pyglet
from readmaps import read

# from readserial import view_value
from utils import (
    dualdigit,
    format_time,
    center_image,
    calc_lanes_x,
    calc_selecs_x,
    calc_lane_separators_x,
)
from random import random, randint

keys = pyglet.window.key

DEBUG = False

""" ALL THE CLASSES """
base_velocity = 120 if DEBUG else 36


class Player(pyglet.sprite.Sprite):
    # Player: the actual player of this game
    # inherits pyglet.sprite.Sprite
    # switches lanes; does not move vertically on the screen
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initiating = True
        self.y = 120
        # start from #0
        self.map = route[0]
        self.minimap = pyglet.image.load(self.map.minimap_image_path)
        next_map_cue.text = "下一关：" + maps[self.map.exits[0]].display_name
        # absolute_y: distance from map starting line
        self.absolute_y = 0
        # NPCs will move at NPC.v relative to Player.v
        self.init_v = 0.0
        self.v = self.init_v
        # delta_t = time since last step
        self.delta_t = 0.0
        # center self
        self.lane = route[0].lanes // 2 - 1
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

        maplabel.text = f"你在: {self.map.display_name}"

        if not self.map.exits[0] == "":
            # unless there's no exit, assume default exit
            route.append(maps[self.map.exits[0]])

    @property
    def lane(self):
        return self._lane

    @lane.setter
    def lane(self, lane_num):
        self._lane = lane_num
        self.dest_x = self.map.lanes_x[lane_num]

    def left(self):
        if self.lane > 0 and not self.reached_cafeteria:
            self.lane -= 1

    def right(self):
        if self.lane < self.map.lanes - 1 and not self.reached_cafeteria:
            self.lane += 1

    def update(self, dt):
        if not self.reached_cafeteria:
            if self.initiating:
                self.x = self.dest_x
                self.initiating = False

            if self.dest_x != self.x:
                self.x = round((self.dest_x + self.x) / 2)

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
            self.init_v = base_velocity / (self.delta_t + 0.01)  # prevent div-by-zero
            self.v = self.init_v
            self.delta_t = 0

    def next_map(self):
        global map_idx

        self.approaching_EOM = False
        self.show_choices = False

        if map_idx < len(route) - 1:  # if there's another map following in `route`
            total_lanes_on_prev_map = self.map.lanes
            map_idx += 1  # literally next map
            self.map = route[map_idx]
            if not (path := self.map.minimap_image_path).endswith(
                "/.png"  # walrus operator; some python 3.8 syntactic sugar
            ):  # no filename
                self.minimap = pyglet.image.load(path)

            maplabel.text = f"你在: {self.map.display_name}"
            finish_line.reset()

            # default selection
            if not self.map.exits[0] == "":
                # assume idx is 0
                # will be popped once player alters exit
                route.append(maps[self.map.exits[0]])

            # reset exit choices
            self.exit_choices = self.map.exits
            self.exit_choice_idx = 0

            try:
                next_map_cue.text = "下一关：" + maps[self.exit_choices[0]].display_name
            except KeyError:
                pass

            if len(self.exit_choices) > 1:
                # it is necessary to select a designated exit
                self.generate_exit_choices_labels()

            # the `soft-reset` procedure
            self.absolute_y = 0
            self.lane = int(self.lane / total_lanes_on_prev_map * self.map.lanes)
        else:  # nothing following; end of route
            if self.map.exits == [""]:
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
        if self.map.length - self.absolute_y <= 1000 and not self.approaching_EOM:
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
            self.exit_choices_labels.append(
                pyglet.text.Label(
                    text=maps[exit].display_name,
                    x=x_axis[exit_x_assignment_idx],
                    y=200,
                    width=300,
                    height=100,
                    align="center",
                    color=(0, 0, 0, 255),
                    anchor_x="center",
                    font_size=28,
                    font_name="Noto Sans CJK SC",
                    batch=self.exit_choices_labels_batch,
                )
            )
            exit_x_assignment_idx += 1
        self.exit_choices_labels[0].color = (248, 101, 57, 255)

    def alter_exit(self, idx):
        if 0 <= idx < len(self.map.exits):
            prev_idx = self.exit_choice_idx
            self.exit_choice_idx = idx
            route.pop()
            route.append(maps[self.map.exits[idx]])
            # emphasize new choice
            self.exit_choices_labels[prev_idx].color = (0, 0, 0, 255)
            self.exit_choices_labels[idx].color = (248, 101, 57, 255)
            next_map_cue.text = "下一关：" + maps[self.map.exits[idx]].display_name

    def check_if_hit_npc(self):
        for npc in self.map.npcs:
            if self.lane == npc.lane and 0 < npc.y - self.y < 45:
                npc.on_hit(self)


class NPC(pyglet.sprite.Sprite):
    # NPC: non-player characters
    # inherits pyglet.sprite.Sprite
    # includes other students, faculty, random bonuses (aka boni)
    # does not switch lanes
    def __init__(self, track, lane=0, v=0.0, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.map = track
        self.initiating = True
        self.lane = lane
        # init_v is static
        self.init_v = v
        self.v = v
        self.acc = 5

    def update(self, dt):
        # velocity control
        if self.v - self.init_v < -10:
            self.v += self.acc
        elif self.v - self.init_v > 10:
            self.v -= self.acc

        # move on each frame refresh
        self.y += (self.v - player.v) * dt

        if self.initiating:
            self.x = self.dest_x
            self.initiating = False

        if self.x != self.dest_x:
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

    def on_hit(self, character):
        # player or another NPC gets blocked
        character.v = 0

    def react(self, _):
        switch_threshold = 1
        for npc in self.map.npcs:
            if npc.lane == self.lane and npc is not self:
                if (0 < self.y - npc.y < 100 and self.v < npc.v) or (
                    -100 < self.y - npc.y < 0 and self.v > npc.v
                ):
                    # going to hit from the (back) or (front)
                    switch_threshold -= 0.005

                if abs(npc.v - self.v) < 50:
                    # *already* hit
                    npc.on_hit(self)
                    # additionally reduce thres
                    switch_threshold -= 0.005

        if (
            self.lane == player.lane
            and 0 < self.y - player.y < 100
            and self.v < player.v
        ):
            # player approaching from back
            switch_threshold -= 0.02
            self.v += 10
        elif (
            self.lane == player.lane
            and -100 < self.y - player.y < 0
            and self.v > player.v
        ):
            # ... from front
            switch_threshold -= 0.02
            self.v -= 10

        if abs(player.v - self.v) < 50:
            switch_threshold -= 0.04

        if random() > switch_threshold:
            # peek for transferable lanes
            left_ok = True if self.lane != 0 else False
            right_ok = True if self.lane < self.map.lanes else False
            for npc in self.map.npcs:
                if (0 < self.y - npc.y < 80 and self.v < npc.v) or (
                    -80 < self.y - npc.y < 0 and self.v > npc.v
                ):
                    # approaching self from either direction
                    if left_ok and npc.lane == self.lane - 1:
                        left_ok = False
                    elif right_ok and npc.lane == self.lane + 1:
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


class Map:
    def __init__(
        self,
        name="",
        display_name="",
        lanes=1,
        length=10000,
        npc_density=0.0,
        exits=[],
        minimap_image_path="",
    ):
        self.name = name
        self.display_name = display_name
        self.lanes = lanes
        self.lanes_x = calc_lanes_x(width, lane_width, lanes)
        self.length = length
        # npc_density: number of npcs / length
        self.npc_density = npc_density
        self.initiate_npcs()
        self.exits = exits
        self.minimap_image_path = minimap_image_path

    def initiate_npcs(self):
        npcs = []
        batch = pyglet.graphics.Batch()
        for _ in range(round(self.npc_density * self.length * self.lanes)):
            # add new NPCs to `batch`
            # NPCs that have been running midway since game started
            npcs.append(
                NPC(
                    img=center_image(pyglet.resource.image("player/blackhat.png")),
                    track=self,
                    lane=randint(0, self.lanes - 1),
                    y=randint(-self.length / 4, self.length),
                    batch=batch,
                    v=60.0,
                )
            )
        self.npcs = npcs
        self.npc_batch = batch


class FinishLine(pyglet.sprite.Sprite):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.y = height + 10
        self.x = width / 2
        self.moving = False

    def update(self, dt):
        if self.moving:
            dy = player.v * dt
            self.y -= dy
            next_map_cue.y -= dy
            if self.y < player.y:
                self.reset()

        else:
            if route[map_idx].length - player.absolute_y < height:
                self.moving = True

    def reset(self):
        self.moving = False
        self.y = height + 10
        next_map_cue.y = height + 20


""" GRAPHICS SETUP """
# (nearly) fullscreen
width, height = 1920, 1040
window = pyglet.window.Window(width=width, height=height, caption="跑饭 - Lunchrush")
window.set_icon(pyglet.image.load('./res/icon.png'))
lane_width = 100
# solid white bg
white = pyglet.image.SolidColorImagePattern((255, 255, 255, 255)).create_image(
    width, height
)

pyglet.resource.path = ["./res"]
pyglet.resource.reindex()

lane_sep_img = pyglet.image.load("./res/track-separator.png")


""" SCORING SETUP """
# displayed and updated over time
time = [12, 0, 0]

time_label = pyglet.text.Label(
    text=format_time(time), x=20, y=(height - 68), color=(0, 0, 0, 255), font_size=48
)

vlabel = pyglet.text.Label(
    text="v=0.00", x=20, y=(height - 120), color=(0, 0, 0, 255), font_size=32
)

ylabel = pyglet.text.Label(
    text="y=0.00/0", x=20, y=(height - 160), color=(0, 0, 0, 255), font_size=32
)

maplabel = pyglet.text.Label(
    text="你在： ---",
    x=20,
    y=(height - (220 if DEBUG else 120)),
    color=(0, 0, 0, 255),
    font_name="Noto Sans CJK SC",
    font_size=32,
)

""" MAPS INITIATION """
# load all maps listed in efzmaps.csv
# TODO: dynamic loading under poor performance
raw_maps = read(width, lane_width)  # read() provided by ./readmaps.py
maps = {}
for map_key in raw_maps:
    map_dict = raw_maps[map_key]
    maps[map_key] = Map(
        name=map_key,
        display_name=map_dict["display_name"],
        lanes=map_dict["lanes"],
        length=map_dict["length"],
        npc_density=map_dict["npc_density"],
        exits=map_dict["exits"],
        minimap_image_path=map_dict["minimap_image"],
    )

route = [maps["s104w"]]
map_idx = 0
next_map_cue = pyglet.text.Label(
    x=width / 2,
    y=(height + 20),
    color=(248, 101, 57, 255),
    font_name="Noto Sans CJK SC",
    font_size=32,
    anchor_x="center",
)

finish_line = FinishLine(img=center_image(pyglet.resource.image("finish_line.png")))

""" PLAYER INITIATION """
player = Player(img=center_image(pyglet.resource.image("player/megan.png")))


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

    if DEBUG:
        vlabel.text = f"v={player.v: .2f}"
        vlabel.draw()
        ylabel.text = f"y={player.absolute_y: .2f}/{player.map.length}"
        ylabel.draw()

    for x in calc_lane_separators_x(width, lane_width, player.map.lanes):
        lane_sep_img.blit(x, 0)

    finish_line.draw()
    next_map_cue.draw()
    route[map_idx].npc_batch.draw()

    if player.show_choices:
        player.exit_choices_labels_batch.draw()

    player.minimap.blit(100, 500 if DEBUG else 600)
    player.draw()


""" EVENTS """


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


""" SERIAL """
"""
prev_pin_states = {
    'pedal_l': 0,
    'pedal_r': 0
    # 'panel_l': 0,
    # 'panel_r': 0,
    # 'panel_a': 0,
    # 'panel_b': 0
}
foot_down = 0  # the foot stamped down
def react_to_serial(_):
    # access values read and stored in `readserial.py`
    global prev_pin_states
    global foot_down
    res_pin_states = view_value()
    # pedal_[lr]: type int. interpreted as bools.
    pedal_l = res_pin_states['pedal_l']
    pedal_r = res_pin_states['pedal_r']
    # player.step() criteria:
    # L0R1 -> L1R0 or L1R0 -> L0R1
    res_foot_down = foot_down  # default
    if pedal_l and (not pedal_r):
        res_foot_down = 0
    elif (not pedal_l) and pedal_r:
        res_foot_down = 1
    if not res_foot_down == foot_down:
        player.step()
        foot_down = res_foot_down
    prev_pin_states = res_pin_states
"""


def refresh_NPCs(dt):
    for npc in route[map_idx].npcs:
        npc.update(dt)


def NPC_react(_):
    for npc in route[map_idx].npcs:
        npc.react(_)


def clocktick(_):
    # time = [h, m, s]
    time[2] += 1
    # running time > 12 hours not handled
    for i in (2, 1):
        if time[i] == 60:
            time[i] = 0
            time[i - 1] += 1


pyglet.clock.schedule_interval(clocktick, 1)
# pyglet.clock.schedule_interval(react_to_serial, 0.02)
pyglet.clock.schedule_interval(refresh_NPCs, 0.05)
pyglet.clock.schedule_interval(NPC_react, 0.5)
pyglet.clock.schedule_interval(player.update, 0.05)
pyglet.clock.schedule_interval(finish_line.update, 0.05)
pyglet.app.run()
