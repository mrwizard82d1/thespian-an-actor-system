"""
Implements the "client" `ActorSystem`.
"""

from datetime import timedelta
import sys

from thespian.actors import ActorSystem


if __name__ == '__main__':
    # The convertion leaders IP address **must** be supplied on
    # the command line. In addition, we tag this system  as the
    # "Client" system.
    capabilities = {
        'Convention Address.IPv4': (sys.argv[1], 1900),
        'Client': True,
    }
    actor_system = ActorSystem('multiprocTCPBase',
                               capabilities=capabilities)

    # Create an actor from the echo "library" with the class `EchoRequestor`
    echo_app = actor_system.createActor('echo.EchoRequestor')

    # Send the echo actor a message: the (maximum?) number of echo requests
    # it should perform.
    actor_system.tell(echo_app, int(sys.argv[2]))

    # Now, send the echo payload, and wait for a maximum of 10s for
    # an answer
    response = actor_system.ask(echo_app,
                                'Hello, Thespian echo world!',
                                timedelta(seconds=10))
    while response:
        # If we get the "echo_done" message, as an answer, we stop
        if response == 'echo_done':
            break

        # Otherwise, the message is unexpected so we "eat it"
        # and retry listening for messages.
        response = actor_system.listen(timedelta(seconds=10))
