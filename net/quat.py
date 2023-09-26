import numpy as np
from scipy.spatial.transform import Rotation


class quat:
    def __init__(self, w, x, y, z):
        self.w = w
        self.x = x
        self.y = y
        self.z = z

    def identity():
        return np.array([0, 0, 0, 1])

    def euler2quat(rotations, channels):
        roll = float(rotations[0])  # z
        pitch = float(rotations[1])  # y
        yaw = float(rotations[2])  # x

        r = Rotation.from_euler("xyz", [roll, pitch, yaw], degrees=True)

        return r.as_quat()

        """
        if channels == ["Zrotation", "Yrotation", "Xrotation"]:
            roll = float(rotations[0])  # z
            pitch = float(rotations[1])  # y
            yaw = float(rotations[2])  # x
        elif channels == ["Xrotation", "Yrotation", "Zrotation"]:
            roll = float(rotations[2])  # z
            pitch = float(rotations[1])  # y
            yaw = float(rotations[0])  # x
        
        qx = np.sin(roll / 2) * np.cos(pitch / 2) * np.cos(yaw / 2) - np.cos(
            roll / 2
        ) * np.sin(pitch / 2) * np.sin(yaw / 2)
        qy = np.cos(roll / 2) * np.sin(pitch / 2) * np.cos(yaw / 2) + np.sin(
            roll / 2
        ) * np.cos(pitch / 2) * np.sin(yaw / 2)
        qz = np.cos(roll / 2) * np.cos(pitch / 2) * np.sin(yaw / 2) - np.sin(
            roll / 2
        ) * np.sin(pitch / 2) * np.cos(yaw / 2)
        qw = np.cos(roll / 2) * np.cos(pitch / 2) * np.cos(yaw / 2) + np.sin(
            roll / 2
        ) * np.sin(pitch / 2) * np.sin(yaw / 2)

        return [qx, qy, qz, qw]
        # return quat(w, x, y, z)
        """

    def quat2rotmat(Q):
        # Extract the values from Q
        q0 = Q[0]
        q1 = Q[1]
        q2 = Q[2]
        q3 = Q[3]

        # First row of the rotation matrix
        r00 = 2 * (q0 * q0 + q1 * q1) - 1
        r01 = 2 * (q1 * q2 - q0 * q3)
        r02 = 2 * (q1 * q3 + q0 * q2)

        # Second row of the rotation matrix
        r10 = 2 * (q1 * q2 + q0 * q3)
        r11 = 2 * (q0 * q0 + q2 * q2) - 1
        r12 = 2 * (q2 * q3 - q0 * q1)

        # Third row of the rotation matrix
        r20 = 2 * (q1 * q3 - q0 * q2)
        r21 = 2 * (q2 * q3 + q0 * q1)
        r22 = 2 * (q0 * q0 + q3 * q3) - 1

        # 3x3 rotation matrix
        rot_matrix = np.array([[r00, r01, r02], [r10, r11, r12], [r20, r21, r22]])

        return rot_matrix
