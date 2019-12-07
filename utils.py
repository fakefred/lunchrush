from pyglet.text import Label


def dualdigit(num: int) -> str:
    return (str(num) if num > 9 else "0" + str(num)) if num < 100 else str(num % 100)


def format_time(time: list) -> str:
    return f"{str(time[0])}:{dualdigit(time[1])}:{dualdigit(time[2])}"


def center_image(image):
    # sets an image's anchor point to its center
    # works with pyglet
    image.anchor_x = image.width // 2
    image.anchor_y = image.height // 2
    return image


def calc_lanes_x(window_width: int, lane_width: int, lanes: int) -> tuple:
    # calculate x axis of the center of each lane
    start = int((window_width - lane_width * lanes) / 2 + lane_width / 2)
    end = int(start + lane_width * lanes) - 1
    return tuple(range(start, end, lane_width))


def calc_lane_separators_x(window_width: int, lane_width: int, lanes: int) -> tuple:
    lanes_x = calc_lanes_x(window_width, lane_width, lanes)
    return [int(x - lane_width / 2) for x in lanes_x + (lanes_x[-1] + lane_width,)]


def calc_selecs_x(
    window_width: int, padding: int, labelwidth: int, len_choices: int
) -> tuple:
    if len_choices == 2:
        return (
            window_width / 2 - padding / 2 - labelwidth / 2,
            window_width / 2 + padding / 2 + labelwidth / 2,
        )
    elif len_choices == 3:
        return (
            window_width / 2 - padding - labelwidth,
            window_width / 2,
            window_width / 2 + padding + labelwidth,
        )


BONUS_FILENAMES = {
    "slip_left": "slip_left.png",
    "slip_right": "slip_right.png",
    "accelerate": "accelerate.png",
    "bulldozer": "bulldozer.png",
}


def make_label(text="", size=24, x=0, y=0, color=(0, 0, 0, 255), *args, **kwargs):
    return Label(
        text=text,
        x=x,
        y=y,
        color=color,
        font_name="Noto Sans CJK SC",
        font_size=size,
        *args,
        **kwargs,
    )
