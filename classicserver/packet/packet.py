from classicserver.packet.field.data_types import ByteField


class BasePacket(object):
    ID = None

    def encode(self, buf, values):
        pass

    def decode(self, buf):
        pass


class Packet(BasePacket):
    ID = -1

    FIELDS = []

    def encode(self, buf, values):
        ByteField().encode(buf, self.ID)
        for field in self.FIELDS:
            field.encode(buf, values[field.get_name()])

    def decode(self, buf):
        if (ByteField().decode(buf) != self.ID) and not (self.ID == -1):
            raise ValueError("Invalid packet ID")

        values = {}
        for field in self.FIELDS:
            values[field.get_name()] = field.decode(buf)

        return values
