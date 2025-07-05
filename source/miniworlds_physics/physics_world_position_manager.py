from math import radians, degrees
from typing import Tuple

import miniworlds.worlds.manager.position_manager as position_manager
from miniworlds.base.exceptions import (
    PhysicsSimulationTypeError,
)
from miniworlds.actors import actor as actor_mod


class PhysicsWorldPositionManager(position_manager.Positionmanager):
    def __init__(self, actor: "actor_mod.Actor", world, position):
        super().__init__(actor, world, position)

    def set_position(
        self, value: Tuple[float, float]
    ) -> Tuple[float, float]:
        pos = super().set_position(value)
        if hasattr(self.actor, "physics"):
            self.actor.physics.dirty = 1
        return pos

    def set_center(self, value):
        pos = super().set_center(value)
        if hasattr(self.actor, "physics"):
            self.actor.physics.dirty = 1
        return pos

    def set_size(self, value, scale=False):
        super().set_size(value, scale)
        if hasattr(self.actor, "physics"):
            self.actor.physics.dirty = 1

    def move_to(self, position: Tuple[float, float]):
        super().move_to(position)
        if hasattr(self.actor, "physics"):
            self.actor.physics.reload()

    def get_direction(self):
        return self._direction

    def set_direction(self, value):
        if hasattr(self.actor, "physics") and self.actor.physics.body:
            pymunk_direction = self.get_pymunk_direction(value)
            self.actor.physics.body.angle = pymunk_direction
            super().set_direction((value + 360) % 360)
        else:
            super().set_direction(value)

    def get_pymunk_direction_from_miniworlds(self):
        mwm_direction = self._direction
        return self.get_pymunk_direction(mwm_direction)

    def get_pymunk_direction(self, value):
        mwm_direction = (value + 360) % 360
        direction = radians(mwm_direction)
        return direction

    def set_mwm_direction_from_pymunk(self):
        pymunk_dir_in_degrees = degrees(self.actor.physics.body.angle)
        mwm_direction = (pymunk_dir_in_degrees + 360) % 360
        super().set_direction(mwm_direction)

    def impulse(self, direction: float, power: int):
        self.actor.physics.impulse_in_direction(direction, power)

    def force(self, direction: float, power: int):
        self.actor.physics.force_in_direction(direction, power)

    def set_simulation(self, simulation_type: str):
        if simulation_type in ["simulated", "manual", "static", None]:
            self.actor.physics.simulation = simulation_type
            self.actor.physics.reload()
        else:
            raise PhysicsSimulationTypeError()

    def set_velocity_y(self, value):
        self.actor.physics.velocity_y = value

    def set_velocity_x(self, value):
        self.actor.physics.velocity_x = value

    def set_velocity(self, value):
        self.actor.physics.velocity_x, self.actor.physics.velocity_y = (
            value[0],
            value[1],
        )

    def self_remove(self):
        self.actor.physics._remove_from_space()
