import bpy
from bpy.types import Panel

from Properties.RigPanelPropertie import RigPanelProperties


class RigPanel(Panel):
    bl_label = 'BlendViews'
    bl_idname = 'BLENDVIEWS_RIG_PANEL'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'BlendViews'

    def draw(self, context):
        layout = self.layout
        rigPanelProperties: RigPanelProperties = context.scene.RigPanelProperties

        layout.label(text="Paramétrage du rig", icon='CAMERA_DATA')

        layout.prop(rigPanelProperties, "camera_config")
        layout.prop(rigPanelProperties, "baseline_distance")
        layout.prop(rigPanelProperties, "nb_views")

        layout.separator()

        layout.prop(rigPanelProperties, "use_toe_in")

        if rigPanelProperties.use_toe_in:
            layout.prop(rigPanelProperties, "toe_in_object")

        layout.operator("blendviews.generate_rig", text="Générer le rig", icon='OUTLINER_OB_CAMERA')
        layout.operator("blendviews.render_views", text="Rendre les vues", icon='RENDER_STILL')