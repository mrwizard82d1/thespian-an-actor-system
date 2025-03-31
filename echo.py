"""
The echo module: the meat of this application and used by
both client and server.

This module contains these classes:

- Simple data classes named "Ping" and "Pong"
- Actor (class) EchoRequestor (for issuing pings)
- Actor (class) EchoServer (for issuing pongs)
"""

import datetime
import logging
import logging.handlers

from thespian.actors import ActorTypeDispatcher, requireCapability


# Set up some logging to see what is happening
log = logging.getLogger('EchoLogger')
log.setLevel(logging.DEBUG)
handler = logging.handlers.SysLogHandler(address='/dev/log')
log.addHandler(handler)


class Ping:
    """A simple object that carries a payload."""
    def __init__(self, payload):
        self.payload = payload


class Pong(Ping):
    """
    Another simple object that carries a payload.

    We subclass it from `Ping` to use the implementation of `Ping`
    but still distinguish it by type.
    """
    pass


@requireCapability('Server')
class EchoServer(ActorTypeDispatcher):
    """
    The echo server actor.

    It will receive `Ping` messages, log them, and reply back to
    the sender with a `Pong` message.

    Specifies a system tagged with the "Server" capability as a
    requirements. This requirement causes the linked actor systems
    to instantiate it on the **server** actor system.
    """
    def receiveMsg_Ping(self, ping_request, sender):
        log.debug(f'Got {ping_request}, sending pong back to {sender}')
        self.send(sender, Pong(ping_request.payload))


@requireCapability('Client')
class EchoRequestor(ActorTypeDispatcher):
    """
    The echo client Actor.

    It specifies an actor system tagged with the "Client" capability. The
    client module is tagged with `Client: True`; consequently, this actor
    instance will get started on the client system.
    """

    echo_server = None

    def __init__(self):
        """
        Initialize counters and a timer.

        Don't forget to call the superclass constructor.
        """
        super().__init__()
        self.client = None
        self.pings_to_send = 0
        self.pongs_to_receive = 0
        self.time = None

    def receiveMsg_int(self, count, _client):
        """
        Increment `pings_to_send` by `count`.

        :param count: The number of pings to send.
        :param _client: Ignored
        """
        self.pings_to_send += count

    def receiveMsg_str(self, payload, client):
        """
        Receive my first payload and start pinging.

        If I receive a message of `type` `str`, I interpret that
        value as a payload with which to ping. I then start pinging
        for `self.pings_to_send` times.

        :param payload: The payload to send with each "ping."
        :param client: The client sending our initial message and
        to whom we report when finished.
        """

        # Remember the client (server) to notify later when we are finished.
        self.client = client

        # After stashing the client for later, instantiate an echo server.
        # Remember, because the `EchoServer` class has a requirement,
        # 'Server', it will be started on the actor system tagged with
        # the 'Server' capability.
        self.echo_server = self.createActor(EchoServer)

        # Finally, start sending "ping messages." Remember to save
        # the start time.
        ping = Ping(payload)
        log.debug(f'Sending: server={self.echo_server}'
                  f'message: {ping}, '
                  f'count: {self.pings_to_send}')
        self.time = datetime.datetime.now()

        # Send out `pings_to_send` Pings to the server
        for _ in range(self.pings_to_send):
            self.send(self.echo_server, ping)

        # Update counters.
        self.pongs_to_receive += self.pings_to_send
        self.pings_to_send = 0

    def receiveMsg_Pong(self, _pong, _server):
        """
        Receive "Pong" messages from the echo server actor.

        :param _pong: Ignored
        :param _server: Ignored
        """
        self.pongs_to_receive -= 1
        if self.pongs_to_receive <= 1:
            log.info(
                f'Got all messages, timedelta={datetime.datetime.now() - self.time}'
            )

            # We're finished so send a message informing the client
            log.info(f'Sending end request to {self.client}')
            self.send(self.client, 'echo_done')
