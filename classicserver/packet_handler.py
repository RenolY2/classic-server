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

import hashlib

from classicserver.packet.buffer import ReadBuffer
from classicserver.packet.packet import *
from classicserver.world import *


class PacketHandler(object):
    _server = None

    def __init__(self, server):
        """

        :type server: ClassicServer
        """
        self._server = server

    def handle_packet(self, connection, data):
        buf = ReadBuffer(data)

        while buf.left() > 0:
            try:
                packet, fields = Packet.from_buffer(buf, True)
            except BaseException as e:
                print("Unable to decode packets: %s" % repr(e))
                break

            if packet == PlayerIdentificationPacket:
                if fields["key"] == hashlib.md5((fields["username"] + self._server.get_salt()).encode("utf-8")) \
                        .digest():
                    print("[INFO] Player %s is verified" % fields["username"])
                else:
                    print("[INFO] Unable to verify player %s" % fields["username"])

                sendbuf = ServerIdentificationPacket.make({
                    "protocol_version": 7,
                    "server_name": self._server.get_name(),
                    "server_motd": self._server.get_motd(),
                    "user_type": 0x64 if self._server.is_op(fields["username"]) else 0x00
                })

                chunk = self._server.get_world().encode()
                parts = [chunk[i: i + 1024] for i in range(0, len(chunk), 1024)]

                sendbuf += LevelInitializePacket.make()

                for count, part in enumerate(parts):
                    sendbuf += LevelDataChunkPacket.make({
                        "chunk_length": len(part),
                        "chunk": part,
                        "percent": int((100 / len(parts)) * count)
                    })

                sendbuf += LevelFinalizePacket.make({
                    "x": WORLD_WIDTH,
                    "y": WORLD_HEIGHT,
                    "z": WORLD_DEPTH
                })

                connection.send(sendbuf)

                username = fields["username"]
                player_id = self._server.add_player(connection, None, username)
                print("[SERVER] Player %s has joined with ID=%d!" % (username, player_id))
                player = self._server.get_player(player_id)

                connection.send(PositionAndOrientationPacket.make({
                    "player_id": -1,
                    "frac_x": int(player.coordinates[0] * 32),
                    "frac_y": int(player.coordinates[1] * 32),
                    "frac_z": int(player.coordinates[2] * 32),
                    "yaw": 0,
                    "pitch": 0
                }))

                self._server.broadcast(SpawnPlayerPacket.make({
                    "player_id": player.player_id,
                    "username": player.name,
                    "x": int(player.coordinates[0]),
                    "y": int(player.coordinates[1]),
                    "z": int(player.coordinates[2]),
                    "yaw": 0,
                    "pitch": 0
                }), [connection.get_address()])

                self._server.broadcast(MessagePacket.make({
                    "unused": 0xFF,
                    "message": "%s has joined!" % player.name
                }))

            elif packet == PositionAndOrientationPacket:
                player = self._server.get_player_by_address(connection.get_address())
                player.coordinates = [float(fields["frac_x"] / 32.0),
                                      float(fields["frac_y"] / 32.0),
                                      float(fields["frac_z"] / 32.0)]

                player.yaw = fields["yaw"]
                player.pitch = fields["pitch"]

                fields["player_id"] = player.player_id

                self._server.broadcast(PositionAndOrientationPacket.make(fields))

            elif packet == SetBlockPacket:
                x, y, z = fields["x"], fields["y"], fields["z"]
                mode = fields["mode"]
                block_type = fields["block_type"]

                # Sanity check
                if x in range(WORLD_WIDTH) and y in range(WORLD_HEIGHT) and z in range(WORLD_DEPTH):
                    if mode == 0:
                        block_type = 0

                    self._server.broadcast(BlockUpdatePacket.make({
                        "x": x,
                        "y": y,
                        "z": z,
                        "block_type": block_type
                    }))

                    self._server.get_world().set_block(x, y, z, block_type)

            elif packet == MessagePacket:
                player = self._server.get_player_by_address(connection.get_address())
                message = fields["message"]

                self._server.broadcast(MessagePacket.make({
                    "unused": 255,
                    "message": "[%s] &a%s" % (player.name, message)
                }))

            else:
                print("unknown packet %s", packet.__class__.__name__)
