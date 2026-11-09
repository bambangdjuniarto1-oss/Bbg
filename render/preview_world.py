"""Render still diorama untuk cek tampilan: python3 render/preview_world.py -- OUT.png [az] [res]"""
import math, os, sys, time
import bpy
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lowpoly as lp, world  # noqa
args = sys.argv[sys.argv.index("--") + 1:]
out = args[0]; az = float(args[1]) if len(args) > 1 else -135; res = args[2] if len(args) > 2 else "540x960"; osc = float(args[3]) if len(args) > 3 else 290
rx, ry = map(int, res.split("x"))
lp.reset(); lp.setup_render(rx, ry, 10); world.setup_world_light()
t = time.time(); info = world.build_world(); print("build", round(time.time() - t, 1), "s, objs", len(bpy.data.objects))
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); lp._link(cam)
cam.data.type = "ORTHO"; cam.data.sensor_fit = "VERTICAL"; cam.data.ortho_scale = osc; cam.data.shift_y = 0.11; cam.data.clip_end = 3000
el = math.radians(35); a = math.radians(az); D = 600
tx, ty = -2, -4
cam.location = (tx + D * math.cos(el) * math.cos(a), ty + D * math.cos(el) * math.sin(a), D * math.sin(el))
cam.rotation_euler = (math.pi / 2 - el, 0, a + math.pi / 2)
bpy.context.scene.camera = cam
bpy.context.scene.render.filepath = out
t = time.time(); bpy.ops.render.render(write_still=True); print("render", round(time.time() - t, 1))
