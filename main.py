from machine import ADC, Pin, UART
from collections import deque
import time
import uctypes

# define
def calc_mean(data):
    total = sum(data)
    return round(total / len(data))

class analog_input:
    MAXVAL = 65535
    NUM_AVG = 16
    def __init__(self, chan):
        self.adc = ADC(Pin(chan))  # GP26 is ADC0
        self.q = deque((), self.NUM_AVG)
    def readraw(self):
        return self.adc.read_u16() >> 9
    def read(self):
        val = self.adc.read_u16()
        self.q.append(val)
        return calc_mean(self.q) >> 9

class key_scanner:
    NUM_KEYS = 49
    ROW_SWITCH_DELAY = 0.0002
    KEYEVENT_KEYPRESS = 0x80
    KEYEVENT_KEYREL = 0x00
    SCAN_CODES = [ 4,51,42,33,24,15, 6,53,44,35,26,17, 8,45,36,27,18, 9, 0,46,37,28,19,10, 1,48,39,30,21,12, 3,50,41,32,23,14, 5,52,43,34,25,16, 7,47,38,29,20,11, 2]

    def __init__(self, midi_buf_size):
        
        self.keybitmap_persist = 0x0000000000000000
        self.eventq = deque((), midi_buf_size)
        self.keymap = dict(zip( self.SCAN_CODES, range(49) )) # keycode from scancode

    def scan(self):
        # scan and obtain key bitmap
        keybitmap = 0
        scancode = 0
        for row_pin in row_outputs:
            row_pin.value(1)    
            time.sleep(self.ROW_SWITCH_DELAY)
            for col_pin in col_inputs:
                if col_pin.value() == 1:
                    key = self.keymap[scancode]
                    if DEBUG:
                        print("scancode=", scancode, "keycode=", key)
                    keybitmap |= 2 ** key
                scancode = scancode + 1
            row_pin.value(0)

        # generate "press" and "unpress" events from keybitmap
        for i in range(self.NUM_KEYS):
            # check press
            if ((keybitmap & (1<<i)) != 0) and ((self.keybitmap_persist & (1<<i)) == 0):
                self.eventq.append ( 0x80 + i )
            # check release
            if ((keybitmap & (1<<i)) == 0) and ((self.keybitmap_persist & (1<<i)) != 0):
                self.eventq.append ( i )
                
        if DEBUG:
            time.sleep(0.1)
            print("key=", keybitmap, "oldkey=", self.keybitmap_persist, "queue=", self.eventq)

        # remember key state
        self.keybitmap_persist = keybitmap




# declare

# IO
a0 = analog_input(26)
a1 = analog_input(27)
a2 = analog_input(28)
pico_led = Pin(25, Pin.OUT)  # Onboard LED is GPIO 25
# uart
uart = UART(0, baudrate=31250, bits=8, parity=None, stop=1, tx=Pin(16), rx=Pin(17))
buf = bytearray(3)
# key array
row_pin_outputs = [0, 1, 2, 3, 4, 5]
col_pin_inputs = [7, 8, 9, 10, 11, 12, 13, 19, 18]
row_outputs = [Pin(n, Pin.OUT) for n in row_pin_outputs]
col_inputs = [Pin(n, Pin.IN, Pin.PULL_DOWN) for n in col_pin_inputs]

# constants
MIDI_BUF_SIZE = 21
DEBUG = 0
VER = 2 # 8/9/2025: multi press, release events tested, works well
NOTE_OFFSET = 0x3c - 24 #3c is key 24


# global variables
vel = 0x40
scanner = key_scanner(MIDI_BUF_SIZE)


# calibrate bend
v0 = a0.readraw()
offsv0 = 64 - v0
v0 = 64
lastv0 = v0

# calibrate vel
v1 = a1.readraw()
offsv1 = 64 - v1
v1 = 64
lastv1 = v1


# set outputs on all rows
for pin in row_outputs:
    pin.value(0)

while (1):

    # get keys and generate MIDI messages for keys
    scanner.scan()
    while (len(scanner.eventq) > 0):
        evt = scanner.eventq.pop()
        if (evt & 0x80):
            buf[0], buf[1], buf[2] = 0x90, (NOTE_OFFSET + (evt & 0x7f) ), vel
        else:
            buf[0], buf[1], buf[2] = 0x90, (NOTE_OFFSET + (evt & 0x7f) ), 0
        uart.write(buf)

    # get bend and generate MIDI bend message
    v0 = a0.readraw() + offsv0
    if (v0 != lastv0):
        pitchval = v0 << 7
        buf[0], buf[1], buf[2] = 0xE0, 0, pitchval >> 8
        uart.write(buf)            
    lastv0 = v0

    # get velocity
    v1 = a1.readraw() + offsv1
    if (v1 != lastv1):
        vel = v1
    lastv1 = v1




    pico_led.toggle()


# timing
# v1:
# features
#     basic keyscan, chords
# perf
#     pulse_wid = 164us   (200us nominal)
#     cycle_tim = 3.77ms  (1.2ms nominal)
#     lat = 95ms
#
# v2:
# features:
#     PCB
#     added bend
#     added velocity
# perf:
#     pulse_wid = 181us (200us nominal)
#     cycle_tim = 3.89ms (1.2ms nominal)
#     lat = 110mx
#
#
#
#






