import pyglet
from utils import dualdigit, format_time
from gamedata import maps, DEBUG
from initplayer import player
from initnpc import npcs, npc_batch

""" GRAPHICS SETUP """
# (nearly) fullscreen
width, height = 1920, 1006
window = pyglet.window.Window(width=width, height=height)
# solid white bg
white = pyglet.image.SolidColorImagePattern(
    (255, 255, 255, 255)).create_image(width, height)

pyglet.resource.path = ['./res']
pyglet.resource.reindex()

""" OPERATION SETUP """
keys = pyglet.window.key

""" SCORING SETUP """
# displayed and updated over time
time = [12, 0, 0]

time_label = pyglet.text.Label(
    text=format_time(time), x=20, y=(height - 68), color=(0, 0, 0, 255), font_size=48)

vlabel = pyglet.text.Label(
    text='v=0.00', x=20, y=(height - 120), color=(0, 0, 0, 255), font_size=32)

ylabel = pyglet.text.Label(
    text='y=0.00', x=20, y=(height - 160), color=(0, 0, 0, 255), font_size=32)


""" START GRAPHICS """
@window.event
def on_draw():
    # cover window with white bg
    # equivalent of clearing canvas
    white.blit(0, 0)

    # update time label
    time_label.text = format_time(time)
    time_label.draw()

    if DEBUG:
        vlabel.text = f'v={player.v: .2f}'
        vlabel.draw()
        ylabel.text = f'y={player.absolute_y: .2f}'
        ylabel.draw()

    npc_batch.draw()
    player.draw()


@window.event
def on_key_press(symbol, mods):
    if symbol == keys.SPACE:
        player.step()
    elif symbol == keys.LEFT:
        player.left()
    elif symbol == keys.RIGHT:
        player.right()


def refresh_NPCs(dt):
    for npc in npcs:
        npc.update(dt)


def clocktick(_):
    # time = [h, m, s]
    time[2] += 1
    # running time > 12 hours not handled
    for i in (2, 1):
        if time[i] == 60:
            time[i] = 0
            time[i - 1] += 1


pyglet.clock.schedule_interval(clocktick, 1)
pyglet.clock.schedule_interval(refresh_NPCs, 1/60.0)
pyglet.clock.schedule_interval(player.update, 0.05)
pyglet.app.run()
