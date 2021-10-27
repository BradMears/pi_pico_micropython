#!/usr/bin/env python3
'''Example of how to use PIO to control four LEDs. Demonstrates how to wrap a PIO
program as a member of a python class.'''

import time
from machine import Pin
import rp2
from rp2 import StateMachine, asm_pio

class Four_LEDs():
    '''Provides a way to feed an arbitrary length pattern to a collection
    of four LEDs or other devices. Each nibble gets passed to the four
    LEDs. The speed of the blinking is controlled by three values - the
    freq parameter to init() and the hardcoded values T and LOOPS in prog().
    By using different patterns of nibbles, you can create a variety of effects
    like a Ceylon, Knight Rider, or a countdown timer.'''
    
    def __init__(self, patterns=(0x0,), loops=1, delay_mult=5, freq=2000, out_base=None):
        self.patterns = patterns
        self.loops = loops
        self.out_base = out_base
        self.sm = rp2.StateMachine(0, self.prog, freq=freq, out_base=out_base, set_base=out_base)

        self.sm.exec(f'set(x,{delay_mult})') # set the delay multiplier
        self.count = 0
        self.sm.irq(self.ISR)
        self.sm.put(patterns[0])
        self.sm.active(1)
        
    @rp2.asm_pio(out_init=(rp2.PIO.OUT_LOW,)*4,
                 set_init=(rp2.PIO.OUT_LOW,)*4,
                 autopull=True)
    def prog():
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

    def ISR(self,sm):
        '''Interrupt service routine that feeds the next word of the pattern
        into the PIO prog.'''
        self.count += 1
        if self.loops > 0 and self.count > len(self.patterns)*self.loops:
            sm.active(0)
            sm.exec('set(pins,0x0)') # turn off all the LEDs
        else:
            self.sm.put(self.patterns[self.count%len(self.patterns)])

    def stop(self):
        '''Stops the state machine and turns off the LEDs.'''
        self.sm.active(0)
        self.sm.exec('set(pins,0x0)')

if __name__ == "__main__":
    # The following patterns show different effects you can achieve
    
    patterns = (0x01234567, 0x89abcdef, 0xf0f0f0f0)
    #patterns = (0x01234567, 0x89abcdef, 0x0f0f0f0f)
    #patterns = (0x12481248, 0x12481248, 0x12481248, 0xf0f0f0f0)
    #patterns = (0x81248124, 0x42184218)
    #patterns = (0x42184218, 0x81248124)
    #patterns = (0x42184218, 0x42184218, 0x42184218, 0x81248124, 0x81248124, 0x81248124)
    #patterns = (0x81248124, 0x81248124)
    #patterns = (0x42184218, 0x42184218)
    #patterns = (0x42184218)

    blinker = Four_LEDs(patterns=patterns, loops=3, delay_mult=1, out_base=Pin(25)) #,freq=8000)
    while blinker.sm.active():
        pass

    #blinker.stop()
    print('Finished')
