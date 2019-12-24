import numpy as np
import math
G = 6.6743015*math.pow(10,-11)

cpdef double[:] test(int x):
    cdef double[:] y = np.zeros((x,))
    cdef int i
    for i in range(x):
        y[i] = i
    return y

cpdef double[:] my_verle_for_xy(double z0, double z1, double z2, double z3,
                                double delta_t, double a0, double a1):
    cdef double[:] xy_next = np.zeros(2)
    xy_next[0] = z0 + z2 * delta_t + a0 * delta_t * delta_t/ 2.0
    xy_next[1] = z1 + z3 * delta_t + a1 * delta_t * delta_t/ 2.0
    return xy_next


cpdef double[:] my_verle_for_uv(double uv_prev0, double uv_prev1, double delta_t, double a_prev0,
                                double a_prev1, double a_next0, double a_next1):
    cdef double[:] uv_next = np.zeros(2)
    uv_next[0] = uv_prev0 + (a_next0 + a_prev0) * delta_t/2.0
    uv_next[1] = uv_prev1 + (a_next1 + a_prev1) * delta_t/2.0
    # print('uv', 1/2)
    # print('uv', 1.0/2.0)
    # print('uv', 1/2.0)
    # print('uv', 1.0/2)
    return uv_next


# cpdef double[:] calculate_a(list points_jx, list points_jy, list point_i):
#     cdef double[:] summ_xy = np.zeros(2)
#     cdef double r_3
#     cdef double j
#     for j in range(len(points_jx)):
#         r_3 = math.pow(
#             math.pow(math.fabs(points_jx[j] - point_i[0]), 2) + math.pow(math.fabs(p[1] - point_i[1]),
#                                                                                  2), 3 / 2)
#         summ_xy[0] += G*p[2] * (p[0] - point_i[0]) / r_3
#         summ_xy[1] += G*p[2] * (p[1] - point_i[1]) / r_3
#     return ([summ_x, summ_y])


# def calculate_verle(particles, t_, delta_t):
#     t = np.linspace(0, t_, t_ / delta_t + 1)
#     all_coords = []
#     coords = []
#     for p in particles:
#         coords.append([p.x, p.y, p.u, p.v])
#     all_coords.append(coords)
#
#     a = np.zeros((len(particles), 2))
#     a_next = np.zeros((len(particles), 2))
#     for k, tk in enumerate(t):
#         if k !=0:
#             coords = []
#             for i, p in enumerate(particles):
#                 if tk == t[0]:
#                     a[i, 0], a[i, 1] = calculate_a([[all_coords[k-1][j][0], all_coords[k-1][j][1],
#                                                      pa.m] for j, pa in enumerate(particles) if j != i],
#                                                    [all_coords[k-1][i][0], all_coords[k-1][i][1], p.m])
#                 lk = my_verle_for_xy([all_coords[k-1][i][0], all_coords[k-1][i][1],all_coords[k-1][i][2],all_coords[k-1][i][3]],
#                                      delta_t, a[i])
#                 coords.append([lk[0], lk[1],0,0])
#             for i, p in enumerate(coords):
#                 a_next[i, 0], a_next[i, 1] = calculate_a([[pa[0], pa[1], particles[j].m]
#                                                           for j, pa in enumerate(coords) if j != i],
#                                                          [p[0], p[1], particles[i].m])
#                 lk = my_verle_for_uv([all_coords[k-1][i][2], all_coords[k-1][i][3]], delta_t, a[i], a_next[i])
#                 coords[i][2], coords[i][3] = lk[0], lk[1]
#             all_coords.append(coords)
#             a = copy.deepcopy(a_next)
#
#     return [[{'x': p[0], 'y': p[1], 'u': p[2], 'v': p[3]} for p in c] for c in all_coords]

