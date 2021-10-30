# Micropython
'''Reads from a variety of temperature sensors and displays the results on stdout
and on an OLED board.'''

############## Hardware Configuration ############################
# This script requires the following external components
# SSD1306 on I2C 0 (GP0 & GP1)
# MCP9808 on I2C 0 (GP0 & GP1)
# DHT11 on GP15
# TMP36 on ADC0
# It also makes use of the Pico's internal temp sensor on ADC3
##################################################################
import utime
from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
import dht11_pio 
from internal_temperature_sensor import InternalTemperatureSensor
from TMP36_Sensor import TMP36_TemperatureSensor
from mcp9808 import MCP9808

def oled_writeln(oled, s, line_num):
    '''Writes a string to the specified line.'''
    oled.text(s, 0, line_num*8)
        
if __name__ == "__main__":
    
    i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
    oled = SSD1306_I2C(128, 32, i2c)
 
    # Read the temperature from four different sensors
    # Some of these are pretty inaccurate so don't expect them to match
    mcp9808 = MCP9808(i2c)
    internal_temp_sensor = InternalTemperatureSensor()
    tmp36 = TMP36_TemperatureSensor(0) # TMP36 IC on ADC0
    dht11 = dht11_pio.DHT11_PIO(15, 1)
    utime.sleep_ms(500)
    for ii in range(5):
        lines = []
        lines.append(f'MCP9808: {round(mcp9808.get_temp())} C')
        lines.append(f'TMP36  : {round(tmp36.read())} C')
        lines.append(f'Pico   : {round(internal_temp_sensor.read())} C')
        humidity, temperature = dht11.read()
        lines.append(f'DHT11: {temperature} C {humidity}%')

        oled.fill(0)
        for jj in range(len(lines)):
            print(lines[jj])
            oled_writeln(oled, lines[jj], jj)
        print()
        oled.show()
        utime.sleep_ms(500)
        
    dht11.deinit()
