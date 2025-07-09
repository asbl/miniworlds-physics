import math
import sys
from typing import Optional, Union
import pygame
import pymunk as pymunk_engine
import pymunk.pygame_util
from miniworlds.actors import actor as actor
from miniworlds.actors.shapes import shapes


class ActorPhysics:
    """Defines physics-properties of a actor, used as my_actor.physics.attribute or my_actor.physics.method

    Can only be used for actors on a PhysicsWorld.

    Examples:

        .. code-block:: python

            from miniworlds import *

            world = PhysicsWorld((800, 600))

            a = Circle()
            a.position = (75, 200)
            a.color = (255,0,0)
            a.physics.simulation = "simulated"
            a.direction = 180
            a.physics.shape_type = "circle"
            a.impulse(45, 1500)

            world.run()
    """

    def __init__(self, actor, world):
        self.started: bool = False
        self._body_type = pymunk.Body.DYNAMIC
        self.world = world
        self.actor: actor.Actor = actor
        self.simulation: str = "simulated"
        self._gravity: bool = False
        self._stable: bool = False
        self._can_move: bool = True
        self._density: float = 10
        self.moment: Optional[float] = None
        self.damping = 1
        self.max_velocity_x = math.inf
        self._friction: float = 0.5
        self._velocity_x: float = 0
        self._velocity_y: float = 0
        self._elasticity: float = 0.5
        self._shape_type: str = "rect"
        self._correct_angle: float = 90
        self._body: Union[pymunk_engine.Body, None] = None
        self._shape: Union[pymunk_engine.Shape, None] = None
        self.dirty: int = 1
        self.has_physics: bool = False
        self.size = (1, 1)  # scale factor for physics box model
        self.joints = []

    @staticmethod
    def velocity_function(body, gravity, damping, dt):
        pymunk.Body.update_velocity(
            body, gravity, body.physics_property.damping * damping, dt
        )
        if (
            body.physics_property.max_velocity_x != math.inf
            and body.velocity[0] > body.physics_property.max_velocity_x
        ):
            body.velocity = body.physics_property.max_velocity_x, body.velocity[1]
        if (
            body.physics_property.max_velocity_x != math.inf
            and body.velocity[0] < -body.physics_property.max_velocity_x
        ):
            body.velocity = -body.physics_property.max_velocity_x, body.velocity[1]

    def join(self, other: "actor.Actor", type="pin"):
        """joins two actors at their center points"""
        if not hasattr(other, "physics"):
            raise TypeError("Other actor has no attribute physics")
        my_body = self._body
        other_body = other.physics._body
        pj = pymunk.PinJoint(my_body, other_body, (0, 0), (0, 0))
        self.joints.append(pj)
        self.world.space.add(pj)
        return self.actor.position_manager.position, other.position

    def remove_join(self, other: "actor.Actor"):
        """Remove a joint between two actors.

        Removes a joint between two actors, if a joint exists.

        Examples:

            Add and remove a joint on key_down:

            .. code-block:: python

                import random
                from miniworlds import *
                world = PhysicsWorld((400, 200))
                connected = False
                line = None
                anchor = Rectangle()
                anchor.size = (20,20)
                anchor.center = (100, 20)
                anchor.physics.simulation = "manual"
                other_side = Line((250,100),(500,200))
                def add_line(obj1, obj2):
                    l = Line(obj1.center, obj2.center)
                    l.physics.simulation = None
                    @l.register
                    def act(self):
                        self.start_position = obj1.center
                        self.end_position = obj2.center
                    return l
                c = Circle()
                @c.register
                def on_key_down(self, key):
                    global connected
                    global line
                    if not connected:
                        print("not connected")
                        self.physics.join(anchor)
                        line = add_line(self, anchor)
                        connected = True
                    else:
                        print("connected")
                        self.physics.remove_join(anchor)
                        line.remove()

                world.run()


            .. raw:: html

                <video loop autoplay muted width=400>
                <source src="../_static/jointsremove1.webm" type="video/webm">
                <source src="../_static/jointsremove1.mp4" type="video/mp4">
                Your browser does not support the video tag.
                </video>
        """
        for join in self.joints:
            if other.physics._body == join.b:
                self.world.space.remove(join)

    def _start(self):
        """Starts the physics-simulation

        Called in world-connector
        """
        if not self.started:
            self.started = True
            self._setup_physics_model()  # After on_setup

    def _get_pymunk_shape(self):
        actor_rect =  self._get_rect()
        if self.shape_type.lower() == "rect":
            shape = pymunk.Poly.create_box(
                self._body,
                (self.size[0] * self.actor.width, self.size[1] * self.actor.height),
                1,  # small radius
            )
        elif self.shape_type.lower() == "circle":
            shape = pymunk.Circle(
                self._body,
                self.size[0] * self.actor.width / 2,
                (0, 0),
            )
        elif isinstance(self.actor, shapes.Line):
            start = pymunk.pygame_util.from_pygame(
                (0, -self.actor._length / 2), actor_rect
            )
            end = pymunk.pygame_util.from_pygame(
                (0, self.actor._length / 2), actor_rect
            )
            shape = pymunk.Segment(self._body, start, end, self.actor.thickness)
        else:
            raise AttributeError("No shape set!")
        return shape

    def _setup_physics_model(self):
        if (
            self.dirty and self.actor.position_manager.position
        ):  # if actor is on the world
            # create body
            self.has_physics = False
            self._body = pymunk_engine.Body(body_type=self.body_type)
            self._body.physics_property = self
            self._body.moment = math.inf
            self._body.velocity_func = self.velocity_function
            # self._body.damping = self.damping
            self._set_pymunk_position()
            self._set_pymunk_direction()
            self._body.size = (
                self.size[0] * self.actor.width,
                self.size[1] * self.actor.height,
            )

            # disable velocity for actors if actor has no gravity
            if self.simulation == "static":
                self._body.velocity_func = lambda body, gravity, damping, dt: None
            else:
                self._body.velocity = self.velocity_x, self._velocity_y
            # Adds object to space
            if self._simulation:
                self._shape = self._get_pymunk_shape()
                self._shape.density = self.density
                self._shape.friction = self.friction
                self._shape.elasticity = self.elasticity
                self._shape.actor = self.actor
                self._shape.collision_type = hash(self.actor.__class__.__name__) % (
                    (sys.maxsize + 1) * 2
                )
                self.world.space.add(self._body, self._shape)
            if self.moment is not None:
                self._body.moment = self.moment
            if self.simulation == "static":
                self.world.space.reindex_static()
            self.dirty = 1
            self.has_physics = True

    def _get_rect(self):
        rect =  self.actor.world.backgrounds_manager.image if hasattr(self.actor.world, "backgrounds_manager") else pygame.Rect(0,0,1,1)

    def _set_pymunk_position(self):
        actor_rect =  self._get_rect()
        pymunk_position = self.actor.center[0], self.actor.center[1]
        self._body.position = pymunk.pygame_util.from_pygame(
            pymunk_position, actor_rect
        )

    def _set_pymunk_direction(self):
        self._body.angle = (
            self.actor.position_manager.get_pymunk_direction_from_miniworlds()
        )

    def _set_mwm_actor_position(self):
        actor_rect =  self._get_rect()
        if self._body:
            self.actor.center = pymunk.pygame_util.from_pygame(
                self._body.position, actor_rect
            )
            self.dirty = 0

    def _set_mwm_actor_direction(self):
        self.actor.position_manager.set_mwm_direction_from_pymunk()
        self.dirty = 0

    def reload(self):
        """Removes actor from space and reloads physics_model"""
        if self.started:
            self.dirty = 1
            # Remove shape and body from space
            self._remove_from_space()
            # Set new properties and reset to space
            self._setup_physics_model()
        else:
            self.dirty = 1

    def _remove_from_space(self):
        if self._body:
            for shape in list(self._body.shapes):
                if shape in self.world.space.shapes:
                    self.world.space.remove(shape)
            if self._body in self.world.space.bodies:
                self.world.space.remove(self._body)

    def remove(self):
        """Removes an object from physics-space"""
        self._remove_from_space()

    @property
    def simulation(self):
        """Sets simulation type for actor (`static`, `manual`, `simulated` or `None`)

        Sets simulation type for actor:

        * `simulated`: Actor is fully simulated by physics engine.
        * `manual`: Actor is not affected by gravity.
        * `static`: Actor is not moved by physics engine, but actors can collide with actor.
        * `None`: Actor is not moved by physics engine and other actors can't collide with actor.
        """
        return self._simulation

    @simulation.setter
    def simulation(self, value: Union[str, None]):
        # Sets the simulation type
        self._simulation = value
        if not value:
            self._is_rotatable = False
            self._gravity = False
            self._can_move = False
            self._stable = True
        elif value.lower() == "static":
            self._is_rotatable = False
            self._gravity = False
            self._can_move = False
            self._stable = True
            self.density = 0
        elif value.lower() == "manual":
            self._is_rotatable = True
            self._gravity = False
            self._can_move = True
            self._stable = True
        elif value.lower() == "simulated":
            self._is_rotatable = True
            self._gravity = True
            self._can_move = True
            self._stable = True
        self.dirty = 1
        self.reload()

    @property
    def body(self):
        return self._body

    @body.setter
    def body(self, value):
        self._body = value

    @property
    def body_type(self):
        """Returns body type of actor

        Must not be used from outside - Use property simulation instead.
        """
        if self.simulation is None or self.simulation == "static":
            return pymunk.Body.STATIC
        elif self.simulation == "manual":
            return pymunk.Body.KINEMATIC
        else:
            return pymunk.Body.DYNAMIC

    @property
    def size(self):
        """Sets size of physics_object in relation to object

        * 1: Physics object size equals actor size
        * < 1: Physics object is smaller than actor
        * > 1: Physics object is larger than actor.

        .. warning::

            Actor is re-added to physics space after this operation - Velocity and impulses are lost.
        """
        return self._size

    @size.setter
    def size(self, value: tuple):
        self._size = value
        self.dirty = 1
        self.reload()

    @property
    def shape_type(self):
        """Sets shape type of object:

        Shape Types:
          * "rect": Rectangle
          * "circle": Circle

        .. warning::

            Actor is re-added to physics space after this operation - Velocity and impulses are lost.

        Examples:

            Demonstrate different shape types:

            .. code-block:: python

                from miniworlds import *

                world = PhysicsWorld(600,300)
                Line((0,100),(100,150))
                t = Actor((0,50))
                t.physics.shape_type = "rect"
                Line((200,100),(300,150))
                t = Actor((200,50))
                t.physics.shape_type = "circle"
                world.run()

            .. raw:: html

                <video loop autoplay muted width=400>
                <source src="../_static/shape_types.webm" type="video/webm">
                <source src="../_static/shape_types.mp4" type="video/mp4">
                Your browser does not support the video tag.
                </video>
        """
        return self._shape_type

    @shape_type.setter
    def shape_type(self, value: str):
        self._shape_type = value
        self.dirty = 1
        self.reload()

    @property
    def friction(self):
        """Sets friction of actor

        .. warning::

            Actor is re-added to physics space after this operation - Velocity and impulses are lost.

        """
        return self._friction

    @friction.setter
    def friction(self, value: float):
        self._friction = value
        self.dirty = 1
        self.reload()

    @property
    def elasticity(self):
        """Sets elasticity of actor

        .. warning::

            Actor is re-added to physics space after this operation - Velocity and impulses are lost.

        """
        return self._elasticity

    @elasticity.setter
    def elasticity(self, value: float):
        self._elasticity = value
        self.dirty = 1
        self.reload()

    @property
    def density(self):
        """Sets density of actor

        .. warning::

            Actor is re-added to physics space after this operation - Velocity and impulses are lost.

        """
        return self._density

    @density.setter
    def density(self, value: float):
        self._density = value
        self.dirty = 1
        self.reload()

    def _simulation_preprocess_actor(self):
        """
        Updates the physics model in every frame

        Returns:

        """
        if (
            self._body and not self._body.body_type == pymunk_engine.Body.STATIC
        ) and self.dirty:
            self._set_pymunk_position()
            self._set_pymunk_direction()
            self.world.space.reindex_shapes_for_body(self._body)
            self.dirty = 0

    def _simulation_postprocess_actor(self):
        """
        Reloads physics model from pygame data
        """
        if self.simulation and not math.isnan(self._body.position[0]):
            self._set_mwm_actor_position()
            self._set_mwm_actor_direction()
        if self._body and not self._body.body_type == pymunk_engine.Body.STATIC:
            self.velocity_x = self._body.velocity[0]
            self.velocity_y = self._body.velocity[1]
            if self.world.debug:
                options = pymunk.pygame_util.DrawOptions(self.actor.world.backgrounds_manager.image)
                options.collision_point_color = (255, 20, 30, 40)
                self.world.space.debug_draw(options)

    @property
    def velocity_x(self):
        """Sets velocity in x-direction. Can be positive or negative.

        Examples:

           Move a actor left or right.

           .. code-block:: python

               def on_key_pressed_d(self):
                   self.physics.velocity_x = 50

               def on_key_pressed_a(self):
                   self.physics.velocity_x = - 50

        """
        return self._velocity_x

    @velocity_x.setter
    def velocity_x(self, value: float):
        self._velocity_x = value
        if self._body:
            self._body.velocity = value, self._body.velocity[1]

    @property
    def velocity_y(self):
        """Sets velocity in y-direction"""
        return self._velocity_y

    @velocity_y.setter
    def velocity_y(self, value: float):
        self._velocity_y = value
        if self._body:
            self._body.velocity = self._body.velocity[0], value

    @property
    def is_rotatable(self):
        """defines, if actor will be rotated by physics-engine."""
        return self._is_rotatable

    @is_rotatable.setter
    def is_rotatable(self, value: bool):
        self._is_rotatable = value
        self.dirty = 1
        self.reload()

    def impulse_in_direction(self, direction: float, power: float):
        """
        Adds an impulse in actor-direction

        Examples:

            .. code-block:: python

                from miniworlds import *

                world = PhysicsWorld(300, 200)

                rect = Rectangle((280,120), 20, 80)
                rect.physics.simulation = "manual"
                ball = Circle((50,50),20)

                @rect.register
                def act(self):
                    rect.x -= 1
                    if rect.x == 0:
                        rect.x = 280

                @ball.register
                def on_key_down(self, key):
                    self.physics.impulse_in_direction(0, 5000)
                world.run()


        Args:
            power: The power-value of the impulse.
            direction: pymunk direction
        """
        impulse = pymunk.Vec2d(1, 0)
        impulse = impulse.rotated_degrees(
            360
            - self.actor.position_manager.dir_to_unit_circle(
                direction - self.actor.direction
            )
        )
        impulse = power * 1000 * impulse.normalized()
        self._body.apply_impulse_at_local_point(impulse)

    def force_in_direction(self, direction: float, power: float):
        """
        Adds a force in given direction

        Args:
            power: The power-value of the force.
            direction: pymunk direction
        """
        force = pymunk.Vec2d(1, 0)
        force = force.rotated_degrees(
            360
            - self.actor.position_manager.dir_to_unit_circle(
                direction - self.actor.direction
            )
        )
        force = power * 10000 * force.normalized()
        self._body.apply_force_at_local_point(force, (0, 0))
