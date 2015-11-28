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

import random
import socket
import string
import threading
import time
import traceback
import logging
import urllib.request
import urllib.parse

from classicserver.connection import Connection
from classicserver.packet.packet import MessagePacket, PingPacket, DespawnPlayerPacket, DisconnectPlayerPacket
from classicserver.packet_handler import PacketHandler
from classicserver.player import Player
from classicserver.world import World


class ClassicServer(object):
    MTU = 1024

    _bind_address = None
    _running = None
    _sock = None

    _packet_handler = None

    _connections = {}

    _players = {}
    _players_by_address = {}

    _connections_lock = None

    _player_id = 1

    _server_name = ""
    _motd = ""

    _save_file = ""
    _heartbeat_url = ""
    _salt = ""

    _op_players = []
    _max_players = -1

    _world = None

    def __init__(self, bind_address, server_name="", motd="", save_file="", heartbeat_url="", op_players=None,
                 max_players=32):
        self._bind_address = bind_address
        self._running = False
        self._server_name = server_name
        self._motd = motd
        self._save_file = save_file
        self._heartbeat_url = heartbeat_url
        self._op_players = op_players if op_players else []
        self._max_players = max_players

        if self._max_players > 255:
            raise ValueError("The player limit is up to 255 excluding the admin slot.")

        logging.basicConfig(level=logging.DEBUG)

        self._connections_lock = threading.Lock()

        self._packet_handler = PacketHandler(self)

        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.bind(self._bind_address)

        self._sock.listen(1)
        self._start()

    def data_hook(self, client, data):
        try:
            self._packet_handler.handle_packet(client, data)
        except (IOError, ValueError, BrokenPipeError) as ex:
            logging.error("Error in packet handler: %s" % repr(ex))
            logging.debug(traceback.format_exc())

    def _heartbeat_thread(self):
        while self._running:
            try:
                f = urllib.request.urlopen(self._heartbeat_url + (
                    "?port=%d&max=%d&name=%s&public=True&version=7&salt=%s&users=%d" % (
                        self._bind_address[1], self._max_players,
                        urllib.parse.quote(self._server_name, safe=""), self._salt, len(self._players))
                ))

                data = f.read()

                logging.debug("Heartbeat sent, json response: %s" % data.decode("utf-8"))

            except BaseException as ex:
                logging.error("Heartbeat failed: %s" % repr(ex))
                logging.debug(traceback.format_exc())
            time.sleep(45)

    def _save_thread(self):
        while self._running:
            try:
                self.broadcast(MessagePacket.make({
                    "player_id": 0,
                    "message": "Autosaving the world..."
                }))
                self.save_world()
                time.sleep(120)
            except BaseException as ex:
                logging.error("Autosaving failed: %s" % repr(ex))
                logging.debug(traceback.format_exc())

        self.save_world()

    def _keep_alive_thread(self):
        while self._running:
            self._connections_lock.acquire()
            for connection in self._connections.values():
                try:
                        connection.send(PingPacket.make())
                except IOError:
                        self._disconnect(connection)
            self._connections_lock.release()
            time.sleep(30)

    def _connection_thread(self):
        while self._running:
            sock, addr = self._sock.accept()

            self._connections_lock.acquire()
            self._connections[addr] = Connection(self, addr, sock)
            self._connections_lock.release()

    def _flush_thread(self):
        while self._running:
            try:
                connections = [x for x in self._connections.values()]
                for connection in connections:
                    try:
                        connection.flush()
                    except IOError:
                        self._disconnect(connection)
            except RuntimeError:
                pass

    def broadcast(self, data, ignore=None):
        if not ignore:
            ignore = []

        for connection in self._connections.values():
            if connection.get_address() not in ignore:
                connection.send(data)

    def _disconnect(self, connection):
        player = None

        if connection.get_address() in self._players_by_address:
            player = self.get_player_by_address(connection.get_address())

        del self._connections[connection.get_address()]

        if player:
            logging.info("Player %s has quit" % player.name)
            del self._players_by_address[connection.get_address()]
            del self._players[player.player_id]
            self.broadcast(DespawnPlayerPacket.make({"player_id": player.player_id}))
            self.broadcast(MessagePacket.make({"player_id": 0, "message": "%s&f has quit"}))

    def _start(self):
        self.generate_salt()
        self.load_world()
        self._running = True
        threading.Thread(target=self._save_thread).start()
        threading.Thread(target=self._connection_thread).start()
        threading.Thread(target=self._flush_thread).start()
        threading.Thread(target=self._keep_alive_thread).start()
        if self._heartbeat_url:
            threading.Thread(target=self._heartbeat_thread).start()

    def _stop(self):
        self._running = False
        self._sock.close()

    def load_world(self):
        try:
            save = open(self._save_file, "rb").read()
            self._world = World.from_save(save)
            return
        except FileNotFoundError:
            logging.info("Save file not found, creating a new one")
        except IOError as ex:
            logging.error("Error during loading save file: %s" % repr(ex))
            logging.error(traceback.format_exc())

        self._world = World()

    def save_world(self):
        logging.info("Saving the world...")
        save_file = open(self._save_file, "wb")
        save_file.write(self._world.encode())
        save_file.flush()
        save_file.close()

    def generate_salt(self):
        base_62 = string.ascii_letters + string.digits
        # generate a 16-char salt
        salt = "".join([random.choice(base_62) for i in range(16)])
        self._salt = salt

    def add_player(self, connection, coordinates, name):
        """

        :type connection: Connection
        """
        if len(self._players) < self._max_players and not self.is_op(name):
            player_id = self._player_id
            if self._player_id in self._players:
                for i in range(256):
                    if not i in self._players:
                        self._player_id = i
                        player_id = i
                        break
                else:
                    raise ValueError("No more ID's left")

            else:
                self._player_id += 1

            player = Player(player_id, connection, coordinates, name, 0x64 if self.is_op(name) else 0x00)
            self._players[player_id] = player
            self._players_by_address[connection.get_address()] = player
            return player_id
        else:
            logging.warning("Disconnecting player %s because no free slots left." % name)
            connection.send(DisconnectPlayerPacket.make({"reason": "Server full"}))

    def kick_player(self, player_id, reason):
        player = self._players[player_id]
        logging.info("Kicking player %s for %s" % (player.name, reason))
        player.connection.send(DisconnectPlayerPacket.make({"reason": reason}))
        self.broadcast(MessagePacket.make({"player_id": 0, "message": "Player %s kicked, %s" % (player.name, reason)}))
        self._disconnect(player.connection)

    def is_op(self, player_name):
        if player_name in self._op_players:
            return True
        else:
            return False

    def get_name(self):
        return self._server_name

    def get_motd(self):
        return self._motd

    def get_player(self, player_id):
        return self._players[player_id]

    def get_player_by_address(self, address):
        return self._players_by_address[address]

    def get_players(self):
        return self._players

    def get_world(self):
        return self._world

    def get_salt(self):
        return self._salt

    def __exit__(self):
        self._stop()
