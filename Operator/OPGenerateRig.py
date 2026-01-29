from bpy.types import Operator
import bpy
import mathutils


class OPGenerateRig(Operator):
    bl_idname = "blendviews.generate_rig"
    bl_label = "Generate Camera Rig"
    bl_description = "Generate a camera rig based on the specified parameters"

    def execute(self, context):
        rigPanelProperties = context.scene.RigPanelProperties

        base_camera = rigPanelProperties.camera_config
        baseline_distance = rigPanelProperties.baseline_distance
        nb_views = rigPanelProperties.nb_views
        use_toe_in = rigPanelProperties.use_toe_in
        toe_in_object = rigPanelProperties.toe_in_object

        if base_camera is None:
            self.report({'ERROR'}, "No base camera selected.")
            return {'CANCELLED'}

        # Logic to generate the camera rig goes here
        # This is a placeholder for the actual implementation
        self.report({'INFO'}, f"Generating rig with {nb_views} views, baseline {baseline_distance}, "
                              f"{'using toe-in' if use_toe_in else 'not using toe-in'}.")

        cam_collection = bpy.data.collections.get("AutoStereo_Cameras")
        if not cam_collection:
            cam_collection = bpy.data.collections.new("AutoStereo_Cameras")
            context.scene.collection.children.link(cam_collection)
        else:
            # Clear existing cameras
            for obj in cam_collection.objects:
                bpy.data.objects.remove(obj, do_unlink=True)

        # remove empty rig object
        existing_rig = bpy.data.objects.get("AutoStereo_Rig")
        if existing_rig:
            bpy.data.objects.remove(existing_rig, do_unlink=True)

        rig_empty = bpy.data.objects.new("AutoStereo_Rig", None)
        rig_empty.empty_display_type = 'PLAIN_AXES'
        rig_empty.location = base_camera.location
        rig_empty.rotation_euler = base_camera.rotation_euler
        context.scene.collection.objects.link(rig_empty)

        quat = base_camera.rotation_euler.to_quaternion()
        right = quat @ mathutils.Vector((1, 0, 0))

        for i in range(nb_views):
            t = i / (nb_views - 1)  # normalized [0, 1]
            offset = (t - 0.5) * baseline_distance

            cam_data = bpy.data.cameras.new(name=f"AutoStereo_Cam_{i+1:02d}")
            cam_obj = bpy.data.objects.new(name=f"AutoStereo_Cam_{i+1:02d}", object_data=cam_data)
            cam_collection.objects.link(cam_obj)

            cam_obj.parent = rig_empty

            cam_obj.location = mathutils.Vector((offset, 0, 0))
            cam_obj.rotation_euler = (0, 0, 0)

            # copy base camera settings
            cam_data.lens = base_camera.data.lens
            cam_data.sensor_width = base_camera.data.sensor_width
            cam_data.sensor_height = base_camera.data.sensor_height
            cam_data.clip_start = base_camera.data.clip_start
            cam_data.clip_end = base_camera.data.clip_end

            if use_toe_in and toe_in_object:
                constraint = cam_obj.constraints.new(type='TRACK_TO')
                constraint.target = toe_in_object
                constraint.track_axis = 'TRACK_NEGATIVE_Z'
                constraint.up_axis = 'UP_Y'

        return {'FINISHED'}