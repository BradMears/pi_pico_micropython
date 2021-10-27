import time
from rp2 import StateMachine, asm_pio
from machine import Pin

        
@rp2.asm_pio(out_init=(rp2.PIO.OUT_LOW,)*4)
def blinky():
    '''PIO routine that runs 4 LEDs through a specified pattern.'''
    label("refill")
    pull()
    mov(x, osr)
    mov(osr, x)
    irq(0)  # Tell the ISR that we need our next value

    label("next_nibble")
    out(pins, 4)
    
    set(y, 5)
    label("delay_loop")
    nop()         [31]    ####[self.T]
    jmp(y_dec, "delay_loop")
    
    jmp(not_osre, "next_nibble")
    jmp("refill")

count = 0
patterns = [0x01234567, 0x89abcdef, 0xf0f0f0f0]
#patterns = [0x12481248, 0x12481248, 0x12481248, 0xf0f0f0f0]
#patterns = [0x42184218]
loops = 2
#terminating = False

def monitor(sm):
    global count
    global patterns
        
    count += 1
    if count >= len(patterns)*loops:
        '''
        sm.put(0x0)
        time.sleep(1)
        sm.active(0)
        '''
        sm.active(0)
        sm.put(0x0)
        sm.active(1)
        time.sleep(1)
        sm.active(0)
    else:
        sm.put(patterns[count%len(patterns)])

'''
def ISR(sm):
    self.count += 1
    if self.count >= len(self.patterns)*loops:
        self.sm.active(0)
    else:
        self.sm.put(self.patterns[self.count%len(self.patterns)])
'''

class Pattern_4():
    '''Provides a mechanism to trigger four outputs using a
       repeating pattern.'''
    
    def __init__(self):
        self.count = 0
        #self.patterns = [0x01234567, 0x89abcdef, 0xf0f0f0f0]
        #self.patterns = [0x12481248, 0x12481248, 0x12481248, 0xf0f0f0f0]
        self.patterns = [0x42184218]
        self.loops = 2
        self.T = 31
        self.sm = rp2.StateMachine(0, blinky, freq=2000, out_base=Pin(25))
        self.sm.irq(monitor)
        monitor(self.sm)
    
    def start(self):
        self.sm.active(1)

    def stop(self):
        self.sm.active(1)


if __name__ == "__main__":
 
    blinker = Pattern_4()
    blinker.start()
    while (blinker.sm.active()):
        pass
        #time.sleep(0.01)

    '''
    sm.active(0)
    patterns = [0x0, 0x0]
    patterns = [0x0]
    loops = 2
    count = 0
    monitor(sm)
    sm.active(1)
    while (sm.active()):
        pass
    '''
    
    
    print('Finished')
