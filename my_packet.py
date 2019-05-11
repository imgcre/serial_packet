from typing import *
import struct
from abc import ABCMeta, abstractmethod


@overload
def make_packet_payload_type(type_name: str, arg: Callable[[Any], bytes]) -> type: pass


@overload
def make_packet_payload_type(type_name: str, arg: str) -> type: pass


def make_packet_payload_type(type_name, arg):
    def pack(payload):
        return struct.pack(arg, payload)
    if callable(arg):
        pack = arg
    elif type(arg) is not str:
        raise TypeError('arg should be a format str or a func')
    return type(type_name, (object,), dict(pack=pack))


ushort = make_packet_payload_type('ushort', '<H')
byte = make_packet_payload_type('byte', '<B')


T = TypeVar('T')
PayloadInfo = Tuple[T, Type[T]]


class PacketMgrBase(metaclass=ABCMeta):
    def send_packet(self, packet_id: int, *args: PayloadInfo):
        data = self.build_packet(packet_id, *args)
        self.send_bytes(data)

    @abstractmethod
    def build_packet(self, packet_id: int, *args: PayloadInfo) -> bytes:
        pass

    @staticmethod
    def build_payload(*args: PayloadInfo) -> bytes:
        from io import BytesIO
        with BytesIO() as s:
            for payload, payload_type in args:
                if payload_type in (int, float):
                    s.write(struct.pack('<' + {
                        int: 'i',
                        float: 'f',
                    }[payload_type], payload))
                else:
                    s.write(payload_type.pack(payload))
            return s.getvalue()

    @abstractmethod
    def send_bytes(self, data: bytes):
        pass


class PacketSender:
    __slots__: List[Text] = ['__packet_type_id', '__func']
    __sender = Callable[..., None]
    __current_type_ids: Dict[Text, int] = {}

    @overload
    def __init__(self, packet_type_id: int = None): pass

    @overload
    def __init__(self, func: __sender): pass

    def __init__(self, arg=None):
        if arg is None or type(arg) is int:
            self.__packet_type_id = arg
            pass
        elif callable(arg):  # 这里直接确定当前的packet_id
            self.__packet_type_id = self.__get_and_inc_current_type_id(cast(Any, arg))
            self.__func = arg
        else:
            raise TypeError('arg should be a packet_type_id or a func')

    def __get__(self, instance, owner) -> __sender:  # 能执行到这里, 说明肯定是实例方法
        return lambda *args, **kwargs: self.__send_packet(instance, *args, **kwargs)

    def __call__(self, func) -> __sender:
        self.__func = func
        if self.__packet_type_id is None:
            self.__packet_type_id = self.__get_and_inc_current_type_id(func)
        else:
            self.__set_current_type_id(func, self.__packet_type_id + 1)
        return lambda *args, **kwargs: self.__send_packet(*args, **kwargs)

    def __send_packet(self, *args, **kwargs):
        import inspect
        s = inspect.signature(self.__func)
        ba = s.bind(*args, **kwargs)
        ba.apply_defaults()
        params = list(zip(ba.arguments.values(), [p.annotation for p in s.parameters.values()]))
        cast(PacketMgrBase, params[0][0]).send_packet(self.__packet_type_id, *params[1:])

    @classmethod
    def __get_and_inc_current_type_id(cls, func):
        obj_unique_prefix = cls.__get_func_unique_prefix(func)
        if obj_unique_prefix not in cls.__current_type_ids.keys():
            cls.__current_type_ids[obj_unique_prefix] = 0
        current_type_id = cls.__current_type_ids[obj_unique_prefix]
        cls.__current_type_ids[obj_unique_prefix] += 1
        return current_type_id

    @classmethod
    def __set_current_type_id(cls, func, value):
        obj_unique_prefix = cls.__get_func_unique_prefix(func)
        cls.__current_type_ids[obj_unique_prefix] = value

    @staticmethod
    def __get_func_unique_prefix(func):
        import os
        obj_unique_name = f'{func.__module__}.{func.__qualname__}'
        return os.path.splitext(obj_unique_name)[0]
