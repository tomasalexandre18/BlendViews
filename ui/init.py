import ui.RigPanel as RigPanel
import bpy

elements_to_register = [
    RigPanel.RigPanel
]

def register():
    for elem in elements_to_register:
        bpy.utils.register_class(elem)

def unregister():
    for elem in elements_to_register:
        bpy.utils.unregister_class(elem)