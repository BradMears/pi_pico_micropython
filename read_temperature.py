# Micropython
'''Reads from an I2C temperature sensor and displays the results
on stdout and on an OLED board.'''

############## Hardware Configuration ############################
# This script requires the following external components
# MCP9808 temperature sensor on I2C
#
# Optional components
# SSD1306 OLED on I2C 
##################################################################
import utime
from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
from mcp9808 import MCP9808
import uos

uname = uos.uname()
if 'esp32' in uname.sysname:
    print("uC is an esp32")
    i2c_num = 0
    sda_pin = Pin(21)
    scl_pin = Pin(22)
elif 'rp2' in uname.sysname:
    print("uC is a Pi Pico")
    i2c_num = 0
    sda_pin = Pin(0)
    scl_pin = Pin(1)
else:
    print(f'Unknown board type {uname.sysname}')
    
def oled_writeln(oled, s, line_num):
    '''Writes a string to the specified line.'''
    oled.text(s, 0, line_num*8)

class MockOLED():
    '''Sends all OLED commands to /dev/null.'''
    
    def __init__(self):
        print('Using a mock OLED')
        
    def text(self, *args):
        pass
    
    def fill(self, *args):
        pass
    
    def show(self, *args):
        pass
    
    
if __name__ == "__main__":
    
    i2c = I2C(i2c_num, sda=sda_pin, scl=scl_pin, freq=400000)
    try:
        oled = SSD1306_I2C(128, 32, i2c)
    except OSError:
        oled = MockOLED() # No oled found so use a dummy
      
    # Read the temperature from the 9808
    mcp9808 = MCP9808(i2c)
    utime.sleep_ms(500)
    for ii in range(15):
        lines = []
        lines.append(f'MCP9808: {round(mcp9808.get_temp())} C')

        # send the same output to the OLED and to stdout
        oled.fill(0)
        for jj in range(len(lines)):
            print(lines[jj])
            oled_writeln(oled, lines[jj], jj)
        oled.show()
        utime.sleep_ms(500)
