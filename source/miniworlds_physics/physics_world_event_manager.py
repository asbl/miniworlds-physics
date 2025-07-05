import miniworlds.tools.inspection as inspection
import miniworlds.worlds.manager.event_manager as event_manager
from miniworlds.actors import actor as actor_mod
from miniworlds.tools import actor_class_inspection
from miniworlds_physics import (
    physics_world_connector as physics_world_connector_mod,
)


class PhysicsWorldEventManager(event_manager.EventManager):
    """Adds on_touching and on separation events"""

    @classmethod
    def setup_event_list(cls):
        super().setup_event_list()
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
        cls.actor_class_events["on_touching"] = touching_actor_methods
        cls.actor_class_events["on_separation"] = separation_actor_methods
        cls.fill_event_sets()

    def register_event(self, member, instance):
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
