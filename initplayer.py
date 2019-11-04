from player import Player
from pyglet import resource
from gamedata import maps
from utils import center_image

player = Player(img=center_image(
    resource.image('player/megan.png')), maps=maps)
