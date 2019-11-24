from machine import Pin
from time import sleep_ms

pins = [
    Pin(2, Pin.IN),  # pedal_l
    Pin(15, Pin.IN)  # pedal_r
]

while True:
    out = ''
    for pin in pins:
        out += str(1 - int(pin.value()))  # reverse
    print(out)
    sleep_ms(10)
