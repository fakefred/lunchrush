from machine import Pin
from time import sleep_ms

pin_no = [34, 35, 32, 33, 25, 26]

pins = [Pin(i, Pin.IN) for i in pin_no]

while True:
    out = ""
    for pin in pins:
        # reverse, because of pull-up resistors
        out += str(1 - int(pin.value()))
    print(out)
    sleep_ms(20)
