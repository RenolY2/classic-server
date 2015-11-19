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

DEFAULT_COORDINATES = [127.0, 35.0, 127.0]


class Player(object):
    player_id = None
    coordinates = DEFAULT_COORDINATES
    yaw = 0
    pitch = 0
    name = ""
    client = None
    user_type = None

    def __init__(self, player_id, client, coordinates, name, user_type):
        self.player_id = player_id
        self.client = client
        if coordinates:
            self.coordinates = coordinates
        self.name = name
        self.user_type = user_type
