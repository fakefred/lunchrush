from machine import Pin
from time import sleep_ms

pin_no = [2, 15]

pins = [Pin(i, Pin.IN) for i in pin_no]

while True:
    out = ''
    for pin in pins:
        out += str(1 - int(pin.value()))  # reverse
    print(out)
    sleep_ms(10)
