"""
Loads and Saves BVH files.
"""


import math
import re
import numpy as np
from collections import defaultdict
from net.euler import euler
from net.graph import graph


class BVH:
    def extract_joint_hierarchy(lines):
        name = []
        offsets = []
        nchannels = []
        channels = []
        parents = defaultdict(list)
        parent = None
        stack = []

        for line in lines[lines.index("HIERARCHY\n") + 1 : lines.index("MOTION\n")]:
            if "ROOT" in line:
                name.append(line.split()[1])
                stack.append(name[-1])
                continue
            if "JOINT" in line or "End Site" in line:
                if "JOINT" in line:
                    name.append(line.split()[1])
                else:
                    name.append(f"{name[-1]}_EndSite")
                parents[stack[-1]].append(name[-1])
                stack.append(name[-1])
                continue
            if "{" in line:
                continue
            if "}" in line:
                stack.pop()
                if stack:
                    parent = stack[-1]
                else:
                    parent = None
                continue
            if "OFFSET" in line:
                offsets.append([float(x) for x in line.split()[1::]])
                continue
            if "CHANNELS" in line:
                chan = line.split()
                nchannels.append(int(chan[1]))
                channels.append(chan[2::])
                continue

        return name, offsets, nchannels, channels, parents

    def extract_motion_data(lines):
        nframes = 0
        frame_time = 0
        motion_data = np.array([])

        # Motion data
        for line in lines[lines.index("MOTION\n") + 1 : :]:
            if "Frames:" in line:
                nframes = int(line.split()[1])
                continue
            elif "Frame Time:" in line:
                frame_time = float(line.split("Frame Time: ")[1])
                continue
            else:
                motion_data = np.append(motion_data, [float(x) for x in line.split()])
                continue

        return nframes, frame_time, motion_data

    def load(filename):
        """
        Reads a BVH file and constructs an animation

        Parameters
        ----------
        filename: str
            File to be opened

        Returns
        -------

        (graph)
            Object that stores all information of a BVH file in graph format
        """
        skeleton = None

        with open(filename, "r") as file:
            lines = file.readlines()
            nframes, frame_time, motion_data = BVH.extract_motion_data(lines)

            # Create graph object to store the nframes, frame_time
            skeleton = graph(filename.split("/")[-1], nframes, frame_time)

            name, offsets, nchannels, channels, parents = BVH.extract_joint_hierarchy(
                lines
            )

            skeleton.create_graph(name, offsets, channels, motion_data, parents)

        return skeleton

    def save_hierarchy(bvh_file, skeleton):
        for child in skeleton:
            if "EndSite" in child.name:
                bvh_file.write("End Site\n")
                bvh_file.write("{\n")
                bvh_file.write(
                    f"OFFSET {'{:.6f}'.format(float(child.offsets[0]))} {'{:.6f}'.format(float(child.offsets[1]))} {'{:.6f}'.format(float(child.offsets[2]))}\n"
                )
                bvh_file.write("}\n")
                return
            else:
                bvh_file.write(f"JOINT {child.name}\n")
                bvh_file.write("{\n")
                offset_string = "OFFSET"
                channels_string = "CHANNELS " + str(len(child.channels))

                for i in range(len(child.offsets)):
                    offset_string = offset_string + " {:.6f}".format(
                        float(child.offsets[i])
                    )
                offset_string = offset_string + "\n"

                for i in range(len(child.channels)):
                    channels_string = channels_string + " " + str(child.channels[i])

                channels_string = channels_string + "\n"

                bvh_file.write(offset_string)
                bvh_file.write(channels_string)

                BVH.save_hierarchy(bvh_file, child.children)
                bvh_file.write("}\n")

    def save_motion(skeleton, frame, nframes, fps, frame_data, root=True):
        prevframe = frame
        position = None
        if len(skeleton.channels) > 0:
            if len(skeleton.rotations) < nframes and len(skeleton.rotations) > 0:
                # frame = math.floor(frame % math.ceil(nframes/len(skeleton.rotations)))
                frame = math.floor(frame / 4) % len(skeleton.rotations)

            if len(skeleton.channels) > 3:
                # Get the Xpos, Ypos, Zpos
                position = skeleton.positions[frame]
                # position = [skeleton.positions[frame][0],skeleton.positions[frame][1],skeleton.positions[frame][2]]

                # Get the X, Y, Z rotations
                rotation = euler.quat2euler(skeleton.rotations[frame])
                # rotation = [skeleton.rotations[frame][0],skeleton.rotations[frame][1],skeleton.rotations[frame][2]]

                # rotation = skeleton.euler_rotation[frame]
                frame_data.append([f"{x:f}" for x in position])
                frame_data.append([f"{x:f}" for x in rotation])
            else:
                rotation = euler.quat2euler(skeleton.rotations[frame])
                frame_data.append([f"{x:f}" for x in rotation])

        for child in skeleton.children:
            if "EndSite" in child.name:
                break
            BVH.save_motion(child, prevframe, nframes, fps, frame_data, False)

    def save(filename, skeleton):
        with open(filename, "w") as bvh_file:
            # Write BVH header
            bvh_file.write("HIERARCHY\n")
            bvh_file.write("ROOT " + skeleton.root.name + "\n")
            bvh_file.write("{\n")

            offset_string = "OFFSET"
            channels_string = "CHANNELS " + str(len(skeleton.root.channels))

            for i in range(len(skeleton.root.offsets)):
                offset_string = offset_string + " {:.6f}".format(
                    float(skeleton.root.offsets[i])
                )

            offset_string = offset_string + "\n"

            for i in range(len(skeleton.root.channels)):
                channels_string = channels_string + " " + str(skeleton.root.channels[i])

            channels_string = channels_string + "\n"

            bvh_file.write(offset_string)
            bvh_file.write(channels_string)

            # bvh_file.write(f"OFFSET {'{:.6f}'.format(float(skeleton.root.offsets[0]))} {'{:.6f}'.format(float(skeleton.root.offsets[1]))} {'{:.6f}'.format(float(skeleton.root.offsets[2]))}\n")
            # bvh_file.write(f"CHANNELS {len(skeleton.root.channels)} {skeleton.root.channels[0]} {skeleton.root.channels[1]} {skeleton.root.channels[2]} {skeleton.root.channels[3]} {skeleton.root.channels[4]} {skeleton.root.channels[5]}\n")

            # Write joint hierarchy
            BVH.save_hierarchy(bvh_file, skeleton.root.children)
            bvh_file.write("}\n")

            # Write motion data
            bvh_file.write("MOTION\n")
            bvh_file.write(f"Frames: {int(skeleton.nframes)}\n")
            bvh_file.write(f"Frame Time: {float(skeleton.frame_time)}\n")

            frame_data = []

            for frame in range(skeleton.nframes):
                BVH.save_motion(
                    skeleton.root,
                    frame,
                    skeleton.nframes,
                    skeleton.frame_time,
                    frame_data,
                )
                frame_data = re.sub("[\[\],']", "", str(frame_data))
                bvh_file.write(f"{str(frame_data)}\n")
                frame_data = []
            return None
