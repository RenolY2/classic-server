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

import struct
import gzip

WORLD_WIDTH = 256
WORLD_HEIGHT = 64
WORLD_DEPTH = 256


class World(object):
    def __init__(self, blocks=None):
        self.blocks = blocks if blocks else self._generate()

    @staticmethod
    def _generate():
        print("[WORLD] Generating...")
        blocks = bytearray(WORLD_WIDTH * WORLD_HEIGHT * WORLD_DEPTH)

        for x in range(WORLD_WIDTH):
            for y in range(WORLD_HEIGHT):
                for z in range(WORLD_DEPTH):
                    blocks[x + WORLD_DEPTH * (z + WORLD_WIDTH * y)] = 0 if y > 32 else (2 if y == 32 else 3)

        print("[WORLD] done.")
        return blocks

    def get_block(self, x, y, z):
        return self.blocks[x + WORLD_DEPTH * (z + WORLD_WIDTH * y)]

    def set_block(self, x, y, z, block):
        self.blocks[x + WORLD_DEPTH * (z + WORLD_WIDTH * y)] = block

    def encode(self):
        return gzip.compress(struct.pack("!I", len(self.blocks)) + bytes(self.blocks))

    @staticmethod
    def from_save(data):
        return World(bytearray(gzip.decompress(data)[4:]))
