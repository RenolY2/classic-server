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

from classicserver.packet.packet import MessagePacket, DisconnectPlayerPacket

HELP_TEXT = """
&aClassic-Server Help
&4 Commands:
&e /help &b - this help
&e /tp &2<x> <y> <z> &b - teleport to coordinates
&e /tp &2<playerName> &b - teleport to player
&e /kick &2<playerName> [reason] &b - kick a player
"""

class CommandHandler(object):
    @staticmethod
    def handle_command(server, player, command, args):
        if command == "tp":
            if len(args) == 3:
                try:
                    player.coordinates = [float(args[0]), float(args[1]), float(args[2])]
                except ValueError:
                    player.client.send(MessagePacket.make({"unused": 255, "message": "&4Invalid coordinates,"}))
                    player.client.send(MessagePacket.make({"unused": 255,
                                                           "message": "&4please use /tp <x> <y> <z> or"}))
                    player.client.send(MessagePacket.make({"unused": 255, "message": "&4/tp <playerName>"}))
            elif len(args) == 1:
                for target_player in server.get_players().values():
                    if target_player.name == args[1]:
                        player.coordinates = target_player.coordinates
                        break
                else:
                    player.client.send(MessagePacket.make({"unused": 255, "message": "&4Target player not found."}))
            else:
                player.client.send(MessagePacket.make({"unused": 255,
                                                       "message": "&4Invalid arguments, please use /tp <x> <y> <z> or"}))
                player.client.send(MessagePacket.make({"unused": 255, "message": "&4/tp <playerName>"}))
        elif command == "kick":
            if len(args) >= 1:
                player_name = args[0]
                reason = " ".join(args[1:]) if len(args) > 1 else "No reason specified"
                for target_player in server.get_players.values():
                    if target_player.name == player_name:
                        target_player.client.send(DisconnectPlayerPacket.make({"reason": reason}))
                        break
                else:
                    player.client.send(MessagePacket.make({"unused": 255,
                                                           "message": "&4Couldn't find the player specified."}))
            else:
                player.client.send(MessagePacket.make({"unused": 255,
                                                       "message": "&4Usage: /kick <playerName> [reason]"}))
        elif command == "help":
            for line in HELP_TEXT.split("\n"):
                line = line.strip()
                player.client.send(MessagePacket.make({"unused": 255,
                    "message": "%s" % line}))