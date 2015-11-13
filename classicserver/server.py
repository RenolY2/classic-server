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
import urllib.request
import urllib.parse

from classicserver.connection import Connection
from classicserver.packet.packet import MessagePacket, PingPacket, DespawnPlayerPacket
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

    _player_id = 0

    _server_name = ""
    _motd = ""

    _save_file = ""
    _heartbeat_url = ""
    _salt = ""

    _world = None

    def __init__(self, bind_address, server_name="", motd="", save_file="", heartbeat_url=""):
        self._bind_address = bind_address
        self._running = False
        self._server_name = server_name
        self._motd = motd
        self._save_file = save_file
        self._heartbeat_url = heartbeat_url

        self._packet_handler = PacketHandler(self)

        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.bind(self._bind_address)

        self._sock.listen(1)
        self._start()

    def data_hook(self, client, data):
        self._packet_handler.handle_packet(client, data)

    def _heartbeat_thread(self):
        while self._running:
            try:
                f = urllib.request.urlopen(self._heartbeat_url + (
                    "?port=%d&max=32&name=%s&public=True&version=7&salt=%s&users=%d" % (
                    self._bind_address[1], urllib.parse.quote(self._server_name, safe=""), self._salt,
                        len(self._players))
                ))

                data = f.read()

                print("[HEARTBEAT] Heartbeat sent, json response: %s" % data.decode("utf-8"))

            except BaseException as ex:
                print("[HEARTBEAT] Heartbeat failed: %s" % repr(ex))

            time.sleep(45)

    def _save_thread(self):
        while self._running:
            try:
                self.broadcast(MessagePacket.make({
                    "unused": 0xFF,
                    "message": "Autosaving the world..."
                }))
                self.save_world()
                time.sleep(120)
            except BaseException as ex:
                print("[AUTOSAVE] Autosaving failed: %s" % repr(ex))

        self.save_world()

    def _keep_alive_thread(self):
        while self._running:
            try:
                connections = [x for x in self._connections.values()]
                for connection in connections:
                    try:
                        connection.send(PingPacket.make())
                    except IOError:
                        self._disconnect(connection)
                time.sleep(30)

            except RuntimeError:
                pass

    def _connection_thread(self):
        while self._running:
            sock, addr = self._sock.accept()
            self._connections[addr] = Connection(self, addr, sock)

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
            print("[SERVER] Player %s has quit!" % player.name)
            del self._players_by_address[connection.get_address()]
            del self._players[player.player_id]
            self.broadcast(DespawnPlayerPacket.make({"player_id": player.player_id}))
            self.broadcast(MessagePacket.make({"unused": 0xFF, "message": "%s&f has quit"}))

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
        except Exception as ex:
            print("[INIT] Unable to load world, creating new... %s" % repr(ex))

        self._world = World()

    def save_world(self):
        print("[INIT] Saving the world....")
        save_file = open(self._save_file, "wb")
        save_file.write(self._world.encode())
        save_file.flush()
        save_file.close()

    def generate_salt(self):
        BASE_62 = string.ascii_letters + string.digits
        # generate a 16-char salt
        salt = "".join([random.choice(BASE_62) for i in range(16)])
        self._salt = salt

    def add_player(self, connection, coordinates, name):
        """

        :type connection: Connection
        """
        player = Player(self._player_id, connection, coordinates, name)
        self._players[self._player_id] = player
        self._players_by_address[connection.get_address()] = player
        player_id = self._player_id
        self._player_id += 1
        return player_id

    def get_name(self):
        return self._server_name

    def get_motd(self):
        return self._motd

    def get_player(self, player_id):
        return self._players[player_id]

    def get_player_by_address(self, address):
        return self._players_by_address[address]

    def get_world(self):
        return self._world

    def get_salt(self):
        return self._salt

    def __del__(self):
        self._stop()
