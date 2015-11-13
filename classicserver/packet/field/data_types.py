from classicserver.packet.field.field import BaseField


class ByteField(BaseField):
    STRUCTURE = "!B"


class SignedByteField(BaseField):
    STRUCTURE = "!b"


class ShortField(BaseField):
    STRUCTURE = "!h"


class StringField(BaseField):
    def decode(self, buf):
        return buf.read(64).decode("ascii").rstrip()

    def encode(self, buf, val):
        raw = val.encode("ascii")
        raw = raw[:64]  # Trim
        pad = 64 - len(val)
        raw += (pad * b" ")
        buf.write(raw)


class ByteArrayField(BaseField):
    def decode(self, buf):
        return buf.read(1024)

    def encode(self, buf, val):
        val = val[:1024]
        pad = 1024 - len(val)
        val += (b"\0" * pad)
        buf.write(val)
