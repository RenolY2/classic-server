# classic-server
A very basic Minecraft Classic server. It only supports 256x64x256 worlds and has only a flat genrator.

Usage
-----
`python main.py` will start the server with the default setttings (see below).

Configuration
-------------
To change the configuration, edit the file `config/config.json` as shown below:

```
{
  "server": {
    "name": "<server name>",
    "motd": "<message of the day>",
    "port": <port, using 25565 is recommended, make sure that no confilicts occur>
  },

  "save": {
    "file": "<to save the map, please specify the path to save the map in>"
  },

  "heartbeat_url": "<heartbeat url, you will need to change that for Minecraft.net instead of ClassiCube>"
}
```

Legal
-----
Minecraft is a registered trademark of Mojang AB. This project is not in any way affilitated with Mojang AB or Minecraft.
