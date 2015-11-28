"""
    classic-server - A basic Minecraft Classic server.
    Copyright (C) 2015  SopaXorzTaker

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from classicserver.packet.buffer import WriteBuffer
from classicserver.packet.field.data_types import ByteField, StringField, ShortField, SignedByteField, ByteArrayField


class Packet(object):
    ID = -1

    FIELDS = []

    def encode(self, buf, values):
        """
        Encodes a packet to a WriteBuffer.

        :param buf: A packet.buffer.Buffer object to which the packet is encoded.
        :type buf: WriteBuffer
        :param values: Field values for encoding
        :type values: dict
        """
        ByteField().encode(buf, self.ID)
        for field in self.FIELDS:
            field.encode(buf, values[field.get_name()])

    def decode(self, buf):
        """
        Decodes a packet from a ReadBuffer
        :param buf: A ReadBuffer object to decode the packet from.
        :type buf: ReadBuffer
        :return: The decoded field values
        :rtype: dict
        """
        if (ByteField().decode(buf) != self.ID) and not (self.ID == -1):
            raise ValueError("Invalid packet ID")

        values = {}
        for field in self.FIELDS:
            values[field.get_name()] = field.decode(buf)

        return values

    @staticmethod
    def from_buffer(buf, to_server):
        """
        Decodes the packet from a ReadBuffer
        :param buf: A ReadBuffer-like object to decode the packet from.
        :type buf: ReadBuffer
        :param to_server: Specifies which packet set to use.
        :type to_server: bool
        :return: The decoded fields.
        :rtype: dict
        """
        packets = CLIENT_TO_SERVER if to_server else SERVER_TO_CLIENT
        packet_id = ord(buf.read(1, False))

        if packet_id in packets:
            packet = packets[packet_id]
            fields = packet().decode(buf)
            return packet, fields
        else:
            raise ValueError("Invalid packet ID")

    @classmethod
    def make(cls, values=None):
        """
        Makes a Python buffer with the encoded packet.
        :param values: The field values to use.
        :type values: dict
        :return: The buffer with the encoded packet.
        :rtype: buffer
        """

        if not values:
            values = {}

        buf = WriteBuffer()
        cls().encode(buf, values)
        return buf.get_buffer()


class PlayerIdentificationPacket(Packet):
    ID = 0x00
    FIELDS = [ByteField("protocol_version"), StringField("username"), StringField("key"), ByteField("reserved")]


class SetBlockPacket(Packet):
    ID = 0x05
    FIELDS = [ShortField("x"), ShortField("y"), ShortField("z"), ByteField("mode"), ByteField("block_type")]


class PositionAndOrientationPacket(Packet):
    ID = 0x08
    FIELDS = [SignedByteField("player_id"), ShortField("frac_x"), ShortField("frac_y"), ShortField("frac_z"),
              ByteField("yaw"), ByteField("pitch")]


class MessagePacket(Packet):
    ID = 0x0d
    FIELDS = [ByteField("player_id"), StringField("message")]


class ServerIdentificationPacket(Packet):
    ID = 0x00
    FIELDS = [ByteField("protocol_version"), StringField("server_name"), StringField("server_motd"),
              ByteField("user_type")]


class PingPacket(Packet):
    ID = 0x01


class LevelInitializePacket(Packet):
    ID = 0x02


class LevelDataChunkPacket(Packet):
    ID = 0x03
    FIELDS = [ShortField("chunk_length"), ByteArrayField("chunk"), ByteField("percent")]


class LevelFinalizePacket(Packet):
    ID = 0x04
    FIELDS = [ShortField("x"), ShortField("y"), ShortField("z")]


class BlockUpdatePacket(Packet):
    ID = 0x06
    FIELDS = [ShortField("x"), ShortField("y"), ShortField("z"), ByteField("block_type")]


class SpawnPlayerPacket(Packet):
    ID = 0x07
    FIELDS = [SignedByteField("player_id"), StringField("username"), ShortField("x"), ShortField("y"), ShortField("z"),
              ByteField("yaw"), ByteField("pitch")]


class DespawnPlayerPacket(Packet):
    ID = 0x0c
    FIELDS = [ByteField("player_id")]


class DisconnectPlayerPacket(Packet):
    ID = 0x0e
    FIELDS = [StringField("reason")]


class UpdateUserTypePacket(Packet):
    ID = 0x0f
    FIELDS = [ByteField("user_type")]


CLIENT_TO_SERVER = {
    0x00: PlayerIdentificationPacket,
    0x05: SetBlockPacket,
    0x08: PositionAndOrientationPacket,
    0x0d: MessagePacket
}
SERVER_TO_CLIENT = {
    0x00: ServerIdentificationPacket,
    0x01: PingPacket,
    0x02: LevelInitializePacket,
    0x03: LevelDataChunkPacket,
    0x04: LevelFinalizePacket,
    0x06: BlockUpdatePacket,
    0x07: SpawnPlayerPacket,

    0x0c: DespawnPlayerPacket,
    0x0d: MessagePacket,
    0x0e: DisconnectPlayerPacket,
    0x0f: UpdateUserTypePacket
}
