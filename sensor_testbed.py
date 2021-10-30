from machine import ADC
from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
import utime
import dht11_pio 
from internal_temperature_sensor import InternalTemperatureSensor
#from mcp9808 import MCP9808

def map_value(in_v, in_min, in_max, out_min, out_max):           # (3)
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

def oled_writeln(oled, s, line_num):
    oled.text(s, 0, line_num*8)
    
    
if __name__ == "__main__":
    
    i2c=I2C(0,sda=Pin(0), scl=Pin(1), freq=400000)
    oled = SSD1306_I2C(128, 32, i2c)
    
    # Read the temperature from three different sensors
    # None of these are particularly accurate so don't expect them to match
    internal_temp_sensor = InternalTemperatureSensor()
    tmp36 = TMP36_TemperatureSensor(0) # TMP36 IC on ADC0
    dht11 = dht11_pio.DHT11_PIO(15, 1)
    utime.sleep_ms(500)
    for ii in range(5):
        print(f'tmp36 reading = {round(tmp36.read())}')
        print(f'Internal temperature = {round(internal_temp_sensor.read())}')
        humidity, temperature = dht11.read()
        utime.sleep_ms(500)
        oled.fill(0)
        oled_writeln(oled, f'TMP36: {round(tmp36.read())} C', 0)
        oled_writeln(oled, f'Pico: {round(internal_temp_sensor.read())} C', 1)
        oled_writeln(oled, f'DHT11: {temperature} C',2)
        oled_writeln(oled, f'DHT11: {humidity}%',3)
        oled.show()
    dht11.deinit()


    '''
    i2c1 = I2C(1, scl=Pin(11), sda=Pin(10), freq=10000)
    time.sleep(0.1)
    i2c_devices = i2c1.scan()
    for device in i2c_devices:
        print(device, hex(device))

    mcp9808 = MCP9808(i2c1)
    time.sleep(0.2)
    mcp9808._debug_config()
    print(mcp9808.get_temp())
    '''
