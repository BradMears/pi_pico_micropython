# Micropython
'''Demonstrates that when you have two tasks to complete, it is faster to
execute them in parallel using the two available cores rather than doing them
serially on one core. Pretty amazing, eh?

Step 1 is to execute both tasks serially and time how long they take to complete.
Step 2 is to execute them in parallel using both cores and time them. Then we print
the elapsed time for both phases as well as the ratio of serial/parallel.

It would be great if we got a speed up of 2 but we don't. I consistently get a speed-up
of about 1.92.

While we're letting both cores do their number crunching, we also use a PWM block to
blink the built-in LED. This is just there to remind us that the Pico can do a number
of independent things simultaneously, which is very useful.'''

import utime
import _thread
from machine import PWM, Pin, WDT

#wdt = machine.WDT(0, 12000)
led = PWM(Pin(25, Pin.OUT))
led.duty_u16(10000)
led.freq(10)

class NumberCruncher():
    '''Provides a method that can be called singlethreaded or multi-threaded so
    we can compare performance using one core vs two cores.'''
    
    def __init__(self, id):
        self.id = id
        self.running = True
        self.result = 0.0
        
    def calculate(self, count):
        '''Does some meaningless number crunching and stores the result in self.result.'''
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
    cruncher2 = NumberCruncher(2)
    X = 500000
    print('X = ', X)

    # Run the two number crunching routines serially and time how long
    # it takes to complete them.
    t1 = utime.ticks_ms()
    cruncher1.calculate(X)
    cruncher2.calculate(X)
    while cruncher1.running or cruncher2.running:
        pass
    serial_duration = utime.ticks_ms() - t1
    assert(cruncher1.result, cruncher2.result)

    # Run the two number crunching routines in parallel and time how long
    # it takes to complete them. Hopefully this will take less time than
    # it did in serial.
    t1 = utime.ticks_ms()
    _thread.start_new_thread(cruncher1.calculate, (X,))
    cruncher2.calculate(X)
    
    while cruncher1.running or cruncher2.running:
        pass
    parallel_duration = utime.ticks_ms() - t1
    assert(cruncher1.result, cruncher2.result)

    print("Time elapsed in serial phase = ", serial_duration)
    print("Time elapsed in parallel phase = ", parallel_duration)
    print("Ratio of serial to parallel = ", serial_duration/parallel_duration)
    led.duty_u16(0)
