bl_info = {
    "name": "Antigravity Simulation Pipeline",
    "author": "Antigravity",
    "version": (1, 0, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > Antigravity Tab",
    "description": "Procedural simulation and asset pipeline orchestrated by Antigravity",
    "category": "3D View",
}

from . import operators
from . import ui


def register():
    operators.register()
    ui.register()


def unregister():
    ui.unregister()
    operators.unregister()


if __name__ == "__main__":
    register()
