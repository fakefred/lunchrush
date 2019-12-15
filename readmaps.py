from csv import reader
from utils import calc_lanes_x


def read(window_width: int, lane_width: int) -> dict:
    maps_file = list(reader(open("efzmaps.csv")))
    keys = maps_file[0]
    values = maps_file[1:]
    maps = {}
    for line in values:
        # 0    1            2     3      4           5             6     7
        # name,display_name,lanes,length,npc_density,bonus_density,exits,minimap_image
        line[2] = int(line[2])
        line[3] = int(line[3]) * 40  # convert paces to pixels
        line[4] = float(line[4])
        line[5] = float(line[5])
        line[6] = line[6].split(";")
        line[7] = f"./res/minimap/{line[7]}.png"
        # this_map = {'lanes_x': calc_lanes_x(window_width, lane_width, line[2])}
        this_map = {}
        for i in range(1, len(line)):
            this_map[keys[i]] = line[i]

        maps[line[0]] = this_map

    return maps


LIST_OF_CLASSROOMS = [line.strip() for line in open("efzclassrooms.txt").readlines()]
