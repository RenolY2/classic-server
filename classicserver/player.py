
DEFAULT_COORDINATES = [127.0, 35.0, 127.0]

class Player(object):
    player_id = None
    coordinates = DEFAULT_COORDINATES
    yaw = 0
    pitch = 0
    name = ""
    client = None

    def __init__(self, player_id, client, coordinates, name):
        self.player_id = player_id
        self.client = client
        if coordinates:
            self.coordinates = coordinates
        self.name = name
