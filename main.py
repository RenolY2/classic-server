import json
from classicserver.server import ClassicServer

config = json.load(open("config/config.json"))

server = ClassicServer(("", config["server"]["port"]), config["server"]["name"], config["server"]["motd"],
                       config["save"]["file"], config["heartbeat_url"])
