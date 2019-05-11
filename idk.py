from my_packet import *


class MySerialPacketMgr(PacketMgrBase):
    def __init__(self):
        pass

    @PacketSender(0x59)
    def set_general(self, *, dist: ushort = 0, strength: ushort = 0, temp: ushort = 0): pass

    @PacketSender
    def set_params(self, a: float, b: float): pass

    @PacketSender()
    def switch_to_fit_mode(self): pass

    @PacketSender
    def switch_to_default_mode(self): pass

    def build_packet(self, packet_id, *args):
        from io import BytesIO
        with BytesIO() as s:
            s.write(self.build_payload((0x59, byte), (packet_id, byte), *args))
            data = s.getvalue()
            checksum = 0
            for b in data:
                checksum += b
            checksum %= 0x100
            s.write(self.build_payload((checksum, byte)))
            return s.getvalue()

    def send_bytes(self, data):
        print(data.hex())


c = MySerialPacketMgr()
