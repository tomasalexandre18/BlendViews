# Blender Add-on Template
# Contributor(s): Aaron Powell (aaron@lunadigital.tv)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import bpy
from bpy.types import Scene

from bpy.types import Panel, Operator, PropertyGroup
from bpy.props import (
    PointerProperty,
    FloatProperty,
    IntProperty,
    BoolProperty,
)

#
# Add additional functions or classes here
#

# This is where you assign any variables you need in your script. Note that they
# won't always be assigned to the Scene object but it's a good place to start.

class AutoStereoProperties(PropertyGroup):

    main_camera: PointerProperty(
        name="Caméra principale",
        type=bpy.types.Object,
        description="Caméra de référence",
        poll=lambda self, obj: obj.type == 'CAMERA'
    )

    baseline: FloatProperty(
        name="Baseline (m)",
        description="Écart total entre les caméras",
        default=0.065,
        min=0.0,
        unit='LENGTH'
    )

    image_count: IntProperty(
        name="Nombre d'images",
        description="Nombre de vues à générer",
        default=5,
        min=2
    )

    use_toe_in: BoolProperty(
        name="Toe-in",
        description="Converger les caméras vers un point",
        default=False
    )

    convergence_object: PointerProperty(
        name="Objet de convergence",
        type=bpy.types.Object,
        description="Objet visé par les caméras (toe-in)"
    )

    use_image_shift: BoolProperty(
        name="Image Shift",
        description="Utiliser le décalage d'image plutôt que le toe-in",
        default=False
    )

    screen_offset: FloatProperty(
        name="Décalage d'écran",
        description="Décalage horizontal de l'écran pour ajuster la convergence",
        default=0.0,
        unit='LENGTH'
    )

    screen_pitch: FloatProperty(
        name="Pitch de l'écran",
        description="Distance entre les lentilles de l'écran autostéréoscopique",
        default=0.0005,
        unit='LENGTH'
    )

    screen_dpi: FloatProperty(
        name="DPI de l'écran",
        description="Résolution de l'écran en points par pouce",
        default=300.0,
        min=1.0
    )

import mathutils

class AUTOSTEREO_OT_generate_rig(Operator):
    bl_idname = "autostereo.generate_rig"
    bl_label = "Générer le rig"
    bl_description = "Créer le rig de caméras autostéréoscopiques"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.autostereo_props

        if not props.main_camera:
            self.report({'ERROR'}, "Aucune caméra principale sélectionnée")
            return {'CANCELLED'}

        # Create collection for cameras
        cam_collection = bpy.data.collections.get("AutoStereo_Cameras")
        if not cam_collection:
            cam_collection = bpy.data.collections.new("AutoStereo_Cameras")
            context.scene.collection.children.link(cam_collection)
        else:
            # Clear existing cameras
            for obj in cam_collection.objects:
                bpy.data.objects.remove(obj, do_unlink=True)

        # remove empty rig if exists
        existing_rig = bpy.data.objects.get("AutoStereo_Rig")
        if existing_rig:
            bpy.data.objects.remove(existing_rig, do_unlink=True)

        main_cam = props.main_camera
        scene = context.scene

        # Create rig empty
        rig = bpy.data.objects.new("AutoStereo_Rig", None)
        rig.empty_display_type = 'PLAIN_AXES'
        rig.location = main_cam.location
        rig.rotation_euler = main_cam.rotation_euler
        scene.collection.objects.link(rig)

        # Camera orientation vectors
        quat = main_cam.matrix_world.to_quaternion()
        right = quat @ mathutils.Vector((1, 0, 0))

        baseline = props.baseline
        count = props.image_count

        for i in range(count):
            t = i / (count - 1)
            offset = (t - 0.5) * baseline

            cam_data = bpy.data.cameras.new(f"AutoStereo_Cam_{i + 1:02d}")
            cam = bpy.data.objects.new(cam_data.name, cam_data)
            cam_collection.objects.link(cam)

            # Parent to rig
            cam.parent = rig

            # Local offset
            cam.location = mathutils.Vector((offset, 0, 0))
            cam.rotation_euler = (0, 0, 0)

            # Copy optical properties
            cam_data.lens = main_cam.data.lens
            cam_data.sensor_width = main_cam.data.sensor_width
            cam_data.clip_start = main_cam.data.clip_start
            cam_data.clip_end = main_cam.data.clip_end

            if props.use_toe_in and props.convergence_object:
                c = cam.constraints.new('TRACK_TO')
                c.target = props.convergence_object
                c.track_axis = 'TRACK_NEGATIVE_Z'
                c.up_axis = 'UP_Y'

            elif props.use_image_shift:
                # Physically correct shift
                cam_data.shift_x = offset / cam_data.sensor_width

        return {'FINISHED'}

class AUTOSTEREO_OT_render_frame(Operator):
    bl_idname = "autostereo.render_frame"
    bl_label = "Rendre la frame"
    bl_description = "Rendre la frame actuelle pour toutes les caméras du rig"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.autostereo_props

        cam_collection = bpy.data.collections.get("AutoStereo_Cameras")
        if not cam_collection:
            self.report({'ERROR'}, "Aucune collection de caméras AutoStereo trouvée")
            return {'CANCELLED'}

        original_camera = context.scene.camera
        original_cam_t = context.scene.cam_t

        for i, cam in enumerate(cam_collection.objects):
            context.scene.camera = cam
            context.scene.render.filepath = f"//tmp_render/autostereo_frame_{context.scene.frame_current:04d}_cam_{i + 1:02d}.png"
            context.scene.cam_t = (i / (len(cam_collection.objects) - 1)) * 2 - 1  # -1 to 1 range
            bpy.ops.render.render(write_still=True)

        context.scene.camera = original_camera
        context.scene.cam_t = original_cam_t

        # calculate colone image after rendering all views

        # import all images as numPy arrays
        import numpy as np
        import os

        image_arrays = np.empty((props.image_count, context.scene.render.resolution_y, context.scene.render.resolution_x, 4), dtype=np.uint8)
        for i in range(props.image_count):
            filepath = f"//tmp_render/autostereo_frame_{context.scene.frame_current:04d}_cam_{i + 1:02d}.png"
            abs_path = bpy.path.abspath(filepath)

            img = bpy.data.images.load(abs_path)

            # Récupération des pixels (float32, RGBA, 0..1)
            pixels = np.empty(len(img.pixels), dtype=np.float32)
            img.pixels.foreach_get(pixels)

            # Reshape → (H, W, 4)
            pixels = pixels.reshape(
                img.size[1],
                img.size[0],
                4
            )

            # Conversion float [0–1] → uint8 [0–255]
            image_arrays[i] = (pixels * 255).astype(np.uint8)

            # Libérer l’image si tu n’en as plus besoin
            bpy.data.images.remove(img)

        final_image = np.zeros_like(image_arrays[0])

        N = props.image_count
        P = props.screen_pitch * (props.screen_dpi / 0.0254)  # convert pitch from meters to pixels
        O = props.screen_offset * (props.screen_dpi / 0.0254)  # convert offset from meters to pixels
        if P <= 0:
            raise ValueError(f"Invalid pitch: {P}")
        self.report({'INFO'}, f"Combinaison des images avec N={N}, P={P}, O={O}")

        period = P * N

        # calcul_index_vue(x) = floor(((x + O) mod (P × N)) / P)
        for x in range(context.scene.render.resolution_x):
            local_x = (x + O) % period
            view_index = int(local_x // P)
            view_index = min(max(view_index, 0), N - 1)
            final_image[:, x, :] = image_arrays[view_index, :, x, :]
        # Create final image
        final_img = bpy.data.images.new("AutoStereo_Final", width=context.scene.render.resolution_x, height=context.scene.render.resolution_y)
        # Flatten and convert to float [0..1]
        flat_pixels = (final_image.flatten().astype(np.float32)) / 255.0
        final_img.pixels.foreach_set(flat_pixels)
        final_filepath = f"//renders/autostereo_final_frame_{context.scene.frame_current:04d}.png"
        os.makedirs(bpy.path.abspath("//renders/"), exist_ok=True)
        final_img.filepath_raw = bpy.path.abspath(final_filepath)
        final_img.file_format = 'PNG'
        final_img.save()

        self.report({'INFO'}, f"Rendu autostéréoscopique sauvegardé : {final_filepath}")
        # open the image in previewer
        bpy.ops.image.open(filepath=bpy.path.abspath(final_filepath))

        return {'FINISHED'}
class AUTOSTEREO_PT_main_panel(Panel):
    bl_label = "AutoStéréoscopie"
    bl_idname = "AUTOSTEREO_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'AutoStereo'

    def draw(self, context):
        layout = self.layout
        props = context.scene.autostereo_props

        layout.label(text="Paramétrage du rig", icon='CAMERA_DATA')

        layout.prop(props, "main_camera")
        layout.prop(props, "baseline")
        layout.prop(props, "image_count")

        layout.separator()

        layout.prop(props, "use_toe_in")

        if props.use_toe_in:
            layout.prop(props, "convergence_object")

        layout.separator()

        layout.prop(props, "use_image_shift")

        layout.separator()
        layout.operator("autostereo.generate_rig", icon='OUTLINER_COLLECTION')

        layout.separator()

        # slider for cam_t (to visualize camera position)
        layout.prop(context.scene, "cam_t", slider=True)

        # ask for pitch and offset before rendering
        layout.prop(props, "screen_dpi")
        layout.prop(props, "screen_pitch")
        layout.prop(props, "screen_offset")
        layout.operator("autostereo.render_frame", icon='RENDER_STILL')


# =========================================================
# Register / Unregister
# =========================================================

classes = (
    AutoStereoProperties,
    AUTOSTEREO_OT_generate_rig,
    AUTOSTEREO_PT_main_panel,
    AUTOSTEREO_OT_render_frame,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.autostereo_props = PointerProperty(
        type=AutoStereoProperties
    )

    bpy.types.Scene.cam_t = FloatProperty(
        name="Camera T",
        description="Camera linear position",
        default=0.0,
        min=-1.0,
        max=1.0
    )


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.autostereo_props

    del bpy.types.Scene.cam_t
