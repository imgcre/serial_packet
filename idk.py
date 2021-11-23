from my_packet import *
from enum import IntEnum, unique

VERSION = (0x00, byte)

@unique
class Target(IntEnum):
    N = 0x00
    F = 0x01
    I = 0x02
    C = 0x03
    S = 0x04
    B = 0x05

class MySerialPacketMgr(PacketMgrBase):
    def __init__(self):
        pass

    @PacketSender((Target.N, 0x00))
    def test(self): pass

    @PacketSender((Target.N, 0x01))
    def device_type(self): pass

    @PacketSender((Target.N, 0x02))
    def device_seq(self): pass

    @PacketSender((Target.N, 0x10))
    def read_rtc(self): pass

    @PacketSender((Target.N, 0x11))
    def set_rtc(self, *, h: byte, m: byte, s: byte, Y: byte, M: byte, D: byte, W: byte): pass

    @PacketSender((Target.N, 0xfe))
    def reset(self): pass

    @PacketSender((Target.N, 0xff))
    def echo(self, data: bytes): pass

    @PacketSender((Target.F, 0x00))
    def flash_test_conn(self): pass

    @PacketSender((Target.F, 0x01))
    def flash_type(self): pass

    @PacketSender((Target.F, 0x02))
    def flash_seq(self): pass

    @PacketSender((Target.F, 0x10))
    def flash_read_single(self, addr: uint): pass

    @PacketSender((Target.F, 0x11))
    def flash_write_single(self, addr: uint, data: byte): pass

    @PacketSender((Target.F, 0x12))
    def flash_read_page(self, addr: uint, len: uint): pass

    @PacketSender((Target.I, 0x13))
    def eeprom_write_burst(self, addr: uint, data: p32bytes): pass

    def build_packet(self, packet_id, *args):
        from io import BytesIO
        HEADER = (0x4e, byte)
        TARGET = (packet_id[0], byte)
        ACTION =  (packet_id[1], byte)
        TAIL = (0x45, byte)
        CRC = (0xffffffff, uint)
        with BytesIO() as s:
            s.write(self.build_payload(HEADER, VERSION, TARGET, ACTION))
            data = self.build_payload(*args)
            data_len = len(data)
            s.write(self.build_payload((data_len, byte)))
            s.write(data)
            s.write(self.build_payload(TAIL, CRC))
            return s.getvalue()

    def send_bytes(self, data):
        print(data.hex(' '))


c = MySerialPacketMgr()

# c.set_rtc(h=0x12, m=0x34, s=0x56, Y=0x78, M=0x9a, D=0xbc, W=0xde)
# c.echo(b'ABC')
# c.flash_read_single(0)
# c.flash_write_single(0, 0xff)