import json
from classicserver.server import ClassicServer

config = json.load(open("config/config.json"))

server = ClassicServer(("0.0.0.0", config["server"]["port"]), config["server"]["name"], config["server"]["motd"],
                       config["save"]["file"], config["heartbeat_url"])
