import miniworlds.worlds.manager.world_connector as world_connector
import miniworlds.worlds.manager.sensor_manager as sensor_manager
import miniworlds.tools.actor_class_inspection as actor_class_inspection
import miniworlds_physics.physics_world as world_mod
import miniworlds_physics.actor_physics as actor_physics
import miniworlds_physics.physics_world_position_manager as physics_position_manager
import miniworlds.actors.actor as actor_mod
import sys


class PhysicsWorldConnector(world_connector.WorldConnector):
    count_actors = 0

    def __init__(self, world: "world_mod.PhysicsWorld", actor: "actor_mod.Actor"):
        super().__init__(world, actor)
        self.world: "world_mod.PhysicsWorld" = world
        self.actor.register(self.impulse, force=True)
        self.actor.register(self.force, force=True)
        self.actor.register(self.set_simulation, force=True)
        self.actor.register(self.set_velocity_x, force=True)
        self.actor.register(self.set_velocity_y, force=True)
        self.actor.register(self.set_velocity, force=True)


    def impulse(self, direction: float, power: int):
        """this method will be registered to an Actor-Instance
        """
        self.actor.position_manager.impulse(direction, power)
    
    def force(self, direction: float, power: int):
        self.actor.position_manager.force(direction, power)

    def set_simulation(self, simulation_type: str):
        self.actor.position_manager.set_simulation(simulation_type)
        
    def set_velocity_x(self, value):
        self.actor.position_manager.set_velocity_x(value)

    def set_velocity_y(self, value):
        self.actor.position_manager.set_velocity_y(value)
        
    def set_velocity(self, value):
        self.actor.position_manager.set_velocity(value)
    @staticmethod
    def get_position_manager_class():
        return physics_position_manager.PhysicsWorldPositionManager

    @staticmethod
    def get_sensor_manager_class():
        return sensor_manager.SensorManager

    def add_to_world(self, position):
        # add actor.physics attribute with physics properties to actor
        self.actor.physics = actor_physics.ActorPhysics(self.actor, self.actor.world)
        if hasattr(self.actor, "_set_physics"):
            self.actor._set_physics()
        super().add_to_world(position)
        self.register_all_physics_collision_managers_for_actor()
        self.actor.physics._start()
        self.world.physics_actors.append(self.actor)
        if hasattr(self.actor, "on_begin_simulation"):
            self.actor.on_begin_simulation()

    def remove_actor_from_world(self, kill: bool = False):
        super().remove_actor_from_world(kill = False)
        self.actor.physics._remove_from_space()
        if self in self.world.physics_actors:
            self.world.physics_actors.remove(self)
        try:
            self.world.physics_actors.remove(self.actor)
        except ValueError:
            pass # actor not in physics actors
        
    def remove_actor_from_physics(self):
        print("remove from physics", self.actor)
        self.actor.physics._remove_from_space()
        if self in self.world.physics_actors:
            self.world.physics_actors.remove(self.actor)
        try:
            self.world.physics_actors.remove(self.actor)
        except ValueError:
            pass # actor not in physics actors
            
    def register_all_physics_collision_managers_for_actor(self):
        """Registers on__touching and on_separation-Methods to actor.
        If new_class is set, only methods with new class (e.g. on_touching_new_class are set)

        :meta private:
        """
        collision_methods = self.world.get_physics_collision_methods_for_actor(self.actor)
        for method in collision_methods:
            if method.__name__.startswith("on_touching_"):
                self.register_touching_method(method)
            elif method.__name__.startswith("on_separation_from_"):
                self.register_separate_method(method)

    def register_touching_method(self, method):
        """
        Registers on_touching_[class] method

        :meta private:
        """
        event = "begin"
        other_cls_name = method.__name__[len("on_touching_"):].lower()
        other_cls = actor_class_inspection.ActorClassInspection(self).find_actor_class_by_classname(other_cls_name)
        if self._register_physics_listener_method(method, event, other_cls):
            self.world.touching_methods.add(method)

    def register_separate_method(self, method):
        """
        Registers on_separation_from_[class] method

        :meta private:
        """
        event = "separate"
        other_cls_name = method.__name__[len("on_separation_from_"):].lower()
        other_cls = actor_class_inspection.ActorClassInspection(self).find_actor_class_by_classname(other_cls_name)
        if self._register_physics_listener_method(method, event, other_cls):
            self.world.separate_methods.add(method)

    def _register_physics_listener_method(self, method, event, other_cls):
        """Registers a physics listener method. (on touching or on_separation.)
        Called from register_touching_method and register_separate_method

        :meta private:
        """
        actor_class_inspect = actor_class_inspection.ActorClassInspection(self)
        all_actor_classes = actor_class_inspect.get_all_actor_classes()
        if other_cls not in all_actor_classes:
            return False
        else:
            subclasses_of_other_actor = actor_class_inspection.ActorClassInspection(other_cls).get_subclasses_for_cls()
            for other_subcls in set(subclasses_of_other_actor).union({other_cls}):
                # If you register a Collision with a Actor, collisions with subclasses of the actor
                # are also registered
                self._pymunk_register_collision_manager(method.__self__, other_subcls, event, method)
            return True

    def _pymunk_register_collision_manager(self, actor, other_class, event, method):
        """Adds pymunk collision handler, which is evaluated by pymunk engine.

        The event (begin, end) and the method (on_touching...) are added as data to the handler

        Args:
            actor: The actor
            other_class: The class which should be detected by collision handler
            event: The pymunk-event  (begin or separate)
            method: The method, e.g. on_touching_actor or on_separation_from_actor. Last part is a class name

        :meta private:
        """

        space = self.world.space
        actor_id = hash(actor.__class__.__name__) % ((sys.maxsize + 1) * 2)
        other_id = hash(other_class.__name__) % ((sys.maxsize + 1) * 2)
        handler = space.add_collision_handler(actor_id, other_id)
        handler.data["method"] = getattr(actor, method.__name__)
        handler.data["type"] = event
        if event == "begin":
            handler.begin = self.world.pymunk_touching_collision_listener
        if event == "separate":
            handler.separate = self.world.pymunk_separation_collision_listener
