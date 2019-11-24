from csv import reader
from utils import calc_lanes_x


def read(window_width: int, lane_width: int) -> dict:
    maps_file = list(reader(open('efzmaps.csv')))
    keys = maps_file[0]
    values = maps_file[1:]
    maps = {}
    for line in values:
        # 0    1            2    3            5           6             7
        # name,display_name,type,lanes,length,npc_density,bonus_density,exits
        line[3] = int(line[3])
        line[4] = int(line[4]) * 40  # convert paces to pixels
        line[5] = float(line[5])
        line[6] = float(line[6])
        line[7] = line[7].split(';')
        # this_map = {'lanes_x': calc_lanes_x(window_width, lane_width, line[2])}
        this_map = {}
        for i in range(1, len(line)):
            this_map[keys[i]] = line[i]

        maps[line[0]] = this_map

    return maps
