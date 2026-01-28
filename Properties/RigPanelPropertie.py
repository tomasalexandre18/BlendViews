from bpy.props import (
    PointerProperty,
    FloatProperty,
    IntProperty,
    BoolProperty
)
import bpy


class RigPanelProperties(bpy.types.PropertyGroup):
    """
    Properties for the Rig Panel in the Autostereoscopic Rendering add-on.
    """

    camera_config: PointerProperty(
        name="Camera for Rig Configuration",
        type=bpy.types.Object,
        description="Select the base camera to configure the rig",
        poll=lambda self, obj: obj.type == 'CAMERA'
    )
    """
    Camera Object Selection: selection of a base camera for the configuration of the rig.
    """

    baseline_distance: FloatProperty(
        name="Baseline Distance",
        description="Distance between the left and right cameras in the rig",
        default=0.065,
        min=0.0,
        unit='LENGTH'
    )
    """
    Baseline Distance: distance between the left and right cameras in the rig.
    """

    nb_views: IntProperty(
        name="Number of Views",
        description="Number of views to generate in the rig",
        default=5,
        min=2,
        max=20
    )
    """
    Number of Views: number of views to generate in the rig.
    """

    use_toe_in: BoolProperty(
        name="Use Toe In",
        default=False,
        description="Use Toe In"
    )
    """
    Use Toe In: whether to use the toe-in method for camera convergence.
    """

    toe_in_object: PointerProperty(
        name="Convergence Object",
        type=bpy.types.Object,
        description="Object to converge the cameras on when using toe-in",
    )
    """
    Convergence Object: object to converge the cameras on when using toe-in.
    """

