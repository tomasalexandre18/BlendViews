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

def register():
    properties.register()
    operator.register()
    ui.register()


def unregister():
    properties.unregister()
    operator.unregister()
    ui.unregister()

if __name__ == '__main__':
    register()