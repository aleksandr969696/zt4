import numpy as np
from scipy.integrate import odeint
import math
import copy
from threading import Thread
from multiprocessing import Pool
from multiprocessing import Process, Queue, Manager
from functools import partial
# import main
from classes import Particle, Emitter
import json


import verle_cython

G = 6.6743015*math.pow(10,-11)


def f_x(y0, t, masses):
    a_array = []
    points = []
    for i, m in enumerate(masses):
        points.append([y0[i*4], y0[i*4+1], m])
    for i, p in enumerate(points):
        a_array.append(calculate_a([point for j, point in enumerate(points) if j !=i], points[i]))
    ret = []

    for i, a in enumerate(a_array):
        ret.extend([y0[i * 4 + 2], y0[i * 4 + 3], a[0], a[1]])
    return ret


def calculate_odeint(particles, t_, delta_t):
    print('odeint')
    t = np.linspace(0, t_, t_ / delta_t + 1)
    y0 = []
    for p in particles:
        y0.extend(p.to_array_coords())
    # print([p.m for p in particles])
    lk = odeint(f_x, y0, t,
                args=([p.m for p in particles],))
    return [[{'x': lk[z][i*4],'y': lk[z][i*4+1],'u': lk[z][i*4+2],'v': lk[z][i*4+3]}
            for i in range(int(len(lk[z])/4))] for z in range(len(lk))]


def calculate_a(points_j, point_i):
    summ_x = 0
    summ_y = 0
    for j, p in enumerate(points_j):
        r_3 = math.pow(
            math.pow(math.fabs(p[0] - point_i[0]), 2) + math.pow(math.fabs(p[1] - point_i[1]),
                                                                                 2), 3 / 2)
        summ_x += G*p[2] * (p[0] - point_i[0]) / r_3
        summ_y += G*p[2] * (p[1] - point_i[1]) / r_3
    return ([summ_x, summ_y])


def my_verle_for_xy(z, delta_t, a_prev):
    # a_ = a_prev
    x_next = z[0] + z[2] * delta_t + 1 / 2 * a_prev[0]* delta_t* delta_t
    y_next = z[1] + z[3] * delta_t + 1 / 2 * a_prev[1]* delta_t* delta_t
    return (x_next, y_next)


def my_verle_for_uv(uv_prev, delta_t, a_prev, a_next):
    u_next = uv_prev[0] + 1 / 2 * (a_next[0] + a_prev[0]) * delta_t
    v_next = uv_prev[1] + 1 / 2 * (a_next[1] + a_prev[1]) * delta_t
    return (u_next, v_next)

def verle_xy_thread(all_particles, t_number, a_prev, i, delta_t):
    if t_number == 0:
        a = calculate_a([[all_particles[0][j].x, all_particles[0][j].y,
                                                     all_particles[0][j].m] for j, pa in enumerate(all_particles[0]) if j != i],
                    [all_particles[0][i].x, all_particles[0][i].y,
                     all_particles[0][i].m])

        a_prev[i] = a
    else:
        a = a_prev[i]
    lk = my_verle_for_xy(
        [all_particles[0][i].x, all_particles[0][i].y,all_particles[0][i].u, all_particles[0][i].v],
        delta_t, a)
    all_particles[1][i].x, all_particles[1][i].y = lk[0], lk[1]

    # print('xy_done------------------------------------------------------------------------')

def verle_uv_thread(all_particles, t_number, a_prev, i, delta_t):
    # print(len(all_particles))
    # print(len(all_particles[1]))
    a_next = calculate_a([[all_particles[1][j].x, all_particles[1][j].y,
                                                     all_particles[1][j].m] for j, pa in enumerate(all_particles[1]) if j != i],
                    [all_particles[1][i].x, all_particles[1][i].y,
                     all_particles[1][i].m])
    lk = my_verle_for_uv([all_particles[0][i].u, all_particles[0][i].v], delta_t, a_prev[i], a_next)
    a_prev[i] = a_next
    all_particles[1][i].u, all_particles[1][i].v = lk[0], lk[1]

    # print('uv_done')


def verle_xy_thread_cython(all_particles, t_number, a_prev, i, delta_t):
    if t_number == 0:
        a = calculate_a([[all_particles[0][j].x, all_particles[0][j].y,
                                                     all_particles[0][j].m] for j, pa in enumerate(all_particles[0]) if j != i],
                    [all_particles[0][i].x, all_particles[0][i].y,
                     all_particles[0][i].m])

        a_prev[i] = a
    else:
        a = a_prev[i]
    lk = verle_cython.my_verle_for_xy(
        all_particles[0][i].x, all_particles[0][i].y,all_particles[0][i].u, all_particles[0][i].v,
        delta_t, a[0], a[1])
    all_particles[1][i].x, all_particles[1][i].y = lk[0], lk[1]

    # print('xy_done------------------------------------------------------------------------')

def verle_uv_thread_cython(all_particles, t_number, a_prev, i, delta_t):
    # print(len(all_particles))
    # print(len(all_particles[1]))
    a_next = calculate_a([[all_particles[1][j].x, all_particles[1][j].y,
                                                     all_particles[1][j].m] for j, pa in enumerate(all_particles[1]) if j != i],
                    [all_particles[1][i].x, all_particles[1][i].y,
                     all_particles[1][i].m])
    lk = verle_cython.my_verle_for_uv(all_particles[0][i].u, all_particles[0][i].v, delta_t, a_prev[i,0], a_prev[i,0],
                                      a_next[0], a_next[1])
    a_prev[i] = a_next
    all_particles[1][i].u, all_particles[1][i].v = lk[0], lk[1]

    # print('uv_done')
# def verle_xy_processes(all_particles, t_number, a_prev, delta_t, i):
#     # print('xy')
#     # if t_number == 0:
#     #     a = calculate_a([[all_particles[0][j].x, all_particles[0][j].y,
#     #                                                  all_particles[0][j].m] for j, pa in enumerate(all_particles[0]) if j != i],
#     #                 [all_particles[0][i].x, all_particles[0][i].y,
#     #                  all_particles[0][i].m])
#     # else:
#     #     a = a_prev[i]
#     # lk = my_verle_for_xy(
#     #     [all_particles[0][i].x, all_particles[0][i].y,all_particles[0][i].u, all_particles[0][i].v],
#     #     delta_t, a)
#     # return {'i': i, 'x': lk[0], 'y': lk[1], 'a': a}
#     return {'i': i, 'x': 0, 'y': 0, 'a': [0,0]}
#
#     # print('xy_done------------------------------------------------------------------------')
#
# def verle_uv_processes(all_particles, t_number, a_prev, delta_t, i):
#     # print('uv')
#     # a_next = calculate_a([[all_particles[1][j].x, all_particles[1][j].y,
#     #                                                  all_particles[1][j].m] for j, pa in enumerate(all_particles[1]) if j != i],
#     #                 [all_particles[1][i].x, all_particles[1][i].y,
#     #                  all_particles[1][i].m])
#     # lk = my_verle_for_uv([all_particles[0][i].u, all_particles[0][i].v], delta_t, a_prev[i], a_next)
#     # return {'i': i, 'u': lk[0], 'v': lk[1], 'a': a_next}
#     return {'i': i, 'u': 0, 'v': 0, 'a': [0, 0]}


def calculate_verle_threads(particles, t_, delta_t):
    t = np.linspace(0, t_, t_ / delta_t + 1)
    all_particles = [copy.deepcopy(particles) for t_ in range(2)]
    a = np.zeros((len(particles), 2))
    for k, tk in enumerate(t):
        threads = []
        for i, p in enumerate(particles):
            threads.append(Thread(target=verle_xy_thread, args=(all_particles, k, a, i, delta_t)))
        for i, p in enumerate(particles):
            threads[i].start()
        for i, p in enumerate(particles):
            threads[i].join()

        threads = []
        for i, p in enumerate(particles):
            threads.append(Thread(target=verle_uv_thread, args=(all_particles, k, a, i, delta_t)))
        for i, p in enumerate(particles):
            threads[i].start()
        for i, p in enumerate(particles):
            threads[i].join()
        all_particles[0] = copy.deepcopy(all_particles[1])
    return [[{'x': p.x, 'y': p.y, 'u': p.u, 'v': p.v} for p in c] for c in all_particles]



def calculate_verle_processes(particles, t_, delta_t):
    t = np.linspace(0, t_, t_ / delta_t + 1)
    all_particles = [copy.deepcopy(particles) for t_ in range(2)]
    a = np.zeros((len(particles), 2))
    for k, tk in enumerate(t):
        threads = []
        for i, p in enumerate(particles):
            threads.append(Thread(target=verle_xy_thread, args=(all_particles, k, a, i, delta_t)))
        for i, p in enumerate(particles):
            threads[i].start()
        for i, p in enumerate(particles):
            threads[i].join()

        threads = []
        for i, p in enumerate(particles):
            threads.append(Thread(target=verle_uv_thread, args=(all_particles, k, a, i, delta_t)))
        for i, p in enumerate(particles):
            threads[i].start()
        for i, p in enumerate(particles):
            threads[i].join()
        all_particles[0] = copy.deepcopy(all_particles[1])
    return [[{'x': p.x, 'y': p.y, 'u': p.u, 'v': p.v} for p in c] for c in all_particles]


# def processes_func(func, parts, t_number, a_v, delta_t):
#     pool = Pool(processes=8)
#
#     # results = pool.imap_unordered(partial(verle_xy_processes,all_particles[:], k, a, delta_t),
#     #                    [i for i in range(len(particles))])
#     results = pool.imap_unordered(partial(func, parts, t_number, a_v, delta_t),
#                                   [i for i in range(len(parts[-1]))])
#     pool.close()
#     pool.join()
#     return results

# def calculate_verle_processes(particles, t_, delta_t):
#     t = np.linspace(0, t_, t_ / delta_t + 1)
#     all_particles = [copy.deepcopy(particles) for t_ in range(2)]
#     a = np.zeros((len(particles), 2))
#     for k, tk in enumerate(t):
#         # pool = Pool(processes=8)
#         #
#         # # results = pool.imap_unordered(partial(verle_xy_processes,all_particles[:], k, a, delta_t),
#         # #                    [i for i in range(len(particles))])
#         # results = pool.imap_unordered(partial(verle_xy_processes, None, None, None, None),
#         #                    [i for i in range(len(particles))])
#         # print(k, '-------------------------------------------------------------------------------------------------------------------')
#         # pool.close()
#         # pool.join()
#         results = processes_func(verle_xy_processes, all_particles[:], k, a, delta_t)
#         print(k, '-------------------------------------------------------------------------------------------------------------------')
#         for result in results:
#             all_particles[1][result['i']].x, all_particles[1][result['i']].y = result['x'], result['y']
#             a[result['i']] = result['a']
#
#         results = processes_func(verle_uv_processes, all_particles[:], k, a, delta_t)
#         # pool = Pool(processes=8)
#         # # results = pool.imap_unordered(partial(verle_uv_processes,all_particles[:], k, a, delta_t),
#         # #                    [i for i in range(len(particles))])
#         # results = pool.imap_unordered(partial(verle_uv_processes, None, None, None, None),
#         #                               [i for i in range(len(particles))])
#
#         for result in results:
#             all_particles[1][result['i']].u, all_particles[1][result['i']].v = result['u'], result['v']
#             a[result['i']] = result['a']
#         print(results,'-------------------------------------------------------------------------------------------------------------------')
#         # pool.close()
#         # pool.join()
#         all_particles[0]=copy.deepcopy(all_particles[1])
#     return [[{'x': p.x, 'y': p.y, 'u': p.u, 'v': p.v} for p in c] for c in all_particles]

    # with Pool(processes=8) as pool:
    #
    #     # print "[0, 1, 4,..., 81]"
    #
    #     # launching multiple evaluations asynchronously *may* use more processes
    #     multiple_results = [pool.apply_async(f, (i,)) for i in range(4)]
    #     print([res.get(timeout=1) for res in multiple_results])
    #
    #
    # # exiting the 'with'-block has stopped the pool
    # print("Now the pool is closed and no longer available")


# def calculate_verle_processes3(particles, t_, delta_t):
#     print(len(particles))
#     t = np.linspace(0, t_, t_ / delta_t + 1)
#     all_particles = [copy.deepcopy(particles) for t_ in range(2)]
#     a = np.zeros((len(particles), 2))
#     # for k, tk in enumerate(t):
#
#     with Pool(processes=8) as pool:
#
#         # print "[0, 1, 4,..., 81]"
#
#         # launching multiple evaluations asynchronously *may* use more processes
#         multiple_results = [pool.apply_async(f, (i,)) for i in range(4)]
#         print([res.get(timeout=1) for res in multiple_results])

    # with Pool(processes=8) as pool:
    #     multiple_results = [pool.apply_async(fx, (i,)) for i in range(4)]
    #     print([res.get(timeout=1) for res in multiple_results])
    # return [[{'x': p.x, 'y': p.y, 'u': p.u, 'v': p.v} for p in c] for c in all_particles]

# def calculate_verle_processes2(particles, t_, delta_t):
#     t = np.linspace(0, t_, t_ / delta_t + 1)
#     manager = Manager()
#     all_particles = manager.list([copy.deepcopy(particles) for t_ in t])
#     a = manager.list(np.zeros((len(particles), 2)))
#     # q = Queue()
#     # q.put([all_particles, a])
#     for k, tk in enumerate(t):
#         processes = []
#         for i, p in enumerate(all_particles[k]):
#             processes.append(Process(target=verle_uv_thread, args=(all_particles, k, a, i, delta_t)))
#         for i, p in enumerate(all_particles[k]):
#             processes[i].start()
#         for i, p in enumerate(all_particles[k]):
#             processes[i].join()
#         # all_particles, a = q.get()
#         processes = []
#         for i, p in enumerate(all_particles[k]):
#             processes.append(Process(target=verle_uv_thread, args=(all_particles, k, a, i, delta_t)))
#         for i, p in enumerate(all_particles[k]):
#             processes[i].start()
#         for i, p in enumerate(all_particles[k]):
#             processes[i].join()
#         # all_particles, a = q.get()
#     return [[{'x': p.x, 'y': p.y, 'u': p.u, 'v': p.v} for p in c] for c in all_particles]

def calculate_verle(particles, t_, delta_t):
    t = np.linspace(0, t_, t_ / delta_t + 1)
    all_particles = [copy.deepcopy(particles) for t_ in range(2)]

    a = np.zeros((len(particles), 2))
    a_next = np.zeros((len(particles), 2))
    for k, tk in enumerate(t):
        for i, p in enumerate(particles):
            verle_xy_thread(all_particles, k, a, i, delta_t)
        for i, p in enumerate(particles):
            verle_uv_thread(all_particles, k, a, i, delta_t)
        all_particles[0] = copy.deepcopy(all_particles[1])
    return [[{'x': p.x, 'y': p.y, 'u': p.u, 'v': p.v} for p in c] for c in all_particles]

# def calculate_verle(particles, t_, delta_t):
#     # print('verle')
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


# def calculate_verle_cython(particles, t_, delta_t):
#     t = np.linspace(0, t_, t_ / delta_t + 1)
#     all_particles = [copy.deepcopy(particles) for t_ in range(2)]
#
#     a = np.zeros((len(particles), 2))
#     a_next = np.zeros((len(particles), 2))
#     for k, tk in enumerate(t):
#         for i, p in enumerate(particles):
#             verle_xy_thread_cython(all_particles, k, a, i, delta_t)
#         for i, p in enumerate(particles):
#             verle_uv_thread_cython(all_particles, k, a, i, delta_t)
#         all_particles[0] = copy.deepcopy(all_particles[1])
#     return [[{'x': p.x, 'y': p.y, 'u': p.u, 'v': p.v} for p in c] for c in all_particles]

def calculate_verle_cython(particles, t_, delta_t):
    # print('verle_cython')
    t = np.linspace(0, t_, t_ / delta_t + 1)
    all_coords = []
    coords = []
    for p in particles:
        coords.append([p.x, p.y, p.u, p.v])
    all_coords.append(coords)

    a = np.zeros((len(particles), 2))
    a_next = np.zeros((len(particles), 2))
    for k, tk in enumerate(t):
        if k !=0:
            coords = []
            for i, p in enumerate(particles):
                if tk == t[0]:
                    a[i, 0], a[i, 1] = calculate_a([[all_coords[k-1][j][0], all_coords[k-1][j][1],
                                                     pa.m] for j, pa in enumerate(particles) if j != i],
                                                   [all_coords[k-1][i][0], all_coords[k-1][i][1], p.m])
                lk = verle_cython.my_verle_for_xy(all_coords[k-1][i][0], all_coords[k-1][i][1],all_coords[k-1][i][2],
                                                  all_coords[k-1][i][3],
                                     delta_t, a[i,0], a[i,1])
                coords.append([lk[0], lk[1],0,0])
            for i, p in enumerate(coords):
                a_next[i, 0], a_next[i, 1] = calculate_a([[pa[0], pa[1], particles[j].m]
                                                          for j, pa in enumerate(coords) if j != i],
                                                         [p[0], p[1], particles[i].m])
                lk = verle_cython.my_verle_for_uv(all_coords[k-1][i][2], all_coords[k-1][i][3],
                                                  delta_t, a[i,0], a[i,1], a_next[i,0], a_next[i,1])
                coords[i][2], coords[i][3] = lk[0], lk[1]
            all_coords.append(coords)
            a = copy.deepcopy(a_next)

    return [[{'x': p[0], 'y': p[1], 'u': p[2], 'v': p[3]} for p in c] for c in all_coords]

# print(verle_cython.verle(5))