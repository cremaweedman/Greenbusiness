"""GreenBusiness Blender scene bootstrap.

Run inside Blender's scripting workspace or:
    blender --background --python tools/blender/greenbusiness_scene_setup.py

This script does not create game art. It normalizes scene settings and
creates canonical collection/camera/light scaffolding for the starter slot.
"""

import bpy
from mathutils import Vector


STATE_COLLECTIONS = [
    "STATE_EMPTY",
    "STATE_PLANTED",
    "STATE_GROWING",
    "STATE_READY",
    "STATE_LOCKED",
    "STATE_ATTENTION",
    "STATE_BOOSTED",
]


def ensure_collection(name: str, parent=None):
    collection = bpy.data.collections.get(name)
    if collection is None:
        collection = bpy.data.collections.new(name)
    parent = parent or bpy.context.scene.collection
    if collection.name not in {c.name for c in parent.children}:
        parent.children.link(collection)
    return collection


def ensure_empty(name: str):
    obj = bpy.data.objects.get(name)
    if obj is None:
        obj = bpy.data.objects.new(name, None)
        bpy.context.scene.collection.objects.link(obj)
    return obj


def ensure_camera():
    camera_obj = bpy.data.objects.get("CAM_SLOT_MASTER")
    if camera_obj is None:
        data = bpy.data.cameras.new("CAM_SLOT_MASTER")
        camera_obj = bpy.data.objects.new("CAM_SLOT_MASTER", data)
        bpy.context.scene.collection.objects.link(camera_obj)

    # Sensible starting point only. Freeze after SLOT-001 art approval.
    camera_obj.location = (4.6, -5.8, 4.4)
    camera_obj.data.lens = 58
    camera_obj.data.sensor_width = 36

    target = Vector((0.0, 0.0, 1.0))
    direction = target - camera_obj.location
    camera_obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.camera = camera_obj
    return camera_obj


def ensure_area_light(name, location, energy, size):
    obj = bpy.data.objects.get(name)
    if obj is None:
        data = bpy.data.lights.new(name=name, type="AREA")
        obj = bpy.data.objects.new(name, data)
        bpy.context.scene.collection.objects.link(obj)
    obj.location = location
    obj.data.energy = energy
    obj.data.shape = "DISK"
    obj.data.size = size
    return obj


def aim_at(obj, target=(0.0, 0.0, 0.9)):
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def setup_render():
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.render.resolution_x = 1536
    scene.render.resolution_y = 1536
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = True
    scene.render.use_file_extension = True

    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0

    scene.view_settings.look = "AgX - Medium High Contrast"


def setup_structure():
    root = ensure_empty("ROOT_SLOT_STARTER")
    root.location = (0.0, 0.0, 0.0)
    root.scale = (1.0, 1.0, 1.0)

    states_root = ensure_collection("SLOT_STATES")
    for name in STATE_COLLECTIONS:
        ensure_collection(name, parent=states_root)


def setup_lighting():
    key = ensure_area_light("LIGHT_KEY", (3.5, -4.0, 5.5), 900, 4.0)
    fill = ensure_area_light("LIGHT_FILL", (-4.0, -1.0, 3.0), 450, 5.0)
    rim = ensure_area_light("LIGHT_RIM", (1.0, 4.0, 4.5), 700, 3.0)

    for light in (key, fill, rim):
        aim_at(light)


def main():
    setup_render()
    setup_structure()
    ensure_camera()
    setup_lighting()
    print("GreenBusiness starter-slot scene scaffold ready.")


if __name__ == "__main__":
    main()
