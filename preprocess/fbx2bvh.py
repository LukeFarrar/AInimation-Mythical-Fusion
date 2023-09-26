import os
import bpy
import numpy as np
from pathlib import Path
import logging


def fbx2bvh(data_path, file):
    sourcepath = data_path + "/" + file

    bvh_path = "./data/" + data_path[2:] + "/" + file.split(".fbx")[0] + ".bvh"

    directory_path = os.path.dirname(bvh_path)

    print(bvh_path)

    if not os.path.exists(directory_path):
        Path(directory_path).mkdir(parents=True, exist_ok=True)
        # os.makedirs(directory_path)
        print("Directory and all intermediate directories created:", directory_path)
    else:
        print("Directory already exists:", directory_path)

    bpy.ops.import_scene.fbx(filepath=sourcepath)

    frame_start = 9999
    frame_end = -9999
    action = bpy.data.actions[-1]
    if action.frame_range[1] > frame_end:
        frame_end = action.frame_range[1]
    if action.frame_range[0] < frame_start:
        frame_start = action.frame_range[0]

    frame_end = np.max([60, frame_end])
    bpy.ops.export_anim.bvh(
        filepath=bvh_path,
        frame_start=int(frame_start),
        frame_end=int(frame_end),
        root_transform_only=True,
    )
    bpy.data.actions.remove(bpy.data.actions[-1])
    print(data_path + "/" + file + " processed.")


def amc2bvh(data_path, file):
    sourcepath = data_path + "/" + file

    bvh_path = "./data/" + data_path[2:] + "/" + file.split(".amc")[0] + ".bvh"

    directory_path = os.path.dirname(bvh_path)

    print(bvh_path)

    if not os.path.exists(directory_path):
        Path(directory_path).mkdir(parents=True, exist_ok=True)
        # os.makedirs(directory_path)
        print("Directory and all intermediate directories created:", directory_path)
    else:
        print("Directory already exists:", directory_path)

    bpy.ops.import_scene.amc(filepath=sourcepath)

    frame_start = 9999
    frame_end = -9999
    action = bpy.data.actions[-1]
    if action.frame_range[1] > frame_end:
        frame_end = action.frame_range[1]
    if action.frame_range[0] < frame_start:
        frame_start = action.frame_range[0]

    frame_end = np.max([60, frame_end])
    bpy.ops.export_anim.bvh(
        filepath=bvh_path,
        frame_start=int(frame_start),
        frame_end=int(frame_end),
        root_transform_only=True,
    )
    bpy.data.actions.remove(bpy.data.actions[-1])
    print(data_path + "/" + file + " processed.")


def find_fbx_files(directory):
    fbx_files = []

    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(".fbx"):
                fbx_files.append(os.path.join(root, file))

    return fbx_files


def file_conversion():
    data_path = "./Datasets/"
    fbx_file_paths = find_fbx_files(data_path)

    logging.info("FBX FILES:")
    for fbx_file_path in fbx_file_paths:
        fbx_dir, fbx_file = os.path.split(fbx_file_path)
        logging.info(f"FOUND: {fbx_file}")

        try:
            fbx2bvh(data_path=fbx_dir, file=fbx_file)
        except:
            logging.error(f"UNABLE TO CONVERT: {fbx_dir + '/' + fbx_file} ")
