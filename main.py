from machine import UART, Pin
import time
import uctypes


pico_led = Pin(25, Pin.OUT)  # Onboard LED is GPIO 25

num_rows = 6
row_pin_outputs = [0, 1, 2, 3, 4, 5]
num_cols = 9
col_pin_inputs = [7, 8, 9, 10, 11, 12, 13, 14, 15]
row_outputs = [Pin(n, Pin.OUT) for n in row_pin_outputs]
col_inputs = [Pin(n, Pin.IN, Pin.PULL_DOWN) for n in col_pin_inputs]
uart = UART(0, baudrate=31250, bits=8, parity=None, stop=1, tx=Pin(16), rx=Pin(17))
keycodes = [4,51,42,33,24,15,6,53,44,35,26,17,8,45,36,27,18,9,0,46,37,28,19,10,1,48,39,30,21,12,3,50,41,32,23,14,5,52,43,34,25,16,7,47,38,29,20,11,2]
keymap = dict(zip( keycodes, range(49) ))
buf = bytearray(3)
keybitmap = 0x0000000000000000
keybitmap_persist = 0x0000000000000000
KEYEVENT_KEYPRESS = 0x80
KEYEVENT_KEYREL = 0x00
NUM_KEYS = 49
NOTE_OFFSET = 0x3c - 24 #3c is key 24
vel = 0x30
eventq = []
VER = 1 # 8/9/2025: multi press, release events tested, works well

def gen_events():
    global eventq
    global keybitmap
    for i in range(NUM_KEYS):
        # check press
        if ((keybitmap & (1<<i)) != 0) and ((keybitmap_persist & (1<<i)) == 0):
            eventq.append ( 0x80 + i )
        # check release
        if ((keybitmap & (1<<i)) == 0) and ((keybitmap_persist & (1<<i)) != 0):
            eventq.append ( i )

def handle_key_events():
    while (len(eventq) > 0):
        evt = eventq.pop()
        if (evt & 0x80):
            buf[0], buf[1], buf[2] = 0x90, (NOTE_OFFSET + (evt & 0x7f) ), vel
        else:
            buf[0], buf[1], buf[2] = 0x90, (NOTE_OFFSET + (evt & 0x7f) ), 0
        uart.write(buf)

def scan():
    global keybitmap
    keybitmap = 0
    rawkey = 0
    for row_pin in row_outputs:
        row_pin.value(1)    
        time.sleep(0.0002)
        for col_pin in col_inputs:
            if col_pin.value() == 1:
                key = keymap[rawkey]
                keybitmap |= 2 ** key
            rawkey = rawkey + 1
        row_pin.value(0)

for pin in row_outputs:
    pin.value(0)
row = 0
while (1):
    scan()
    pico_led.toggle()
    gen_events()
    #print("key=", keybitmap, "oldkey=", keybitmap_persist, "queue=", eventq)
    handle_key_events()
    keybitmap_persist = keybitmap


    # timing
    # v1:
    # pulse_wid = 164us   (200us nominal)
    # cycle_tim = 3.77ms  (1.2ms nominal)
    # lat = 95ms
    #
    #
    #



