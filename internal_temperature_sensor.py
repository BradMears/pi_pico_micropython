# MicroPython
'''Encapsulates the Pi Pico's internal temperature sensor.'''

from machine import ADC

class InternalTemperatureSensor():
    '''Handles access to the internal temperature sensor on ADC(4).
    See Section 4.9.5 of https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf
    for a discussion of calculating the actual temp based on the analog reading and
    techniques to improve the accuracy of that calculation. That write-up explains
    the magic numbers used in this code.'''

    sensor_temp = ADC(4)
    conversion_factor = 3.3 / (65535)

    def __init__(self):
        pass
    
    def read(self):
        '''Returns the temperature in Celsius from the internal temperature sensor.'''
        reading = InternalTemperatureSensor.sensor_temp.read_u16() * InternalTemperatureSensor.conversion_factor 
        return 27 - (reading - 0.706)/0.001721

if __name__ == "__main__":
    internal_temp_sensor = InternalTemperatureSensor()
    for ii in range(10):
        print(f'Internal temperature = {internal_temp_sensor.read()}')
