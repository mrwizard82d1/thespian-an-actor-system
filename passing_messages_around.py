"""
Passing messages around.
"""

import logging

from thespian.actors import (
    ActorSystem,
    ActorTypeDispatcher,
    ActorExitRequest
)


logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)


class Greeting:
    """
    A "data class" to hold a greeting and some addresses.
    """
    def __init__(self, msg: str):
        self.message = msg
        self.send_to = []

    def __str__(self):
        return self.message


class Hello(ActorTypeDispatcher):
    def receiveMsg_str(self, message, sender):
        """Handles all messages of type `str`"""

        if message == 'hi':
            # Create two additional actors of type World and of type Punctuate
            world = self.createActor(World)
            punctuate = self.createActor(Punctuate)

            # Create a greeting and add the punctuate and original sender addresses
            greeting = Greeting('Hello')
            greeting.send_to = [punctuate, sender]

            # Send the greeting to the World actor (who appends to the greeting)
            logger.debug(f'`Hello` sending {greeting} to {world}')
            self.send(world, greeting)


class World(ActorTypeDispatcher):
    def receiveMsg_Greeting(self, message, sender):
        """Handles all messages of type `Greeting` sent to this instance."""

        # Update the message and pass it to the first address in `send_to`.
        message.message += ', Thespian World'
        next_to = message.send_to.pop(0)
        logger.debug(f'`World` sending {message} to {next_to}')
        self.send(next_to, message)


class Punctuate(ActorTypeDispatcher):
    def receiveMsg_Greeting(self, message, sender):
        """Handles all messages of type `Greeting` sent to this instance."""

        # Update the message again and send it back to the original sender
        message.message += '!!!'
        next_to = message.send_to.pop(0)
        logger.debug(f'`Punctuate` sending {message} to {next_to}')
        self.send(next_to, message)


if __name__ == '__main__':
    # Create the "primordial" actor in our "system"
    hello = ActorSystem().createActor(Hello)

    # Send a message to this actor wait 0.2 seconds for a "response"
    # message, and...
    hello_result = ActorSystem().ask(hello, 'hi', 0.2)
    logging.info(f'{str(hello_result)}')

    # Termine the `hello` actor
    ActorSystem().tell(hello, ActorExitRequest())
