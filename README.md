# key49
Micropython app running on a raspberry pi pico to turn a junked 49-key keyboard into a MIDI input device

# keycode scancode vs. keycode
keycodes = [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48]  
scancodes= [ 4,51,42,33,24,15, 6,53,44,35,26,17, 8,45,36,27,18, 9, 0,46,37,28,19,10, 1,48,39,30,21,12, 3,50,41,32,23,14, 5,52,43,34,25,16, 7,47,38,29,20,11, 2]

# keycode vs. scancode
scancodes= [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53]  
keycodes = [18,24,48,30  0,36, 6,42,12,17,23,47,29,   35, 5 41,11,16,22,46,18,  ,34, 4,40,10,15,21,45,27,  ,33, 3,39, 9,14,20,44,26,  ,32, 2,38, 8,13,19,43,25,  ,31, 1,37, 7


basic features:
-49-key grid scanning (6 output vs. 9 input)
-slider pots for bend and velocity value

shortcomings:
-No velocity
