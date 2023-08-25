"""
Creates the spatial temporal graph of the BVH file using joints(nodes)
"""

import numpy as np
from net.node import node
from net.quat import quat


class graph:
    def __init__(self, nframes, frame_time):
        self.root = None
        self.nodes = {}
        self.nframes = int(nframes)
        self.frame_time = float(frame_time)

    def create_graph(self, joints, offsets, channels, motion_data, parents):
        counter = 0
        front_pointer = 0
        back_pointer = 0
        motion_data = np.split(motion_data, self.nframes)

        for index in range(len(joints)):
            joint_rotations = np.array([])
            if "_End" in joints[index]:
                self.nodes.update(
                    {
                        str(joints[index]): node(
                            str(joints[index]),
                            offsets[index],
                            [],
                            [],
                            self.nframes,
                            parents=list(self.nodes.values())[parents[index] - 1],
                        ),
                    }
                )
                counter += 1
                continue

            joint_channels = channels[index - counter]

            if index == 0:
                front_pointer = front_pointer + len(joint_channels)
                for i in range(self.nframes):
                    joint_rotations = np.append(
                        joint_rotations, [motion_data[i][back_pointer:front_pointer]]
                    )
                self.root = node(
                    str(joints[index]),
                    offsets[index],
                    joint_channels,
                    joint_rotations,
                    self.nframes,
                    parents=None,
                )
                self.nodes.update(
                    {
                        str(joints[index]): self.root,
                    }
                )
                back_pointer = front_pointer
                self.nodes[joints[index]].calculate_velocities(self.nframes)
            else:
                front_pointer = front_pointer + len(joint_channels)
                for i in range(self.nframes):
                    joint_rotations = np.append(
                        joint_rotations, [motion_data[i][back_pointer:front_pointer]]
                    )
                self.nodes.update(
                    {
                        str(joints[index]): node(
                            str(joints[index]),
                            offsets[index],
                            joint_channels,
                            joint_rotations,
                            self.nframes,
                            parents=list(self.nodes.values())[parents[index] - 1],
                        ),
                    }
                )
                back_pointer = front_pointer
                self.nodes[joints[index]].calculate_velocities(self.nframes)

    def calculate_global_positions(
        self, node, accumulated_transformations=np.identity(3)
    ):
        global_transform = 0
        for index in range(len(node.positions_local)):
            global_transform = np.dot(
                accumulated_transformations, quat.quat2rotmat(node.rotations[index])
            )

            global_position = np.dot(global_transform, node.positions_local[index])
            node.positions_global.append(global_position)

        for child in node.children:
            self.calculate_global_positions(child, global_transform)
