bl_info = {
    "name": "Autostereoscopic rendering",
    "description": "A Blender add-on to facilitate autostereoscopic rendering.",
    "author": "TOMAS Alexandre",
    "version": (1, 0),
    "blender": (5, 0, 0),
    "location": "View3D > Sidebar > Autostereoscopic Render",
    "warning": "", # used for warning icon and text in add-ons panel
    "category": "Render"
}

import bpy

#
# Add additional functions here
#

def register():
    from . import properties
    from . import ui
    properties.register()
    ui.register()

def unregister():
    from . import properties
    from . import ui
    properties.unregister()
    ui.unregister()

if __name__ == '__main__':
    register()
