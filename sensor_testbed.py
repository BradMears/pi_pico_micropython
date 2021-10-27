#from mcp9808 import MCP9808
#import dht
'''
dht11 = dht.DHT11(machine.Pin(4))
for ii in range(10):
    print(f'DHT11: {d.measure()}, {d.temperature()}, d.humidity()')
'''

    
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
