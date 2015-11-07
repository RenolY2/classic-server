import struct
import gzip

WORLD_WIDTH = 256
WORLD_HEIGHT = 64
WORLD_DEPTH = 256

class World(object):
    def __init__(self, blocks=None):
        self.blocks = blocks if blocks else self._generate()

    def _generate(self):
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
        return World(gzip.decompress(data)[4:])
