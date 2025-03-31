from thespian.actors import (
    Actor,
    ActorSystem,
    ActorExitRequest
)


# Our example actor
class Hello(Actor):
    def receiveMessage(self, msg, sender):
        # The messages will be fed in here. Messages can be of any
        # type as long as they are hashable. We are also supplied
        # with the address of the sender which can be used to
        # respond back.
        self.send(sender, 'Hello, Thespian World!')


if __name__ == '__main__':
    # Create our actor instance. Remember that a created ActorSystem
    # is a singleton that represents the local actor environment.
    # Both actors and the ActorSystem have a `createActor()` method.
    hello = ActorSystem().createActor(Hello)

    # Send "Hi" to our actor and wait for a response. Actors are
    # **not** required to respond, but our Hello actor does.
    print(ActorSystem().ask(hello, 'hi', 1))

    # Telling our `ActorSystem` to clean up for exit.
    ActorSystem().tell(hello, ActorExitRequest())
