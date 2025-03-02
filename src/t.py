import lcd_bus
import xl9555
from machine import Pin
from constants import I2C0
from i2c import I2C
import utime

_WIDTH = 320
_HEIGHT = 240
_BL = xl9555.LCD_BL_IO
_CS = 1
_DC = 2
_RD = 41
_WR = 42
_FREQ = 10000000
_DATA0 = 40
_DATA1 = 39
_DATA2 = 38
_DATA3 = 12
_DATA4 = 11
_DATA5 = 10
_DATA6 = 9
_DATA7 = 46
_BUFFER_SIZE = 320*240*2

rd = Pin(_RD, Pin.OUT, value=0)

i2c_bus = I2C.Bus(host=I2C0.ID,
                scl=I2C0.SCL,
                sda=I2C0.SDA,
                freq=I2C0.FREQ)
bc = xl9555.Pin(id=_BL,i2c_bus=i2c_bus,mode=xl9555.OUT,value=0)

i80_bus = lcd_bus.I80Bus(
    dc=_DC,
    wr=_WR,
    cs=_CS,
    freq=_FREQ,
    data0=_DATA0,
    data1=_DATA1,
    data2=_DATA2,
    data3=_DATA3,
    data4=_DATA4,
    data5=_DATA5,
    data6=_DATA6,
    data7=_DATA7
)

i80_bus.init(
    _WIDTH,
    _HEIGHT,
    16,
    _BUFFER_SIZE,
    True,
    8,
    8
)

i80_bus.tx_param(0x01) #Software reset
utime.sleep_ms(120)
i80_bus.tx_param(0x11) #Exit Sleep 
utime.sleep_ms(120)
i80_bus.tx_param(0x36,bytearray([0x00]))  # Memory Access Control 0
i80_bus.tx_param(0x3A,bytearray([0x65])) # Interface Pixel Format
# 
i80_bus.tx_param(0x21) #Display Inversion On

i80_bus.tx_param(0x29)  #Display on 
utime.sleep_ms(120)
i80_bus.tx_param(0x2A,bytearray([0x00,0x00,0x01,0x3F])) #Column Address Set
i80_bus.tx_param(0x2B,bytearray([0x00,0x00,0x00,0xEF])) #Page Address Set
i80_bus.tx_param(0x2C) #Memory Write
bc.value(1) #Backlight on
