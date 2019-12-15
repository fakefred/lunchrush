from csv import reader


def read_bonuses() -> dict:
    bonuses_file = list(reader(open("bonuses.csv")))
    keys = bonuses_file[0]
    values = bonuses_file[1:]
    bonuses = {}
    for line in values:
        # 0    1     2      3      4             5
        # name,image,weight,1_lane,leftmost_lane,rightmost_lane
        line[2] = float(line[2])
        for key in range(3, 6):
            line[key] = bool(int(line[key]))

        this_bonus = {}
        for i in range(1, len(line)):
            this_bonus[keys[i]] = line[i]

        bonuses[line[0]] = this_bonus

    return bonuses
