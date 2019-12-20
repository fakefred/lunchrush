#!/usr/bin/python3.8
import pyglet
from readmaps import *
from readbonuses import *
from readserial import view_value, read_thread
from utils import *
from math import sqrt
from random import random, randint, choice
from os import listdir

keys = pyglet.window.key

avatars = [file for file in listdir("./res/player/") if file.endswith(".png")]

CHOICE_BUTTONS_Y_AXES = (200, 150, 100)
DEBUG = False

init_selections_left = 3
player_bulldozer_mode = False

BONUS_DATA = read_bonuses()

""" ALL THE CLASSES """
base_velocity = 120 if DEBUG else 72


class Player(pyglet.sprite.Sprite):
    # Player: the actual player of this game
    # inherits pyglet.sprite.Sprite
    # switches lanes; does not move vertically on the screen
    people_killed = 0
    is_player = True
    initiating = True
    allowed_to_run = False
    # absolute_y: distance from map starting line
    absolute_y = 0
    # NPCs will move at NPC.v relative to Player.v
    init_v = 0.0
    v = init_v
    # delta_t = time since last step
    delta_t = 0.0
    reached_cafeteria = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.y = 120
        global player_bulldozer_mode
        player_bulldozer_mode = False

    def load_map(self):
        # start from #0
        self.map = route[0]
        self.minimap = pyglet.image.load(self.map.minimap_image_path)
        next_map_cue.text = "下一关：" + maps[self.map.exits[0]].display_name
        # center self
        lane_num = route[0].lanes // 2
        self._lane = lane_num
        self.dest_x = self.map.lanes_x[lane_num]
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

        map_label.text = f"你在: {self.map.display_name}"

        if not self.map.exits[0] == "":
            # unless there's no exit, assume default exit
            route.append(maps[self.map.exits[0]])

    @property
    def lane(self):
        return self._lane

    @lane.setter
    def lane(self, lane_num):
        if self.allowed_to_run:
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
            if hasattr(self, "dest_x"):
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
            self.check_if_hit_npc_or_bonus()
            self.check_if_is_approaching_EOM()
            if self.map_finished():
                self.next_map()

    def step(self):
        if not self.reached_cafeteria and self.allowed_to_run:
            self.init_v = base_velocity / (self.delta_t + 0.1)  # prevent div-by-zero
            self.v = self.init_v
            self.delta_t = 0

    def next_map(self):
        global map_idx, player_bulldozer_mode

        self.approaching_EOM = False
        self.show_choices = False
        player_bulldozer_mode = False

        if map_idx < len(route) - 1:  # if there's another map following in `route`
            total_lanes_on_prev_map = self.map.lanes
            map_idx += 1  # literally next map
            self.map = route[map_idx]
            if not (path := self.map.minimap_image_path).endswith(
                "/.png"  # walrus operator; some python 3.8 syntactic sugar
            ):  # no filename
                self.minimap = pyglet.image.load(path)

            map_label.text = f"你在: {self.map.display_name}"
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
                # remove all stuff on final map
                route[map_idx].npcs = []
                route[map_idx].bonuses = []
                # fill in stats
                victory_label.text = (
                    f"你用了 {time_spent(time)}到达{self.map.display_name}，跑饭成功！"
                )
                if self.people_killed:
                    victory_label.text += f"\n在推土机模式下共碾压了 {self.people_killed} 个人"

                victory_label.visible = True
                # start showing & spinning victory bg image
                victory_bg.visible = True
                pyglet.clock.schedule_interval(victory_fx, 0.05)
                for label in (map_label, time_label, y_label, v_label):
                    label.visible = False

                pyglet.clock.unschedule(react_to_serial)
                pyglet.clock.unschedule(refresh_NPCs)
                pyglet.clock.unschedule(refresh_bonuses)
                pyglet.clock.unschedule(NPC_react)
                pyglet.clock.unschedule(player.update)
                pyglet.clock.unschedule(finish_line.update)

    def map_finished(self):
        try:
            if self.absolute_y >= self.map.length:
                return True
        except AttributeError:
            pass
        return False

    def check_if_is_approaching_EOM(self):
        try:
            if self.map.length - self.absolute_y <= 1000 and not self.approaching_EOM:
                self.approaching_EOM = True
                if len(self.map.exits) > 1:
                    # show choices if applicable
                    self.show_choices = True
        except AttributeError:
            pass

    def generate_exit_choices_labels(self):
        self.exit_choices_labels = []
        self.exit_choices_labels_batch = pyglet.graphics.Batch()
        exit_x_assignment_idx = 0
        for exit in self.exit_choices:
            self.exit_choices_labels.append(
                make_label(
                    text=maps[exit].display_name,
                    x=120,
                    y=CHOICE_BUTTONS_Y_AXES[exit_x_assignment_idx],
                    width=300,
                    height=30,
                    align="left",
                    anchor_y="center",
                    size=28,
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

    def check_if_hit_npc_or_bonus(self):
        if hasattr(self, "map"):
            for npc in self.map.npcs:
                if self.lane == npc.lane and 0 < npc.y - self.y < 45:
                    if player_bulldozer_mode:
                        if npc.running:  # if they're still alive
                            npc.image = centered_image("bloodstain.png")
                            npc.running = False
                            npc.v = 0
                            self.people_killed += 1
                    else:
                        npc.on_hit(self)
            for bonus in self.map.bonuses:
                if self.lane == bonus.lane and 0 < bonus.y - self.y < 45:
                    bonus.on_hit(self)

    def resume_running(self, _):
        # called after player is no longer frozen
        ice_cube_img.visible = False
        self.allowed_to_run = True


class NPC(pyglet.sprite.Sprite):
    # NPC: non-player characters
    # inherits pyglet.sprite.Sprite
    # includes other students and faculty
    is_player = False
    initiating = True
    running = True

    def __init__(self, track, lane=0, v=0.0, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.opacity = 160  # looks gray
        self.map = track
        self.lane = lane
        # init_v is static
        self.init_v = v
        self.v = v
        self.acc = 5

    def update(self, dt):
        # velocity control
        if self.running:
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
        if self.running:
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


class Bonus(pyglet.sprite.Sprite):
    # Bonus: static object with various outcomes
    # not all positive
    # inherits pyglet.sprite.Sprite
    # does not switch lanes
    def __init__(self, category, lane=0, lanes_x=(), *args, **kwargs):
        self._category = category
        super().__init__(
            img=centered_image("bonus/" + BONUS_DATA[category]["image"]),
            *args,
            **kwargs,
        )
        self.lane = lane
        self.x = lanes_x[lane]

    def update(self, dt):
        self.y -= player.v * dt

    @property
    def category(self):
        return self._category

    @category.setter
    def category(self, cat):
        perceived_category = cat if not self.category == "disabled" else ""
        self._category = cat
        if cat == "bulldozer":
            self.image = centered_image("bonus/bulldozer.png")
        elif cat == "exit_bulldozer":
            self.image = centered_image("bonus/exit_bulldozer.png")

    def on_hit(self, character):
        global player_bulldozer_mode
        if self.category == "slip_left":
            character.left()
        elif self.category == "slip_right":
            character.right()
        elif self.category == "accelerate":
            character.v *= 1.5
        elif self.category == "bulldozer":
            if character.is_player:
                player_bulldozer_mode = True
                character.map.toggle_bulldozer_bonuses()
        elif self.category == "exit_bulldozer":
            if character.is_player:
                player_bulldozer_mode = False
                character.map.toggle_bulldozer_bonuses()
        elif self.category == "freeze":
            if character.is_player:
                character.allowed_to_run = False
                character.v = 0
                ice_cube_img.position = player.position
                ice_cube_img.visible = True
                pyglet.clock.schedule_once(character.resume_running, 2)
        elif self.category == "-1s":
            if character.is_player:
                clocktick(0)

        self.category = "disabled"


class Map:
    def __init__(
        self,
        name="",
        display_name="",
        lanes=1,
        length=10000,
        npc_density=0.0,
        npc_reverse_rate=0.0,
        bonus_density=0.0,
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
        # npc_reverse_rate: N(NPC's going backwards)/N(NPC's)
        self.npc_reverse_rate = npc_reverse_rate
        self.initiate_npcs()
        self.bonus_density = bonus_density
        self.initiate_bonuses()
        self.exits = exits
        self.minimap_image_path = minimap_image_path

    def initiate_npcs(self):
        npcs = []
        batch = pyglet.graphics.Batch()
        total = self.npc_density * self.length * self.lanes
        for _ in range(round(total * (1-self.npc_reverse_rate * 1.25))):
            # add new NPCs to `batch`
            # NPCs that have been running midway since game started
            npcs.append(
                NPC(
                    img=centered_image(f"player/{choice(avatars)}"),
                    track=self,
                    lane=randint(0, self.lanes - 1),
                    y=randint(-self.length / 4, self.length),
                    batch=batch,
                    v=40 + random() * 40,
                )
            )
        for _ in range(round(total * self.npc_reverse_rate * 1.25)):
            # NPC's, running in reverse
            npcs.append(
                NPC(
                    img=centered_image(f"player/{choice(avatars)}"),
                    track=self,
                    lane=randint(0, self.lanes - 1),
                    y=randint(0, self.length * 5 / 4),
                    batch=batch,
                    v=-40 - random() * 40,
                )
            )
        self.npcs = npcs
        self.npc_batch = batch

    def initiate_bonuses(self):
        bonuses = []
        batch = pyglet.graphics.Batch()

        while len(bonuses) < self.bonus_density * self.length * self.lanes:
            category = choice(list(BONUS_DATA))
            bonus = BONUS_DATA[category]
            lane = randint(0, self.lanes - 1)
            if not (
                # check if bonus is allowed on current map or on randomly generated lane
                (self.lanes == 1 and not bonus["1_lane"])  # single lane
                or (lane == 0 and not bonus["leftmost_lane"])
                or (lane == self.lanes - 1 and not bonus["rightmost_lane"])
            ) and (
                bonus["weight"] == 1.0 or bonus["weight"] > random()
            ):  # also apply weight
                bonuses.append(
                    Bonus(
                        category,
                        lane=lane,
                        lanes_x=self.lanes_x,
                        y=randint(100, self.length),
                        batch=batch,
                    )
                )

        self.bonuses = bonuses
        self.bonus_batch = batch

    def toggle_bulldozer_bonuses(self):
        if player_bulldozer_mode:
            for bonus in self.bonuses:
                if bonus.category == "bulldozer":
                    bonus.category = "exit_bulldozer"
        else:
            for bonus in self.bonuses:
                if bonus.category == "exit_bulldozer":
                    bonus.category = "bulldozer"


class FinishLine(pyglet.sprite.Sprite):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.y = height + 120
        self.x = width // 2
        self.moving = False

    def update(self, dt):
        if self.moving:
            dy = player.v * dt
            self.y -= dy
            next_map_cue.y -= dy
            if self.y < player.y:
                self.reset()

        else:
            if len(route) and route[map_idx].length - player.absolute_y < height:
                self.moving = True

    def reset(self):
        self.moving = False
        self.y = height + 120
        next_map_cue.y = height + 150


""" GRAPHICS SETUP """
# (nearly) fullscreen
width, height = 1920, 1020
window = pyglet.window.Window(width=width, height=height, caption="跑饭 - Lunchrush")
window.set_icon(pyglet.image.load("./res/icon.png"))
lane_width = 100
# solid white bg
white = pyglet.image.SolidColorImagePattern((255, 255, 255, 255)).create_image(
    width, height
)

pyglet.resource.path = ["./res"]
pyglet.resource.reindex()


def centered_image(filename: str):
    return center_image(pyglet.resource.image(filename))


solid_line_img = pyglet.resource.image("track_separator_solid.png")
lane_sep_img = pyglet.resource.image("track_separator.png")
LN_SEP_SEGM_LEN = 156

# button images beside choice labels to indicate player which button(s) to push
button_imgs = {}
for name in ("red", "yellow", "both"):
    button_imgs[name] = pyglet.image.load(f"./res/buttons/{name}.png")
    button_imgs[name].anchor_y = 40

BUTTON_X_AXIS = 60  # x-axis of the button icons of exit selection

lunchrush_img = pyglet.sprite.Sprite(
    img=pyglet.resource.image("lunchrush.png"), x=width - 320, y=40
)

ice_cube_img = pyglet.sprite.Sprite(img=centered_image("ice_cube.png"), x=0, y=0)
ice_cube_img.visible = False
ice_cube_img.opacity = 192  # translucent overlay on player when they're frozen

""" SCORING SETUP """
# displayed and updated over time
time = [12, 0, 0]
time_label = make_label(text=format_time(time), x=20, y=(height - 68), size=48)
v_label = make_label(text="v=0.00", x=20, y=(height - 120), size=32)
y_label = make_label(text="y=0.00/0", x=20, y=(height - 160), size=32)
map_label = make_label(
    text="你在： ---", x=20, y=(height - (220 if DEBUG else 120)), size=32,
)
bulldozer_label = make_label(text="您已进入推土机模式", x=width - 300, y=360)
# NOTE TO CLUB UNION:
# IF YOU'RE TRYING TO INTERVENE,
# FUCK YOU.
people_killed_label_template = lambda n_killed: f"已碾压 {n_killed} 人"
people_killed_label = make_label(
    text=people_killed_label_template(0), x=width - 300, y=320,
)

victory_bg = pyglet.sprite.Sprite(
    img=centered_image("victory_bg.png"), x=width // 2, y=height // 2,
)

victory_bg.scale_x = 4
victory_bg.scale_y = 4
victory_bg.visible = False

victory_label = make_label(
    size=32,
    x=width // 2,
    y=height // 2 - 300,
    width=width - 100,
    anchor_x="center",
    align="center",
    color=(255, 255, 255, 255),
    bold=True,
    multiline=True,
)

WEIGHT_DIVISOR = 16


def victory_fx(dt):
    # move player to window center
    # until player is roughly aligned (20px bias allowed)
    if not (abs(player.x - width // 2) < 20 and abs(player.y - height // 2) < 20):
        player.x = ((WEIGHT_DIVISOR - 1) * player.x + width / 2) // WEIGHT_DIVISOR
        player.y = ((WEIGHT_DIVISOR - 1) * player.y + height / 2) // WEIGHT_DIVISOR
        # scale: target is 4; to slow down expansion, `4` is given a weight of 3/4
        scale = ((WEIGHT_DIVISOR - 1) * player.scale_x + 4) / WEIGHT_DIVISOR
        player.scale_x = scale
        player.scale_y = scale

    victory_bg.rotation += 4 * dt
    if victory_bg.rotation > 360:
        victory_bg.rotation -= 360


""" MAPS INITIATION """
# load all maps listed in efzmaps.csv
# TODO: dynamic loading for less RAM (not necessary for now)
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
        npc_reverse_rate=map_dict["npc_reverse_rate"],
        bonus_density=map_dict["bonus_density"],
        exits=map_dict["exits"],
        minimap_image_path=map_dict["minimap_image"],
    )
route = []
map_idx = 0
next_map_cue = make_label(
    x=width // 2,
    y=(height + 20),
    color=(248, 101, 57, 255),
    size=32,
    anchor_x="center",
)
finish_line = FinishLine(img=centered_image("finish_line.png"))

""" PLAYER INITIATION """
player = Player(img=centered_image("player/megan.png"))

selection_cursor = [0, 0]  # x, y, 0-indexed
cursor_matrix_size = (3, 2)  # 1-indexed
cursor_sprite = pyglet.sprite.Sprite(img=centered_image("cursor_box.png"))
panel_demonstration = pyglet.resource.image("panel.png")
confirmed = False

# generate batches
avi_selection_label = make_label(text="请选择头像", size=32, x=950, y=900, anchor_x="center")
avi_id = 0
avi_sprites = []
avi_batch = pyglet.graphics.Batch()
for avi_filename in avatars:
    avi_sprites.append(
        pyglet.sprite.Sprite(
            **AVATAR_LABEL_AXES[avi_id],  # contains x's and y's
            img=centered_image(f"player/{avi_filename}"),
            batch=avi_batch,
        )
    )
    avi_id += 1

clr_selection_label = make_label(text="请选择班级", size=32, x=950, y=900, anchor_x="center")
clr_id = 0
clr_labels = []
clr_batch = pyglet.graphics.Batch()
for map_name in LIST_OF_CLASSROOMS:  # 29 classes
    clr_labels.append(
        make_label(
            text=raw_maps[map_name]["display_name"],
            **CLASSROOM_LABEL_AXES[clr_id],
            batch=clr_batch,
        )
    )
    clr_id += 1
prev_clr_id = -1

tutorial_img = pyglet.resource.image("tutorial.png")


@window.event
def on_draw():
    # cover window with white bg
    # equivalent of clearing canvas
    white.blit(0, 0)  # update time label, unless reached cafeteria
    global init_selections_left, confirmed, selection_cursor, cursor_matrix_size, prev_clr_id
    if init_selections_left == 3:
        # select avatar
        avi_selection_label.draw()
        avi_batch.draw()
        panel_demonstration.blit(720, 20)
        id = selection_cursor[1] * cursor_matrix_size[0] + selection_cursor[0]
        cursor_position = AVATAR_LABEL_AXES[id]
        cursor_sprite.x = cursor_position["x"]
        cursor_sprite.y = cursor_position["y"]
        cursor_sprite.draw()
        if confirmed:
            player.image = centered_image(f"player/{avatars[id]}")
            confirmed = False
            cursor_matrix_size = (3, 10)
            selection_cursor = [0, 0]
            init_selections_left -= 1

    elif init_selections_left == 2:
        # select classroom of departure
        clr_selection_label.draw()
        clr_batch.draw()
        panel_demonstration.blit(720, 20)
        id = selection_cursor[0] * cursor_matrix_size[1] + selection_cursor[1]
        if not id == prev_clr_id and id < len(LIST_OF_CLASSROOMS):
            clr_labels[prev_clr_id].color = (0, 0, 0, 255)
            clr_labels[id].color = (248, 101, 57, 255)
            prev_clr_id = id

        if confirmed:
            route.append(maps[LIST_OF_CLASSROOMS[id]])
            confirmed = False
            init_selections_left -= 1

    elif init_selections_left == 1:
        tutorial_img.blit(0, 0)
        if confirmed:
            player.load_map()
            player.allowed_to_run = True
            pyglet.clock.schedule_interval(clocktick, 1)  # start clock-ticking
            confirmed = False
            init_selections_left -= 1

    else:
        if not player.reached_cafeteria:
            time_label.text = format_time(time)
        time_label.draw()
        map_label.draw()
        if player_bulldozer_mode:
            bulldozer_label.draw()
            people_killed_label.text = people_killed_label_template(
                player.people_killed
            )
            people_killed_label.draw()

        if DEBUG:
            v_label.text = f"v={player.v: .2f}"
            v_label.draw()
            y_label.text = f"y={player.absolute_y: .2f}/{player.map.length}"
            y_label.draw()
        x_axes = calc_lane_separators_x(width, lane_width, player.map.lanes)
        for x in (x_axes[0], x_axes[-1]):  # exterior boundary
            solid_line_img.blit(x, 0)
        for x in x_axes[1:-1]:  # interior seps
            lane_sep_img.blit(x, -player.absolute_y % LN_SEP_SEGM_LEN - LN_SEP_SEGM_LEN)
        finish_line.draw()
        next_map_cue.draw()
        route[map_idx].npc_batch.draw()
        route[map_idx].bonus_batch.draw()
        if player.show_choices:
            player.exit_choices_labels_batch.draw()
            button_imgs["red"].blit(BUTTON_X_AXIS, CHOICE_BUTTONS_Y_AXES[0])
            button_imgs["yellow"].blit(BUTTON_X_AXIS, CHOICE_BUTTONS_Y_AXES[1])
            if len(player.exit_choices) == 3:
                button_imgs["both"].blit(BUTTON_X_AXIS, CHOICE_BUTTONS_Y_AXES[2])
        player.minimap.blit(100, 500 if DEBUG else 600)
        victory_bg.draw()
        victory_label.draw()
        player.draw()
        ice_cube_img.draw()

    lunchrush_img.draw()  # on-the-go marketing


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
    elif symbol == keys.H:
        move_cursor(selection_cursor, "h", cursor_matrix_size)
    elif symbol == keys.J:
        move_cursor(selection_cursor, "j", cursor_matrix_size)
    elif symbol == keys.K:
        move_cursor(selection_cursor, "k", cursor_matrix_size)
    elif symbol == keys.L:
        move_cursor(selection_cursor, "l", cursor_matrix_size)
    elif symbol == keys.ENTER:
        global confirmed
        confirmed = True


""" SERIAL """
pps = {  # previous pin values
    "pedal_l": 0,
    "pedal_r": 0,
    "panel_l": 0,  # panel_[lr]: green button 60mm in diameter
    "panel_r": 0,
    "panel_a": 0,  # red button 30mm
    "panel_b": 0,  # yellow button 30mm
}
foot_down = 0  # the foot stamped down


def react_to_serial(_):
    # access values read and stored in `readserial.py`
    global pps
    global foot_down
    rps = view_value()  # response pin values
    # renamed pin value variables to keep it short
    # just remember pps is old data and rps is new
    # pedal_[lr]: type int. interpreted as bools.
    pedal_l = rps["pedal_l"]
    pedal_r = rps["pedal_r"]
    # player.step() criteria:
    # L0R1 -> L1R0 or L1R0 -> L0R1
    res_foot_down = foot_down  # default

    if not init_selections_left:
        if pedal_l and (not pedal_r):
            res_foot_down = 0
        elif (not pedal_l) and pedal_r:
            res_foot_down = 1
        if not res_foot_down == foot_down:
            player.step()
            foot_down = res_foot_down
        # steering
        if not pps["panel_l"] and rps["panel_l"]:
            player.left()
        elif not pps["panel_r"] and rps["panel_r"]:
            player.right()
        # decision-making
        if not (pps["panel_a"] and pps["panel_b"]):
            # if player was not pushing down both buttons on prev read
            # prevents non-simultaneous button release
            if not pps["panel_a"] and rps["panel_a"] and not rps["panel_b"]:  # red
                player.alter_exit(0)
            elif not pps["panel_b"] and rps["panel_b"] and not rps["panel_a"]:  # yellow
                player.alter_exit(1)
            elif rps["panel_a"] and rps["panel_b"]:  # both
                player.alter_exit(2)
    else:
        if not pps["panel_l"] and rps["panel_l"]:
            move_cursor(selection_cursor, "h", cursor_matrix_size)
        elif not pps["panel_a"] and rps["panel_a"]:
            move_cursor(selection_cursor, "j", cursor_matrix_size)
        elif not pps["panel_b"] and rps["panel_b"]:
            move_cursor(selection_cursor, "k", cursor_matrix_size)
        elif not pps["panel_r"] and rps["panel_r"]:
            move_cursor(selection_cursor, "l", cursor_matrix_size)
        elif (not pps["pedal_l"] and rps["pedal_l"]) or (
            not pps["pedal_r"] and rps["pedal_r"]
        ):
            global confirmed
            confirmed = True

    pps = rps


def refresh_NPCs(dt):
    if len(route):
        for npc in route[map_idx].npcs:
            npc.update(dt)


def refresh_bonuses(dt):
    if len(route):
        for bonus in route[map_idx].bonuses:
            bonus.update(dt)


def NPC_react(_):
    if len(route):
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


pyglet.clock.schedule_interval(react_to_serial, 0.02)
pyglet.clock.schedule_interval(refresh_NPCs, 0.05)
pyglet.clock.schedule_interval(refresh_bonuses, 0.05)
pyglet.clock.schedule_interval(NPC_react, 0.5)
pyglet.clock.schedule_interval(player.update, 0.05)
pyglet.clock.schedule_interval(finish_line.update, 0.05)
pyglet.app.run()
