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

import bpy

def register():
    print("Registering Autostereoscopic rendering add-on")

def unregister():
    print("Unregistering Autostereoscopic rendering add-on")

if __name__ == '__main__':
    register()
