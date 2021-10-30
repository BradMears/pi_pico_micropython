from machine import ADC

def map_value(in_v, in_min, in_max, out_min, out_max):
    """Helper method to map an input value (v_in)
       between alternative max/min ranges."""
     
    v = (in_v - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
    if v < out_min:
        v = out_min
    elif v > out_max:
        v = out_max
    return v

class TMP36_TemperatureSensor():
    '''Handles access to a TMP36 IC temperature sensor on an analog pin.
    See https://learn.adafruit.com/tmp36-temperature-sensor for a discussion of
    calculating the actual temp based on the analog reading. That write-up explains
    the magic numbers used in this code.'''

    def __init__(self, pin):
        self.sensor = ADC(pin)
        self.max_analog_value = 65535  # The pico analog readings use all 16 bits
        self.analog_ref = 3.3  # Should probably measure this with a voltmeter
    
    def read(self):
        '''Returns the temperature in Celsius from the internal temperature sensor.'''
        reading = self.sensor.read_u16()
        reading = map_value(reading, 0, self.max_analog_value, 0, self.analog_ref*1000)
        return (reading - 500) / 10.0  #[(Vout in mV) - 500] / 10

