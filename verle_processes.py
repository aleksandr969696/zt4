import math
from multiprocessing import Process, Pool, freeze_support
import copy
import numpy as np
from functools import partial
import json
from classes import Particle
import time
import random

G = 6.6743015*math.pow(10,-11)


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
    x_next = z[0] + z[2] * delta_t + 1 / 2 * a_prev[0]* delta_t* delta_t
    y_next = z[1] + z[3] * delta_t + 1 / 2 * a_prev[1]* delta_t* delta_t
    return (x_next, y_next)


def my_verle_for_uv(uv_prev, delta_t, a_prev, a_next):
    u_next = uv_prev[0] + 1 / 2 * (a_next[0] + a_prev[0]) * delta_t
    v_next = uv_prev[1] + 1 / 2 * (a_next[1] + a_prev[1]) * delta_t
    return (u_next, v_next)

def verle_xy_thread(all_particles, t_number, a_prev, delta_t, i):
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
    return (lk, a, i)

def verle_uv_thread(all_particles, t_number, a_prev, delta_t, i):
    a_next = calculate_a([[all_particles[1][j].x, all_particles[1][j].y,
                                                     all_particles[1][j].m] for j, pa in enumerate(all_particles[1]) if j != i],
                    [all_particles[1][i].x, all_particles[1][i].y,
                     all_particles[1][i].m])
    lk = my_verle_for_uv([all_particles[0][i].u, all_particles[0][i].v], delta_t, a_prev[i], a_next)
    return (lk, a_next, i)

def verle_xy_thread2(all_particles, t_number, a_prev, i, delta_t):
    return ([1,2], [3,4], i)

    # print('xy_done------------------------------------------------------------------------')




def calculate_verle_processes(particles, t_, delta_t):
    # print('here')
    t = np.linspace(0, t_, t_ / delta_t + 1)
    all_particles = [copy.deepcopy(particles) for t_ in range(2)]
    a = np.zeros((len(particles), 2))
    for k, tk in enumerate(t):
        with Pool(processes=4) as pool:
            # multiple_results = [pool.apply_async(partial(verle_xy_thread, all_particles=all_particles,
            #                                              t_number=k, a_prev = a,
            #                                              delta_t = delta_t), (j,)) for j in range(len(particles))]

            multiple_results = [pool.apply_async(partial(verle_xy_thread, all_particles,
                                                         k, a,
                                                         delta_t), (i,)) for i in range(len(particles))]
            for res in multiple_results:
                part = res.get(timeout=1)
                all_particles[1][part[2]].x, all_particles[1][part[2]].y = part[0][0], part[0][1]
                a[0], a[1] = part[1][0], part[1][1]

        with Pool(processes=4) as pool:
            multiple_results = [pool.apply_async(partial(verle_uv_thread, all_particles,
                                                         k, a,
                                                         delta_t), (j,)) for j in range(len(particles))]
            for res in multiple_results:
                part = res.get(timeout=1)
                all_particles[1][part[2]].u, all_particles[1][part[2]].v = part[0][0], part[0][1]
                a[0], a[1] = part[1][0], part[1][1]

            all_particles[0] = copy.deepcopy(all_particles[1])
    return [[{'x': p.x, 'y': p.y, 'u': p.u, 'v': p.v} for p in c] for c in all_particles]

def generate_particles(N):
    particles = []
    for j in range(N):
        particles.append(Particle(random.randint(-math.pow(10,10), math.pow(10,10)),
                                  random.randint(-math.pow(10,10), math.pow(10,10)),
                                  random.randint(-math.pow(10,4), math.pow(10,4)),
                                  random.randint(-math.pow(10,4), math.pow(10,4)),
                                  random.randint(-math.pow(10,24), math.pow(10,24)),
                                  100,
                                  None))
    return particles

if __name__ == '__main__':
    print('not here')
    from calculations import calculate_verle, calculate_verle_cython
    freeze_support()
    # particles = []
    # filename = 'inputs/solar_system2.json'
    # with open(filename, 'r') as f:
    #     data = json.load(f)
    # print(data)
    # print(type(data))
    # for d in data['particles'].values():
    #     particles.append(Particle(int(d['x']), int(d['y']),int(d['u']), int(d['v']), int(d['m']),
    #                               int(d['lifetime']), d['color']))

    particles = generate_particles(100)
    parts = [{'x': p.x, 'y': p.y, 'u': p.u, 'v': p.v} for p in particles]
    t = time.time()
    a = calculate_verle_processes(particles, 10000, 10000)
    print(time.time()-t)
    print(a[-1])
    t = time.time()
    a = calculate_verle(particles, 10000, 10000)
    print(time.time() - t)
    print(a[-1])
    t = time.time()
    a = calculate_verle_cython(particles, 10000, 10000)
    print(time.time() - t)
    print(a[-1])
    print(parts)

