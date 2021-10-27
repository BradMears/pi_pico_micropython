# Micropython
'''Demonstrates basic use of PIO to blink four LEDs. The pattern of the blink is
defined by a tuple or list of 32 bit words.'''
import time
from rp2 import StateMachine, asm_pio
from machine import Pin

@rp2.asm_pio(out_init=(rp2.PIO.OUT_LOW,)*4,
             set_init=(rp2.PIO.OUT_LOW,)*4,
             autopull=True)
def blinky():
    '''PIO routine that runs 4 LEDs through a specified pattern. Before invoking, set
    the x register to the delay factor to use between nibbles.'''
    label("next_nibble")
    out(pins, 4)
    
    T = 31
    mov(y,x)
    label("delay_loop")
    nop()         [T]
    jmp(y_dec, "delay_loop")
    jmp(not_osre, "next_nibble")
    irq(0)  # Tell the ISR that we need our next value
    jmp("next_nibble")

def monitor(sm):
    '''Interrupt Service Routine that feeds the next word of patterns to
    the state machine.'''
    global count
    global patterns

    count += 1
    if count > len(patterns)*loops:
        sm.active(0)
        sm.exec('set(pins,0x0)') # turn off all the LEDs
    else:
        sm.put(patterns[count%len(patterns)])

if __name__ == "__main__":
    patterns = [0x42184218]
    patterns = [0x0f0f0f0f]
    patterns = [0x01020408]
    patterns = [0xf1f2f4f8]
    patterns = [0x6a0f0f0f]
    patterns = [0x01234567, 0x89abcdef, 0x0e0e0e0e]
    patterns = [0x12481248, 0x12481248, 0x12481248, 0xf0f0f0f0]
    count = 0
    loops = 2

    sm = rp2.StateMachine(0, blinky, freq=2000, out_base=Pin(25), set_base=Pin(25))
    sm.exec('set(x,5)') # set the delay multiplier
    sm.irq(monitor)
    monitor(sm)
    sm.active(1)
    while (sm.active()):
        pass

print('Finished')
