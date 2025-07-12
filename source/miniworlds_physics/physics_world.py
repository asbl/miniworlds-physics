import pymunk as pymunk_engine
from miniworlds import Line, World
from miniworlds.tools import actor_inspection
import miniworlds_physics.physics_world_event_manager as event_manager
import miniworlds_physics.physics_world_connector as world_connector


class PhysicsWorld(World):
    """
    A PhysicsWorld is a playing field on which objects follow physical laws.

    The PhysicsWorld itself defines some values with which the physics engine can be influenced, e.g.
    the gravity in the world.

    All actors on a PhysicsWorld have an attribute ``actor.physics``, with which you can change the physical properties
    of the object.
    """

    def __init__(
        self,
        columns: int = 40,
        rows: int = 40,
    ):
        self.gravity_x: float = 0
        self.gravity_y: float = 900
        self.debug: bool = False
        self._accuracy = 1
        self.space = pymunk_engine.Space()
        self.space.gravity = self.gravity_x, self.gravity_y
        self.space.iterations = 35
        self.space.damping = 0.9
        self.space.collision_persistence = 10
        self._damping = 0
        self.physics_actors = list()
        self.touching_methods = set()  # filled in actor_manager
        self.separate_methods = set()  # filled in actor_manager
        super().__init__(columns, rows)


    def _create_event_manager(self):
        return event_manager.PhysicsWorldEventManager(self)

    @property
    def accuracy(self):
        """Sets number of physics-steps performed in each frame.

        Default: 1
        """
        return self._accuracy

    @accuracy.setter
    def accuracy(self, value: int):
        self._accuracy = value

    @staticmethod
    def _get_world_connector_class():
        """needed by get_world_connector in parent class"""
        return world_connector.PhysicsWorldConnector


    def get_physics_collision_methods_for_actor(self, actor):
        """Gets all collision methods for actor

        :meta private:
        """
        # gets all method names
        methods = [
            method_name
            for method_name in dir(actor)
            if method_name.startswith("on_touching_")
            or method_name.startswith("on_separation_from_")
        ]
        # get methods from method names
        return [
            getattr(actor, method_name)
            for method_name in methods
            if hasattr(actor, method_name) and callable(getattr(actor, method_name))
        ]

    def on_new_actor(self, actor):
        if not actor.physics.simulation:
            connector = world_connector.PhysicsWorldConnector(self, actor)
            connector.remove_actor_from_physics()
    
    def simulate_all_physics_actors(self):
        """Iterates over all actors and process physics-simulation

        Processes phyisics-simulation in three steps

        * Convert miniworlds-position/direction to pymunk position/direction
        * Simulate a step in physics-engine
        * Convert pymunk position/direction to miniworlds position/direction

        :meta private:
        """
        if len(self.physics_actors) > 0:
            # pre-process
            [
                actor.physics._simulation_preprocess_actor()
                for actor in self.physics_actors
            ]
            # simulate
            steps = self.accuracy
            for _ in range(steps):
                # if self.physics.space is not None: - can be removed
                self.space.step(1 / (60 * steps))
            # post-process
            [
                actor.physics._simulation_postprocess_actor()
                for actor in self.physics_actors
            ]

    @property
    def gravity(self) -> tuple:
        """Defines gravity in physics world.

        Gravity is a 2-tuple with gravy in x-direction and y-direction.

        Default gravity: x=0, y=500

        Examples:

          Get all actors at mouse position:

          .. code-block:: python

            world = PhysicsWorld(400,400)
            world.gravity = (0, 0)
        """
        return self.gravity_x, self.gravity_y

    @gravity.setter
    def gravity(self, value: tuple):
        self.gravity_x = value[0]
        self.gravity_y = value[1]
        self.space.gravity = self.gravity_x, self.gravity_y

    @property
    def damping(self):
        """Amount of simple damping to apply to the space.

        A value of 0.9 means that each body will lose 10% of its velocity per second. Defaults to 1.
        """
        return self.gravity_x, self.gravity_y

    @damping.setter
    def damping(self, value: tuple):
        self._damping = value
        self.space.damping = self._damping

    def pymunk_touching_collision_listener(self, arbiter, space, data):
        """Handles collisions - Handled by pymunk engine

        :meta private:
        """
        # Translate pymunk variables to miniworlds variables.
        # Arbiter contains the two colliding actors.
        t1 = arbiter.shapes[0].actor
        t2 = arbiter.shapes[1].actor
        collision = dict()
        # get touching methods, e.g. `on_touching_circle`
        for method in self.touching_methods:
            # _cls_search_string = method.__name__[len("on_touching_"):].lower() # Get class by method name
            # filter_class = actor_class_inspection.ActorClassInspection(self).find_actor_class_by_classname(
            #    _cls_search_string
            # )
            # sets parameter for method
            if method.__self__ == t1:
                other = t2
            else:
                other = t1
            # call instance method with correct parameters
            # if isinstance(other, filter_class):
            actor_inspection.ActorInspection(method.__self__).get_and_call_method(
                method.__name__, [other, collision]
            )
        return True

    def pymunk_separation_collision_listener(self, arbiter, space, data):
        """Handles collisions - Handled by pymunk engine

        :meta private:
        """
        # Translate pymunk variables to miniworlds variables.
        # Arbiter contains the two colliding actors.
        t1 = arbiter.shapes[0].actor
        t2 = arbiter.shapes[1].actor
        collision = dict()
        # get touching methods, e.g. `on_touching_circle`
        for method in self.separate_methods:
            # _cls_search_string = method.__name__[len("on_separation_from_"):].lower() # Get class by method name
            # filter_class = actor_class_inspection.ActorClassInspection(self).find_actor_class_by_classname(
            #    _cls_search_string
            # )
            # sets parameter for method
            if method.__self__ == t1:
                other = t2
            else:
                other = t1
            # call instance method with correct parameters
            # if isinstance(other, filter_class):
            actor_inspection.ActorInspection(method.__self__).get_and_call_method(
                method.__name__, [other, collision]
            )
        return True

    def connect(self, actor1, actor2) -> "Line":
        line = Line(actor1.center, actor2.center)
        line.physics.simulation = None
        line.border = 1
        line.fill = True
        line.color = (255, 0, 0, 100)

        @line.register
        def act(self):
            self.start_position = actor1.center
            self.end_position = actor2.center

        return line
