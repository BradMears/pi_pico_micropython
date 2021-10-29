# Micropython
'''Illustrates the use of two cores on the Pico. It uses core0 to toggle an LED and core1
is used for some number crunching.

At the time this code was written, the _thread module is described as 'experimental' and my
tests uncovered some weird behavior.
For example, if you do any moderately complex math on core1, it will trigger random freezes
and crashes. Something as simple as overflowing an integer can do it. So until that library
matures, it is best to use core1 for fairly simple operations.

Using the WatchDog Timer is a good way to defend against core1 going off in the weeds. Without
it, you'll need to physically unplug the Pico and then plug it back in. With the WDT, you just
have to hit the reconnect button to reset everything.

Note about realism: All we're doing in core0 is toggling an LED and that is something we
could do with PWM very easily. So in a more complex example, we could do number crunching
on both cores and use PWM to blink the LED for us. 
Oh yeah! That's exactly what we do in multicore_timing.py. :)
'''

import utime
import _thread
from machine import Pin, WDT

#wdt = WDT(0, 5000)
led = Pin(25, Pin.OUT)

class NumberCruncher():
    '''Provides a method that can be called singlethreaded or multi-threaded so
    we can compare performance using one core vs two cores.'''
    
    def __init__(self, id):
        self.id = id
        self.running = True
        self.result = 0.0
        
    def calculate(self, count):
        self.running = True
        self.result = 1
        for ii in range(1,count):
            #wdt.feed()
            # The following math just burns cycles. There's no other point to it.
            # We have to be careful to not get any arithmetic overflow so we don't
            # send core1 spiraling out of control.
            if ii % 2:
                self.result += ii % 3
            else:
                self.result -= ii % 5
        self.running = False


if __name__ == "__main__":
    cruncher1 = NumberCruncher(1)
    X = 100000
    print('X = ', X)

    t1 = utime.ticks_ms()
    _thread.start_new_thread(cruncher1.calculate, (X,))    
    while cruncher1.running:
        led.toggle()
        utime.sleep_ms(100)
        
    t2 = utime.ticks_ms()
    led.off()
    
    print(f"Results from cruncher1: {cruncher1.result}\tElapsed time = {t2 - t1} ms")
