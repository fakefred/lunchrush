import serial
from threading import _start_new_thread as start_new_thread

# reads output from ESP32 DevKit C running micropython
# connect ESP32 via USB
# change port accordingly
s = serial.Serial('/dev/ttyUSB0', 115200, timeout=0.05)

line = ''

def read_line_thread() -> str:
    global line
    while True:
        line = s.readline().decode('utf-8')

def bit_str_to_states(bitstr: str) -> list:
    if all([True if char in ('0', '1') else False for char in bitstr]):
        # also True if bitstr == ''
        return [int(bitchar) for bitchar in bitstr]
    else:
        return []

# code-golf version:
# bsts = lambda b:list(b)if all([1 if c in('0','1')else 0 for c in b])else[]

def fill_template(states: list) -> dict:
    return {
        'pedal_l': states[0],
        'pedal_r': states[1]
    }

PINS = 2  # number of pins connected

def view_value() -> int:
    global line
    states = bit_str_to_states(line.strip())
    if len(states) == PINS:  # TODO: add more states
        return fill_template(states)
    else:
        # default
        return fill_template([0] * PINS)

start_new_thread(read_line_thread)