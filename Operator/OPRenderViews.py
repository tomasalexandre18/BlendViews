import os

from bpy.types import Operator
import bpy
import mathutils
import subprocess

def show_message(message, title="Info", icon='INFO'):
    def draw(self, context):
        self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)

def redraw_ui(context):
    for area in context.window.screen.areas:
        if area.type == 'VIEW_3D':
            for region in area.regions:
                if region.type == 'UI':
                    region.tag_redraw()

def render(frame, cam_index, p):
    if cam_index < 0:
        p.progress = 100.0
        print('-'*20 + " END RENDERING " + '-'*20)
        p.in_render = False
        redraw_ui(bpy.context)
        show_message("Rendering completed successfully!", title="Render Complete", icon='CHECKMARK')
        return
    blend_file = bpy.data.filepath
    blender = bpy.app.binary_path
    output_path = "//renders/view_{:03d}_frame_{:04d}.png"

    p.progress = 100.0 * (p.nb_views - cam_index-1) / p.nb_views
    redraw_ui(bpy.context)

    cmd = [
        blender,
        "-b",
        blend_file,
        "-P",
        os.path.join(os.path.dirname(__file__), "..", "RenderFrame", "script_rendu_arg.py"),
        "--",
        str(frame),
        str(cam_index+1),
        output_path.format(cam_index+1, frame)
    ]

    print(f"Starting render of camera {cam_index+1} for frame {frame}: {' '.join(cmd)}")

    sub = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    bpy.app.timers.register(lambda: check_render(sub, (frame, cam_index-1, p)), first_interval=0.5)

def check_render(proc, data):
    if proc.poll() is None:
        return 0.5  # recheck dans 0.5s
    else:
        if proc.returncode != 0:
            print(f"Render of camera {data[1]+2} failed.")
            # get output and error
            out, err = proc.communicate()
            print("Output:", out.decode())
            print('-'*20 + " END RENDERING " + '-'*20)
            data[2].in_render = False
            redraw_ui(bpy.context)
            show_message(f"Rendering failed for camera {data[1]+2}.", title="Render Failed", icon='ERROR')
            return None
        else:
            print(f"Render of camera {data[1]+2} completed successfully.")
        render(*data)
        return None  # stop timer



class OPRenderViews(Operator):
    bl_idname = "blendviews.render_views"
    bl_label = "Render Stereo Views"
    bl_description = "Render all stereo views in the generated rig"

    def execute(self, context):
        # save the blend file

        rigPanelProperties = context.scene.RigPanelProperties

        if rigPanelProperties.in_render:
            self.report({'WARNING'}, "Rendering is already in progress.")
            return {'CANCELLED'}
        rigPanelProperties.in_render = True
        bpy.ops.wm.save_mainfile()
        nb_views = rigPanelProperties.nb_views
        wm = context.window_manager
        wm.progress_begin(0, nb_views)
        print('-'*20 + " START RENDERING " + '-'*20)
        render(frame=context.scene.frame_current, cam_index=nb_views - 1, p=rigPanelProperties)
        return {'FINISHED'}
