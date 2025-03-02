import xl9555
from machine import Pin
import utime as time
from constants import I2C0
from i2c import I2C

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
_BUFFER_SIZE = 138240

_SCL = 45
_SDA = 48
_TP_FREQ = 400000

# 定义数据引脚（GPIO编号）
DATA_PINS = [40, 39, 38, 12, 11, 10, 9, 46]

i2c_bus = I2C.Bus(host=I2C0.ID,
                scl=I2C0.SCL,
                sda=I2C0.SDA,
                freq=I2C0.FREQ)

bc = xl9555.Pin(id=_BL,i2c_bus=i2c_bus,mode=xl9555.OUT)

class I80Bus:
    def __init__(self, data_pins, wr_pin, rd_pin, dc_pin, cs_pin):
        # 配置数据引脚为输出
        self.data_pins = [Pin(pin, Pin.OUT) for pin in data_pins]
        self.wr = Pin(wr_pin, Pin.OUT, value=0)
        self.rd = Pin(rd_pin, Pin.OUT, value=0)
        self.dc = Pin(dc_pin, Pin.OUT)
        self.cs = Pin(cs_pin, Pin.OUT, value=1)# 默认禁用片选
    
    def _set_data(self, value):
        # 将8位数据写入数据线
        for i in range(8):
            self.data_pins[i].value((value >> i) & 0x01)
    
    def write_cmd(self, cmd):
        self._set_data(cmd)
        self.dc.value(0)      # DC低电平表示命令
        self.cs.value(0)       # 使能片选
        self.wr.value(0)       # 产生WR脉冲
        # time.sleep_us(1)
        self.wr.value(1)      # 上升沿
        self.cs.value(1)        # 禁用片选
    
    def write_data(self, data):
        self._set_data(data)
        self.dc.value(1)        # DC高电平表示数据
        self.cs.value(0)
        self.wr.value(0)
        # time.sleep_us(1)
        self.wr.value(1)
        self.cs.value(1)

    def read_data(self):
        self.dc.value(1)
        self.cs.value(0)
        for i in range(8):
            self.data_pins[i].init(mode=Pin.IN)
        self.rd.value(0)
        # time.sleep_us(1)
        data = 0
        for i in range(8):
            data |= self.data_pins[i].value() << i
        self.rd.value(1)
        for i in range(8):
            self.data_pins[i].init(mode=Pin.OUT)
        self.cs.value(1)
        return data

bc = xl9555.Pin(id=_BL,i2c_bus=i2c_bus,mode=xl9555.OUT)
i80 = I80Bus(DATA_PINS, _WR, _RD, _DC, _CS)

i80.write_cmd(0x01)    #Software reset
time.sleep_ms(120)

i80.write_cmd(0x36)    # Memory Access Control 
i80.write_data(0x00)

i80.write_cmd(0x3A)     # Interface Pixel Format
i80.write_data(0x65)

i80.write_cmd(0x11)    #Exit Sleep 
time.sleep_ms(120)
    
i80.write_cmd(0x29)    #Display on 

bc.high()
