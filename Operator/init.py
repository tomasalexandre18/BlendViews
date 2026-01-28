import Operator.OPGenerateRig as OpGenerateRig
import bpy

elements_to_register = [
    OpGenerateRig.OPGenerateRig,
]

def register():
    for elem in elements_to_register:
        bpy.utils.register_class(elem)


def unregister():
    for elem in elements_to_register:
        bpy.utils.unregister_class(elem)
