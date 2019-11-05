# 跑饭 · LUNCHRUSH
## Hardware
So far, the GPIO control has not yet been implemented. The game is currently controled with the keyboard (left/right arrow and spacebar).  After the GPIO work is done, you will be able to control the game using equipments to be specified in this document in the future.

## Dependencies
`pip install` the following:
- pyglet

## Debugging / Running
The entry point is `graphics.py` as for now. Run `python graphics.py` to start (or python3, whose '3' shouldn't exist at the year of 2019). Use left/right arrows to switch lanes (6 in total), and spacebar to accelerate. The game will stop after all maps listed in `gamedata.py` (`maps = [...]`) are finished.

## Licensing
[GPLv3](https://www.gnu.org/licenses/gpl-3.0).
