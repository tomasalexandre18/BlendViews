bl_info = {
    "name": "BlendViews - Autostereoscopic Rendering",
    "description": "A Blender add-on to facilitate autostereoscopic rendering.",
    "author": "Audrey TELLIEZ, Enzo CORTHIER, YACINE SAOUD, Thomas TISSERAND, Alexandre TOMAS",
    "version": (1, 0),
    "blender": (5, 0, 0),
    "location": "View3D > Sidebar > Autostereoscopic Render",
    "warning": "",
    "category": "Render"
}

# add current folder to sys.path
import sys
import os

current_dir = os.path.dirname(__file__)
if current_dir not in sys.path:
    sys.path.append(current_dir)

import bpy
import Properties.init as properties
import ui.init as ui
import Operator.init as operator
from bpy.app.handlers import persistent

def register():
    properties.register()
    operator.register()
    ui.register()

    bpy.app.handlers.load_post.append(on_load)


def unregister():
    properties.unregister()
    operator.unregister()
    ui.unregister()
    bpy.app.handlers.load_post.remove(on_load)

@persistent
def on_load(dummy):
    """
    Function called after loading a .blend file to initialize properties.
    :param dummy:
    :return:
    """

    def late_init():
        scene = bpy.context.scene

        scene.RigPanelProperties.progress = 0.0
        scene.RigPanelProperties.in_render = False

        # redraw UI
        for window in bpy.context.window_manager.windows:
            for area in window.screen.areas:
                area.tag_redraw()

        return None
    # Register a timer to run late_init after loading
    bpy.app.timers.register(late_init, first_interval=0.0)

if __name__ == '__main__':
    register()