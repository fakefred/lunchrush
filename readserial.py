import serial
from threading import Thread


CONNECTED = True
line = ""


def read_line_thread() -> str:
    global line
    while True:
        line = s.readline().decode("utf-8")


def bit_str_to_states(bitstr: str) -> list:
    if all([True if char in ("0", "1") else False for char in bitstr]):
        # also True if bitstr == ''
        return [int(bitchar) for bitchar in bitstr]
    else:
        return []


def fill_template(states: list) -> dict:
    return {
        "pedal_l": states[0],
        "pedal_r": states[1],
        "panel_l": states[2],
        "panel_r": states[3],
        "panel_a": states[4],
        "panel_b": states[5],
    }


PINS = 6  # number of pins connected
read_thread = Thread(None, read_line_thread)


# reads output from ESP32 DevKit C running micropython
# connect ESP32 via USB
# change port accordingly
try:
    s = serial.Serial("/dev/ttyUSB0", 115200, timeout=0.1)
    read_thread.start()

except serial.serialutil.SerialException:
    CONNECTED = False


def view_value() -> int:
    global line
    states = bit_str_to_states(line.strip())
    if len(states) == PINS and CONNECTED:
        return fill_template(states)
    else:
        # default
        return fill_template([0] * PINS)

