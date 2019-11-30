# 跑饭 · LUNCHRUSH
## Hardware
The game currently can be controlled with either (a) the keyboard (left/right arrow and spacebar), and (b) [WIP; only controlling stepping, currently disabled] an ESP32 (for example) with [Micropython](https://micropython.org). The scheme is **physical switches ->(GPIO)-> ESP32 ->(USB Serial)->     `pyserial` -> Lunchrush.** After the GPIO work is done, you will be able to control the game using equipments to be specified in this document in the future.

## Dependencies
`pip install` the following:
- `pyglet`
- `pyserial` (imported as `serial`)

## Debugging / Running
The entry point is `graphics.py` as for now. Run `python graphics.py` to start (or python3, whose '3' shouldn't exist at the year of 2019).

### Keyboard Control
- Spacebar: accelerate
- Left/right arrows: switch lanes
- 1/2/3: switch exit

## Licensing
- [GPLv3](https://www.gnu.org/licenses/gpl-3.0) for all code in this repository;
- [CC BY-NC 2.5](https://creativecommons.org/licenses/by-nc/2.5/) for all images in `./res/player/` that are cropped out of xkcd comics;
- [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/) for everything else in `./res/`.
