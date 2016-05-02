"""
Modules that allow communication wih shoebot from other programmes.

shell         provides a commandline shell, that IDEs can use to provide livecoding
              and other control of a running bot, such as framerate and changing
              var values.

              shell is activated by using the 'l' (L) command

socketserver  similar to 'shell' but for remote connections, allows changing many
              of the same things as 'shell' except loading new code, as this
              would be a massive security hole!

              socketserver is activated by passing -s and optionally --port
"""
# NOTE - Called 'sbio' not 'io', since calling a module 'io' can break
#        the stdlib and ability to install things with pip :/
from shell import ShoebotCmd
from socket_server import SocketServer