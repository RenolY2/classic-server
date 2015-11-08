import hashlib
from classicserver.packet.buffer import ReadBuffer
from classicserver.packet.packets import *
from classicserver.packet.utils import *

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
                packet, fields = from_buffer(buf, True)
            except BaseException as e:
                print("Unable to decode packets: %s" % repr(e))
                break

            if packet == PlayerIdentificationPacket:
                if fields["key"] == hashlib.md5(fields["username"] + self._server.get_salt()).digest():
                    print("[INFO] Player %s is verified" % fields["username"])
                else:
                    print("[INFO] Unable to verify player %s")

                sendbuf = make_packet(ServerIdentificationPacket, {
                    "protocol_version": 7,
                    "server_name": self._server.get_name(),
                    "server_motd": self._server.get_motd(),
                    "user_type": 0x64
                })

                chunk = self._server.get_world().encode()
                parts = [chunk[i: i + 1024] for i in range(0, len(chunk), 1024)]

                sendbuf += make_packet(LevelInitializePacket, {})

                for count, part in enumerate(parts):
                    sendbuf += make_packet(LevelDataChunkPacket, {
                        "chunk_length": len(part),
                        "chunk": part,
                        "percent": int((100/len(parts))*count)
                    })

                sendbuf += make_packet(LevelFinalizePacket, {
                    "x": WORLD_WIDTH,
                    "y": WORLD_HEIGHT,
                    "z": WORLD_DEPTH
                })

                connection.send(sendbuf)

                username = fields["username"]
                print("[SERVER] Player %s has joined!" % username)
                player_id = self._server.add_player(connection, None, username)
                player = self._server.get_player(player_id)

                connection.send(make_packet(PositionAndOrientationPacket, {
                    "player_id": -1,
                    "frac_x": int(player.coordinates[0]*32),
                    "frac_y": int(player.coordinates[1]*32),
                    "frac_z": int(player.coordinates[2]*32),
                    "yaw": 0,
                    "pitch": 0
                }))

                self._server.broadcast(make_packet(SpawnPlayerPacket, {
                    "player_id": player.player_id,
                    "username": player.name,
                    "x": int(player.coordinates[0]),
                    "y": int(player.coordinates[1]),
                    "z": int(player.coordinates[2]),
                    "yaw": 0,
                    "pitch": 0
                }), [connection.get_address()])

                self._server.broadcast(make_packet(MessagePacket, {
                    "unused": 0xFF,
                    "message": "%s has joined!" % player.name
                }))

            elif packet == PositionAndOrientationPacket:
                player = self._server.get_player_by_address(connection.get_address())
                player.coordinates = [float(fields["frac_x"]/32.0),
                                      float(fields["frac_y"]/32.0),
                                      float(fields["frac_z"]/32.0)]

                player.yaw = fields["yaw"]
                player.pitch = fields["pitch"]

                fields["player_id"] = player.player_id

                self._server.broadcast(make_packet(PositionAndOrientationPacket, fields))

            elif packet == SetBlockPacket:
                x, y, z = fields["x"], fields["y"], fields["z"]
                mode = fields["mode"]
                block_type = fields["block_type"]

                # Sanity check
                if x in range(WORLD_WIDTH) and y in range(WORLD_HEIGHT) and z in range(WORLD_DEPTH):
                    if mode == 0:
                        block_type = 0

                    self._server.broadcast(make_packet(BlockUpdatePacket, {
                        "x": x,
                        "y": y,
                        "z": z,
                        "block_type": block_type
                    }))

                    self._server.get_world().set_block(x, y, z, block_type)

            elif packet == MessagePacket:
                player = self._server.get_player_by_address(connection.get_address())
                message = fields["message"]

                self._server.broadcast(make_packet(MessagePacket, {
                    "unused": 255,
                    "message": "[%s] &a%s" % (player.name, message)
                }))

            else:
                print("unknown packet %s", (packet.__class__.__name__))

