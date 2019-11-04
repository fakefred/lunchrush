def dualdigit(num: int) -> str:
    return (str(num) if num > 9 else '0' + str(num)) if num < 100 else str(num % 100)


def format_time(time):
    return f'{str(time[0])}:{dualdigit(time[1])}:{dualdigit(time[2])}'


def center_image(image):
    # sets an image's anchor point to its center
    # works with pyglet
    image.anchor_x = image.width // 2
    image.anchor_y = image.height // 2
    return image
