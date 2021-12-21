import numpy as np

"""
Since Blender currently is unable to display Bernstein Bézier coefficients
So we need to use this library to convert them to B-spline
"""


class BezierBsplineConverter:
    bi2_bb2b = np.array([
        [2, -1, 0],
        [0, 1, 0],
        [0, -1, 2]
    ])

    bi3_bb2b = np.array([
        [6, -7, 2, 0],
        [0, 2, -1, 0],
        [0, -1, 2, 0],
        [0, 2, -7, 6]
    ])

    bi4_bb2b = np.array([
        [24, -46, 29, -6, 0],
        [0, 6, -7, 2, 0],
        [0, -2, 5, -2, 0],
        [0, 2, -7, 6, 0],
        [0, -6, 29, -46, 24]
    ])

    @classmethod
    def bezier_to_bspline(cls, bezier_coefs_mat, deg_u, deg_v):
        total_bezier_coefs, vert_dim = bezier_coefs_mat.shape
        bezier_coef_per_patch = (deg_u + 1) * (deg_v + 1)

        # horizatal direction (v direction)   TODO: ADD DETAIL EXPLINATION HERE
        mask_v = cls.bb2b_mask_selector(deg_v)
        order_v = deg_v + 1
        temp_bc = np.zeros((total_bezier_coefs, vert_dim))
        for i in range(0, total_bezier_coefs, order_v):
            for j in range(order_v):
                temp_bc[i + j, :] = np.dot(mask_v[j, :], bezier_coefs_mat[i:i + order_v, :])

        # vertical direction (u direction)
        mask_u = cls.bb2b_mask_selector(deg_u)
        order_u = deg_u + 1
        bspline_coefs = np.zeros((total_bezier_coefs, vert_dim))

        for k in range(0, total_bezier_coefs, bezier_coef_per_patch):
            for i in range(order_u):
                for j in range(order_v):
                    bspline_coefs[k + i * order_v + j] = np.dot(mask_u[i, :],
                                                                temp_bc[k + j:k + bezier_coef_per_patch:order_v, :])

        return bspline_coefs

    @classmethod
    def bb2b_mask_selector(cls, deg):
        if deg == 2:
            return cls.bi2_bb2b
        elif deg == 3:
            return cls.bi3_bb2b
        elif deg == 4:
            return cls.bi4_bb2b
        else:
            print("Error: degree setting is not yet supported")
            return False
