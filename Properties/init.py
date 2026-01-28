import Properties.RigPanelPropertie as RigPanelPropertie
from bpy.props import PointerProperty, FloatProperty
import bpy


elements_to_register = [
    RigPanelPropertie.RigPanelProperties,
]

def register():
    for elem in elements_to_register:
        bpy.utils.register_class(elem)

    bpy.types.Scene.RigPanelProperties = PointerProperty(
        type=RigPanelPropertie.RigPanelProperties,
    )

    bpy.types.Scene.cam_t = FloatProperty(
        name="Camera T",
        description="Camera linear position",
        default=0.0,
        min=-1.0,
        max=1.0
    )

def unregister():
    for elem in elements_to_register:
        bpy.utils.unregister_class(elem)

    del bpy.types.Scene.autostereo_props
    del bpy.types.Scene.cam_t