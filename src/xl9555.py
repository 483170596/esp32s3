# xl9555
import io_expander_framework
from i2c import I2C

AP_INT_IO = 0x0001
QMA_INT_IO = 0x0002
BEEP_IO = 0x0004
KEY1_IO = 0x0008
KEY0_IO = 0x0010
SPK_CTRL_IO = 0x0020
CTP_RST_IO = 0x0040
LCD_BL_IO = 0x0080
LEDR_IO = 0x0100
CTP_INT_IO = 0x0200
IO1_2 = 0x0400
IO1_3 = 0x0800
IO1_4 = 0x1000
IO1_5 = 0x2000
IO1_6 = 0x4000
IO1_7 = 0x8000

# XL9555 I2C地址
I2C_ADDR = 0x20

IN = 0x00
OUT = 0x01
LOW = 0x00
HIGH = 0x01

# 寄存器地址 (根据数据手册定义)
INPUT_PORT0 = 0x00
INPUT_PORT1 = 0x01
OUTPUT_PORT0 = 0x02
OUTPUT_PORT1 = 0x03
CONFIG_PORT0 = 0x06
CONFIG_PORT1 = 0x07

class Pin(io_expander_framework.Pin):
    def __init__(self, id, i2c_bus:I2C.Bus, mode=-1, value=None):
        self.i2c_bus = i2c_bus
        self._verify_connection()
        super().__init__(id, mode, value)
        
    def _verify_connection(self):
        """验证设备是否在线"""
        if I2C_ADDR not in self.i2c_bus.scan():
            raise OSError(f"XL9555 at 0x{I2C_ADDR:02X} not found")
    
    def _write_register(self, reg, value):
        """写入寄存器"""
        self.i2c_bus.writeto(I2C_ADDR, bytes([reg, value]))

    def _read_register(self, reg):
        """读取寄存器"""
        return self.i2c_bus.readfrom_mem(I2C_ADDR, reg, 1)[0]

    def _get_port_and_mask(self):
        """分解ID为端口号和位掩码"""
        if self._id & 0xFF:  # 低位字节有效（Port0）
            return 0, self._id & 0xFF
        else:                # 高位字节有效（Port1）
            return 1, (self._id >> 8) & 0xFF
    
    def _set_dir(self, direction):
        port, mask = self._get_port_and_mask()
        config_reg = CONFIG_PORT0 if port == 0 else CONFIG_PORT1
        
        # 读取当前配置
        current = self._read_register(config_reg)
        
        # 配置方向（1=OUT，0=IN）
        if direction == self.OUT:
            new_val = current & ~mask  # 清除位（设为输出）
        else:
            new_val = current | mask  # 设置位（设为输入）
        
        self._write_register(config_reg, new_val)

    def _set_level(self, level):

        port, mask = self._get_port_and_mask()
        output_reg = OUTPUT_PORT0 if port == 0 else OUTPUT_PORT1
        
        # 读取当前输出值
        current = self._read_register(output_reg)
        
        # 更新对应位
        if level:
            new_val = current | mask   # 设置高电平
        else:
            new_val = current & ~mask # 设置低电平
        
        self._write_register(output_reg, new_val)

    def _get_level(self):
        port, mask = self._get_port_and_mask()
        input_reg = INPUT_PORT0 if port == 0 else INPUT_PORT1
        
        # 读取输入寄存器并提取位值
        return bool(self._read_register(input_reg) & mask)