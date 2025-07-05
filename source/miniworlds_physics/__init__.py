import inspect
import os
import sys
from miniworlds_physics.physics_world import PhysicsWorld

# __import__('pkg_resources').declare_namespace(__name__)
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

__all__ = []


__all__.append(PhysicsWorld.__name__)
__all__.append("ABC")
