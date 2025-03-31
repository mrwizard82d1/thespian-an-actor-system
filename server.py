"""
Implements a "Server" system as the Convention leader.
"""

import logging.handlers
import socket

from thespian.actors import ActorSystem


def get_my_ip():
    """Return the IP address of the local host."""
    return socket.gethostbyname(socket.gethostname())


if __name__ == '__main__':
    # Configure logging
    log = logging.getLogger(__name__)
    log.setLevel(logging.DEBUG)
    handler = logging.handlers.SysLogHandler(address='/dev/log')
    log.addHandler(handler)

    # Configure this `ActorSystem` as the convention leader with a
    # capability of "Server"
    #
    # By default, `ActorSystems` use port 1900. We'll use this port
    # for our `ActorSystem` also.
    capabilities = {
        'Convention Address.IPv4': (get_my_ip(), 1900),
        'Server': True,
    }
    ActorSystem('multiprocTCPBase', capabilities=capabilities)
