# 跑饭 · LUNCHRUSH

## DISCOUNT!
You can be qualified for a 0.40 RMB discount
(can be topped with the discount acquired through pre-purchase) if you:
- star this repo with a valid GitHub Account;
- show me your logged-on GitHub profile page when experiencing this game on Dec. 30.

通过以下方式可以获取 0.40 元的折扣（可以享受预购折上折）：
- 用有效的 GitHub 账号给此仓库（repo）加星（star）；
- 在 12 月 30 日体验游戏时向我展示你的已登录的 GitHub 页面。

## Hardware

The game currently can be controlled with either (a) the keyboard (left/right arrow and spacebar), and (b) an ESP32 (for example) with [Micropython](https://micropython.org). The scheme is **physical switches ->(GPIO)-> ESP32 ->(USB Serial)-> `pyserial` -> Lunchrush.** The pin connections are:

GPIO Pin No. | Physical Equipment | Controls
---|---|---|---
34 | Left Pedal | `player.step()` (in combination with 35)
35 | Right Pedal | `player.step()`
32 | Left Button | `player.left()` and left in init selection phase
33 | Right Button | `player.right()` and right in init selection phase
25 | Red Button | select exit #1
26 | Yellow Button | select exit #2

to select exit #3, push 25 and 26 simultaneously.

## Dependencies

`pip install` the following:

- `pyglet`
- `pyserial` (imported as `serial`)

## Debugging / Running

The entry point is `graphics.py` as for now. Run `python graphics.py` to start (or python3, whose '3' shouldn't exist at the year of 2019).

### Keyboard Control

- Init Phase: selecting avatar and classroom
    - h/j/k/l for left/down/up/right (vim keybinding)
    - enter for confirmation
- Spacebar: accelerate
- Left/right arrows: switch lanes
- 1/2/3: switch exit

## Licensing

- [GPLv3](https://www.gnu.org/licenses/gpl-3.0) for all code in this repository;
- [CC BY-NC 2.5](https://creativecommons.org/licenses/by-nc/2.5/) for all images in `./res/player/` that are cropped out of xkcd comics;
- Icons in `./res/bonus/` are modified icons from [icons8](https://icons8.com);
- [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/) for everything else in `./res/`, except `ice_cube.png`,  whose copyright holder is unknown.
