import struct


class BaseField(object):
    STRUCTURE = ""

    name = None

    def __init__(self, name=None):
        self.name = name

    def encode(self, buf, val):
        buf.write(struct.pack(self.STRUCTURE, val))

    def decode(self, buf):
        return struct.unpack(self.STRUCTURE, buf.read(struct.calcsize(self.STRUCTURE)))[0]

    def get_name(self):
        return self.name
