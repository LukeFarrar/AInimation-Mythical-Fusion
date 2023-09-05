"""
Loads and Saves BVH files.
"""


import numpy as np

from net.graph import graph


class BVH:
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
            skeleton = graph(nframes, frame_time)

            name, offsets, nchannels, channels, parents = BVH.extract_joint_hierarchy(
                lines
            )

            skeleton.create_graph(name, offsets, channels, motion_data, parents)

        return skeleton

    def save():
        """
        Saves an Animation to file as BVH

        Parameters
        ----------
        filename: str
            File to be saved to

        anim : Animation
            Animation to save

        names : [str]
            List of joint names

        order : str
            Optional Specifier for joint order.
            Given as string E.G 'xyz', 'zxy'

        frametime : float
            Optional Animation Frame time

        positions : bool
            Optional specfier to save bone
            positions for each frame

        orients : bool
            Multiply joint orients to the rotations
            before saving.

        """
        return None

    def extract_joint_hierarchy(lines):
        name = []
        offsets = []
        nchannels = []
        channels = []
        parents = {}
        parent = None
        stack = []

        for line in lines[lines.index("HIERARCHY\n") + 1 : lines.index("MOTION\n")]:
            if "ROOT" in line:
                name.append(line.split()[1])
                stack.append(name[-1])
                continue
            if "JOINT" in line or "End" in line:
                if "JOINT" in line:
                    name.append(line.split()[1])
                else:
                    name.append(f"{name[-1]}_End")
                if parent:
                    parents.update({parent: name[-1]})
                stack.append(name[-1])
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

        print(parents)
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
