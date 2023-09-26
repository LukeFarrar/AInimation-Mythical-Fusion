import numpy as np
from scipy.spatial.transform import Rotation


class euler:
    def quat2euler(rotations):
        r = Rotation.from_quat(rotations)
        e = r.as_euler("xyz", degrees=True)
        return [e[0], e[1], e[2]]

        """
        x, y, z, w = rotations
        t0 = +2.0 * (w * x + y * z)

        t1 = +1.0 - 2.0 * (x * x + y * y)
        roll = math.atan2(t0, t1)
        t2 = +2.0 * (w * y - z * x)
        t2 = +1.0 if t2 > +1.0 else t2
        t2 = -1.0 if t2 < -1.0 else t2
        pitch = math.asin(t2)
        t3 = +2.0 * (w * z + x * y)
        t4 = +1.0 - 2.0 * (y * y + z * z)
        yaw = math.atan2(t3, t4)
        return [yaw, pitch, roll]
        """
