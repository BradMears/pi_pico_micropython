# Micropython
'''Creates 50% duty cycle square waves using PWM and PIO. You can hook these up to an LED if you
want but my purpose is to use an oscilloscope to compare the quality of the waves produced
by the two different techniques.'''

import time
from machine import Pin, PWM
from rp2 import PIO, StateMachine, asm_pio

@asm_pio(set_init=PIO.OUT_LOW)
def square():
    wrap_target()
    set(pins, 1)
    set(pins, 0)
    wrap()

# This value controls the frequency of both approaches
freq=4000

# Use PWM to create a square wave
pwm_pin = PWM(Pin(0))

pwm_pin.freq(freq)
pwm_pin.duty_u16(32767)   

# Use PIO to create a square wave
sm = rp2.StateMachine(0, square, freq=freq*2, set_base=Pin(15))
sm.active(1)

