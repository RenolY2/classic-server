from classicserver.packet.buffer import WriteBuffer
from classicserver.packet.packets import *


def from_buffer(buf, to_server):
    packets = CLIENT_TO_SERVER if to_server else SERVER_TO_CLIENT
    packet_id = ord(buf.read(1, False))

    if packet_id in packets:
        packet = packets[packet_id]
        fields = packet().decode(buf)
        return packet, fields
    else:
        raise ValueError("Invalid packet ID")


def make_packet(packet, values):
    buf = WriteBuffer()
    packet().encode(buf, values)
    return buf.get_buffer()
