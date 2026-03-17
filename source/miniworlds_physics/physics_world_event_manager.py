import miniworlds.tools.inspection as inspection
import miniworlds.worlds.manager.event_manager as event_manager
from miniworlds.actors import actor as actor_mod
from miniworlds.tools import actor_class_inspection
from miniworlds_physics import (
    physics_world_connector as physics_world_connector_mod,
)


class PhysicsWorldEventManager(event_manager.EventManager):
    """Adds on_touching and on separation events"""

    def __init__(self, world):
        super().__init__(world)
        self._sync_physics_event_definition()

    def _sync_physics_event_definition(self):
        self.definition.update()
        touching_actor_methods = []
        separation_actor_methods = []
        for actor_cls in actor_class_inspection.ActorClassInspection(
            actor_mod.Actor
        ).get_subclasses_for_cls():
            touching_actor_methods.append("on_touching_" + actor_cls.__name__.lower())
        for actor_cls in actor_class_inspection.ActorClassInspection(
            actor_mod.Actor
        ).get_subclasses_for_cls():
            separation_actor_methods.append(
                "on_separation_from_" + actor_cls.__name__.lower()
            )
        self.definition.actor_class_events["on_touching"] = touching_actor_methods
        self.definition.actor_class_events["on_separation"] = separation_actor_methods
        self.definition.fill_event_sets()

    def can_register_to_actor(self, method):
        self._sync_physics_event_definition()
        return method.__name__ in self.definition.actor_class_events_set

    def register_event(self, member, instance):
        self._sync_physics_event_definition()
        super().register_event(member, instance)
        method = inspection.Inspection(instance).get_instance_method(member)
        if member.startswith("on_touching_"):
            connector = physics_world_connector_mod.PhysicsWorldConnector(
                self.world, instance
            )
            connector.register_touching_method(method)
        elif member.startswith("on_separation_from_"):
            connector = physics_world_connector_mod.PhysicsWorldConnector(
                self.world, instance
            )
            connector.register_separate_method(method)

    def act_all(self):
        """Handles acting of actors - Calls the physics-simulation in each frame.

        :meta private:
        """
        super().act_all()
        self.world.simulate_all_physics_actors()