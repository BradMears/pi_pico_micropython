# Micropython
# Sample code that illustrates how to use some of the hardware features of
# the Raspberry Pi Pico with MicroPython. Rather than write a separate script
# for each feature, we use one larger script to show different features operating
# together. The intent is to provide a realistic example of how to use the
# interesting features of the Pi Pico.

############## Hardware Configuration ############################
# To visualize what this script is doing and allow it to to work
# correctly, you need to add some LEDs, resistors, and jumper wires.
#
# The PIO demonstration uses the built-in LED on GPIO 25 as well as external LEDs
# attached to GPIO pins 26, 27, and 28, You will need to add an LED and resistor
# going from each of those pins to ground.
#
# The PWM demonstration uses GPIO pin 16. You will need to add an LED and resistor
# from there to ground.
#
# The UART demonstration sets up a connection between UART0 and UART1. You will
# need to add one jumper wire from GPIO0 to GPIO5 and another from GPIO1 to GPIO4.
#
############## Software Configuration ############################
# The following variables control how the program operates. You can
# comment/uncomment these flags to see how different features work
#
# Set this flag to True to enable the Watchdog Timer as described in
# https://docs.micropython.org/en/latest/library/machine.WDT.html
ENABLE_THE_WATCHDOG_TIMER = False
#ENABLE_THE_WATCHDOG_TIMER = True

# Set this flag to true to let the asynchronouse hardware features
# like the WDT, timers, PWM, and PIO to keep running when the script ends.
BACKGROUND_TASKS_STAY_ACTIVE = False
#BACKGROUND_TASKS_STAY_ACTIVE = True

# A word of warning - If you set ENABLE_THE_WATCHDOG_TIMER to True and
# set BACKGROUND_TASKS_STAY_ACTIVE to False, then the timer that feeds
# the keep-alive signal to the WDT will be stopped. That means that the
# WDT will trigger shortly afterwards. This is exactly the purpose of
# the WDT but may seem surprising the first time you see it happen.
#
################ End of Configuration and instructions ##############

import time
import machine
from machine import Pin, I2C, Timer, PWM, UART
from pio_Four_LEDs import Four_LEDs
from internal_temperature_sensor import InternalTemperatureSensor

internal_temp_sensor = InternalTemperatureSensor()

# Use PIO to drive four LEDs in an entertaining pattern
patterns = (0x42184218, 0x81248124, 0xf0f0f0f0)
blinker = Four_LEDs(patterns=patterns, loops=0, out_base=Pin(25))

# This is how you can set a watchdog timer and a keep-alive to
# go with it. If you stop the keep-alive timer, then the board will
# shut down, forcing you to reconnect. There is no way to turn off the
# watchdog once it is set so if you ever stop tmr2 (the keep-alive), then
# the WDT will expire and bring everything to a sudden halt.
# For this sample, the watchdog will shut everything down if it doesn't
# receive a keep-alive every two seconds. We use a hardware timer to feed
# it that message every one second.
if ENABLE_THE_WATCHDOG_TIMER:
    wdt = machine.WDT(0, 2000)
    tmr2 = Timer(freq=1, mode=Timer.PERIODIC, callback=lambda t:wdt.feed())
else:
    tmr2 = None 
    
# Set a periodic timer using the hardware timer
tmr1 = Timer(freq=0.5, mode=Timer.PERIODIC, callback=lambda t:print('Timer tick'))

print(f'CPU frequency = {machine.freq()/1e6} MHz')

# Turn on a PWM pin. This can be hooked to a LED or you could look at it with
# an oscilloscope.
pwm = PWM(Pin(16))      # create a PWM object on a pin
pwm.duty_u16(32768)     # set duty to 50%

# The Pico has a built-in RTC which will keep track of time once you set it.
# That leaves the question of how you get the current time to set it to.
# It retains the current time as long as power is applied so you only have
# to do an explicit set if you lose power.
rtc = machine.RTC()
#rtc.datetime((2021, 10, 25, 2, 10, 32, 36, 0))

# The pico has two hardware UARTs. We're going to hook them to each
# other and transmit a message both ways. This is just a complicated
# way to talk to yourself but it shows the UARTs in action

uart0 = UART(0, 256000, tx=Pin(0), rx=Pin(1))
uart1 = UART(1, 256000, tx=Pin(4), rx=Pin(5))

msg_0_to_1 = "Come in 1. This is 0."
msg_1_to_0 = "Come in 0. This is 1."
uart0.write(msg_0_to_1)
uart1.write(msg_1_to_0)
time.sleep(0.1) # wait a little time for the bits to move down the wire
rcvd_1 = uart1.readline()
rcvd_0 = uart0.readline()
assert(bytearray(msg_0_to_1) in rcvd_1)
assert(bytearray(msg_1_to_0) in rcvd_0)
if (bytearray(msg_0_to_1) in rcvd_1) and (bytearray(msg_1_to_0) in rcvd_0):
    print("Bi-directional comms between UART0 & UART1 succeeded")

# Print the time from the RTC and the internal temperature. This
# also increases the brightness of the LED in steps
for ii in range (10):
    pwm.duty_u16((ii+1)*6553)
    internal_temp = internal_temp_sensor.read()
    print(rtc.datetime(), internal_temp)
    time.sleep(1)

# Set the LED to a dimmer value
pwm.duty_u16(10000)

### If you don't stop the asynchronous activities, that's okay. Those
### background activities (timer, PWM, PIO) will keep running. That
### could come in handy for some applications,
if not BACKGROUND_TASKS_STAY_ACTIVE:
    # PWM.deinit() should be sufficient to turn off the LED but it isn't.
    # It appears that there is a bug that if you try to deinit() while in the
    # middle of a pulse, it won't shut off. So set the duty cycle to zero
    # and then pause for a moment to let the current pulse end. Instead of
    # calling sleep(), you can also go do other stuff and then call pwm.deinit()
    # when that work completes.
    pwm.duty_u16(0)
    #time.sleep(0.001) # Let the current pulse end before calling deinit()
    #pwm.deinit()      # Kill the PWM-controlled LED

    blinker.stop()     # Disable the PIO blinker
    if tmr1: tmr1.deinit()   
    if tmr2: tmr2.deinit()   
    pwm.deinit()       # Kill the PWM-controlled LED

print('Program ended gracefully')
