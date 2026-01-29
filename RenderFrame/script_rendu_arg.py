import sys
import bpy
import traceback

def custom_excepthook(exc_type, exc_value, exc_traceback):
    print("-"*20 + " ERROR " + "-"*20)
    print("An error occurred during rendering:")
    traceback.print_exception(exc_type, exc_value, exc_traceback, file=sys.stdout)
    print('-'*20 + " END ERROR " + '-'*20)
    sys.exit(1)

sys.excepthook = custom_excepthook

""" Argument are frame, cam_id, output_path"""
frame = int(sys.argv[-3])
cam_id = int(sys.argv[-2])
output_path = sys.argv[-1]

cam_collection = bpy.data.collections.get("AutoStereo_Cameras")
if not cam_collection:
    print("No camera rig found. Please generate the rig first.")
    sys.exit(1)

original_camera = bpy.context.scene.camera
bpy.context.scene.frame_set(frame)
cam_name = f"AutoStereo_Cam_{cam_id:02d}"
cam_obj = cam_collection.objects.get(cam_name)

if cam_obj is None:
    print(f"Camera {cam_name} not found in the rig.")
    sys.exit(1)

# set cam_t [-1, 1]
bpy.context.scene.cam_t = ((cam_id-1) / (len(cam_collection.objects) - 1)) * 2 - 1
bpy.context.scene.camera = cam_obj
# Set output file path
bpy.context.scene.render.filepath = output_path
# Render the scene
bpy.ops.render.render(
    'INVOKE_DEFAULT',
    write_still=True,
)