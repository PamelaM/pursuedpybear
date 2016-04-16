from collections import namedtuple

from ppb import engine
from ppb.event import Tick, Message, ObjectCreated, ObjectDestroyed
from ppb.vmath import Vector2 as Vec

Command = namedtuple("Command", ["event", "callback"])


class Model(object):

    def __init__(self, pos=Vec(0, 0), **kwargs):
        self.pos = pos
        self.commands = []

    def kill(self):
        engine.message(ObjectDestroyed(self, self.commands))


class GameObject(Model):

    def __init__(self, *args, **kwargs):
        super(GameObject, self).__init__(*args, **kwargs)
        engine.message(ObjectCreated(self, self.commands))


class Mobile(Model):

    def __init__(self, velocity=Vec(0, 0), *args, **kwargs):
        super(Mobile, self).__init__(velocity=velocity,
                                     *args,
                                     **kwargs)
        self.velocity = velocity
        self.commands.append((Tick, self.tick))

    def tick(self, tick):
        self.pos += self.velocity * tick.sec


class Renderable(Model):

    def __init__(self, image=None, view=None, image_size=0, hardware=None, *args, **kwargs):
        super(Renderable, self).__init__(image=image,
                                         view=view,
                                         image_size=image_size,
                                         *args,
                                         **kwargs)

        view.add(hardware.Sprite(image, self, size=image_size))

    def kill(self):
        super(Renderable, self).kill()
        engine.message(Message(self, None, {"command": "kill"}))


class Controllable(Mobile):

    def __init__(self, commands=None, *args, **kwargs):
        super(Controllable, self).__init__(commands=commands,
                                           *args,
                                           **kwargs)
        if commands is not None:
            for command in commands:
                self.register_command(command)

    def register_command(self, command):
        """
        Register controls to events.

        To respond the state of the keyboard or mouse each loop, subscribe your
        function to Tick.

        To respond to the instance of pressing a mouse button or key subscribe
        to MouseButtonDown or KeyDown.

        You can also respond to any other event.

        :param scene: Publisher
        :param command: iterable of length 2
                        The first element should be an Event class.
                        The second element should be a function of the
                        signature func(self, event) and return None.
        """
        command = Command(command[0], self.bind(command[1]))
        self.commands.append(command)

    def bind(self, function):
        """
        Bind a callback to Controllable.

        :param function: Must be a function with a signature of
                         function(self, event)
        """
        def callback(event):
            return function(self, event)
        return callback


class Collider(Model):

    def __init__(self, radius=0, *args, **kwargs):
        super(Collider, self).__init__(radius=radius, *args, **kwargs)
        self.radius = radius