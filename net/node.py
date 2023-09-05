"""
Object that stores joint information

Parameters
----------
value: str
    The raw bvh data
    
parent : str
    
 """


import numpy as np

from net.quat import quat


class node:
    def __init__(self, name, offsets, channels, rotations, nframes, parents=None):
        self.positions_local = []
        self.positions_global = []
        self.rotations = []
        self.velocities = []
        self.channels = channels

        if len(channels) > 3:
            joint_rotations = np.split(rotations, nframes)
            for i in range(nframes):
                self.positions_local.append(joint_rotations[i][:3])
                self.rotations.append(joint_rotations[i][3:])
            self.rotations = [quat.euler2quat(x) for x in self.rotations]
        elif len(rotations) > 0:
            self.rotations = np.split(rotations, nframes)
            self.rotations = [quat.euler2quat(x) for x in self.rotations]

        self.name = str(name)
        self.offsets = offsets
        self.children = []

        self.parent = parents
        if self.parent:
            self.parent.add_child(self)
            self.calculate_local_position()
        else:
            for index in range(len(self.positions_local)):
                self.positions_local[index] = np.matmul(
                    quat.quat2rotmat(self.rotations[index]), self.positions_local[index]
                )

    def add_child(self, item):
        self.children.append(item)

    def angular_velocities(self, q1, q2, dt):
        return (2 / dt) * np.array(
            [
                q1[0] * q2[1] - q1[1] * q2[0] - q1[2] * q2[3] + q1[3] * q2[2],
                q1[0] * q2[2] + q1[1] * q2[3] - q1[2] * q2[0] - q1[3] * q2[1],
                q1[0] * q2[3] - q1[1] * q2[2] + q1[2] * q2[1] - q1[3] * q2[0],
            ]
        )

    def calculate_velocities(self, nframes):
        for frame in range(nframes):
            if frame == 0:
                self.velocities.append(np.array([0.0, 0.0, 0.0]))
            else:
                time_interval = 1.0 / nframes
                self.velocities.append(
                    self.angular_velocities(
                        self.rotations[frame - 1], self.rotations[frame], time_interval
                    )
                )

    def calculate_local_position(self):
        for index in range(len(self.rotations)):
            try:
                self.positions_local.append(
                    np.matmul(
                        quat.quat2rotmat(self.rotations[index]),
                        self.offsets + self.parent.positions_local[index],
                    )
                )
            except:
                print()
                # print(self.parent.name)
                # print(self.name)
                # print(self.parent.positions_local)
                # print(len(self.parent.positions_local))
                # print(self.offsets + self.parent.positions_local[index])

    """
    def calculate_velocities(self, nframes):
        for frame in range(nframes):
            time_interval = 1.0 / nframes

            if frame == 0:
                self.velocities.append(np.array([0.0, 0.0, 0.0, 0.0]))
            else:
                self.velocities.append(
                    np.subtract(self.rotations[frame - 1], self.rotations[frame])
                    / time_interval,
                )
    """
