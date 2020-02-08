import numpy as np
from scipy.integrate import odeint
import math
from copy import deepcopy
from threading import Thread
import multiprocessing as mp
from multiprocessing import Pool
from multiprocessing import Process, Queue, Manager
from functools import partial
# import main
from classes import Particle, Emitter
import json


import verle_cython

G = 6.6743015*math.pow(10,-11)

def calculate_a(points_j, point_i):
    summ_x = 0
    summ_y = 0
    for j in range(len(points_j)//5):
        r_3 = math.pow(
            math.pow(math.fabs(points_j[j*5] - point_i[0]), 2) + math.pow(math.fabs(points_j[j*5+1] - point_i[1]),
                                                                                 2), 3 / 2)
        summ_x += G*points_j[j*5+4] * (points_j[j*5] - point_i[0]) / r_3
        summ_y += G*points_j[j*5+4] * (points_j[j*5+1]- point_i[1]) / r_3
    return summ_x, summ_y

def my_verle_for_xy(z, delta_t, a_prev):
    # a_ = a_prev
    x_next = z[0] + z[2] * delta_t + 1 / 2 * a_prev[0]* delta_t* delta_t
    y_next = z[1] + z[3] * delta_t + 1 / 2 * a_prev[1]* delta_t* delta_t
    return (x_next, y_next)


def my_verle_for_uv(uv_prev, delta_t, a_prev, a_next):
    u_next = uv_prev[0] + 1 / 2 * (a_next[0] + a_prev[0]) * delta_t
    v_next = uv_prev[1] + 1 / 2 * (a_next[1] + a_prev[1]) * delta_t
    return (u_next, v_next)

def verle_xy_thread(particles, a_prev, i, delta_t):

    lk = my_verle_for_xy(
        [particles[i*5+0], particles[i*5+1], particles[i*5+2], particles[i*5+3]],
        delta_t, a_prev)
    return lk

    # print('xy_done------------------------------------------------------------------------')

def verle_uv_thread(particles, new_particles, a_prev, i, delta_t):
    a_next = calculate_a([p for j, p in enumerate(new_particles) if j // 5 != i], new_particles[i * 5:(i + 1) * 5])
    lk = my_verle_for_uv([particles[i*5+2], particles[i*5+3]], delta_t, a_prev, a_next)
    return (a_next[0], a_next[1], lk[0], lk[1])



def func(data, times, dt):
    proc_count = mp.cpu_count()
    shape = (times, len(data), len(data[0]))
    size = shape[1] * shape[2]
    block = len(data) // proc_count
    # if block*proc_count<len(data):
    #     block+=1
    remain = len(data)-block*proc_count
    # print('block', block)
    shared_data = mp.Array('d', np.zeros(size*2))
    result = mp.Array('d', np.zeros(int(times * size)))
    data = data.ravel()
    result[:size] = deepcopy(data)

    barrier = mp.Barrier(proc_count)
    queue = mp.Queue()
    processes = []
    for i in range(proc_count):
        i_s = i * block
        if i < proc_count - 1:
            i_e = (i + 1) * block
            if remain-i > 0:
                i_e += 1+i
            else:
                i_e+=remain
        else:
            i_e = shape[1]
        if remain - i > 0:
            i_s+=i
        else:
            i_s+=remain
        # if i == 3:
        # print('i_s_e',i,i_s, i_e, shape[1])
        # i_s*=shape[2]
        # i_e *= shape[2]
        args = [shared_data, result, proc_count, i_s, i_e, times, dt, barrier, queue, size, i]
        process = mp.Process(target=calculate_process_verle, args=(*args,))
        processes.append(process)
        process.start()

    for process in processes:
        process.join()
    return result
    # print(result[:])


def calculate_process_verle(shared_data, result, proc_count, i_s, i_e, times, dt, barrier, queue, size, proc_number):
    # print('process_number', proc_number)
    for i in range(1, times):
        particles = deepcopy(result[(i - 1) * size:i * size])
        if i == 1:
            a = None
        else:
            a = deepcopy(shared_data[:])
        k =  calculate_verle(particles,dt, [i for i in range(i_s, i_e)], a)
        # print('k', k)
        # print('len',len(k),len(k[0][i_s*10:i_e*10]),len(k[1][i_s*5:i_e*5]), len(shared_data[i_s*10:i_e*10]), len(particles[i_s*5:i_e*5]),
        #       len(shared_data[:]), len(particles[:]),i_s, i_e)
        shared_data[i_s*10:i_e*10], particles[i_s*5:i_e*5] = k[0][i_s*10:i_e*10], k[1][i_s*5:i_e*5]
        queue.put([i_s, i_e, particles[i_s*5:i_e*5]])
        barrier.wait()

        # for j in range(proc_count):
        temp = queue.get()
        # print(temp)
        # print(proc_number, j, temp)
        # print(proc_number, i, j, result[:])
        result[int(i * size + temp[0]*5):int(i * size + temp[1]*5)] = deepcopy(temp[2])
        barrier.wait()



def calculate_verle(particles, delta_t, part_range, a_prev = None):
    new_particles = deepcopy(particles)
    if a_prev is None:
        a = np.zeros(len(particles)*2)
    else:
        a = deepcopy(a_prev)

    for i in part_range:
        if a_prev is None:
            # print('a[i]', i, len(a))
            # print('len', len(particles), [p for j, p in enumerate(particles) if j//5!=i])
            a[i*2],a[i*2+1]= calculate_a([p for j, p in enumerate(particles) if j//5!=i], particles[i*5:(i+1)*5])

        # print('len2', len(new_particles), str(i*5+1), len(a), i*2+1)
        new_particles[i*5], new_particles[i*5+1] = verle_xy_thread(particles, [a[i*2], a[i*2+1]], i, delta_t)
    for i in part_range:
        a[i*2], a[i*2+1], new_particles[i*5+2], new_particles[i*5+3] = \
            verle_uv_thread(particles, new_particles, [a[i*2], a[i*2+1]], i, delta_t)
    return a, new_particles

# def calculate_verle(particles, delta_t, part_range, a_prev = None):
#     new_particles = copy.deepcopy(particles)
#     if a_prev is None:
#         a = None
#     else:
#         a = copy.deepcopy(a_prev)
#
#     for i in part_range:
#         if a_prev is None:
#             a[i] = calculate_a(particles, particles[i])
#         new_particles[i].x, new_particles[i].y = verle_xy_thread(particles, a[i], i, delta_t)
#     for i, p in enumerate(particles):
#         a[i][0], a[i][1], new_particles[i].u, new_particles[i].v = \
#             verle_uv_thread(particles, new_particles, a, i, delta_t)


    # return [[{'x': p.x, 'y': p.y, 'u': p.u, 'v': p.v} for p in c] for c in all_particles]

def calc_to_draw(particles, t_, delta_t):
    particles_array = []
    for p in particles:
        particles_array.append([p.x, p.y, p.u, p.v, p.m])
    particles_array = np.array(particles_array)
    times = int(t_ / delta_t) + 1
    result = func(particles_array, times , delta_t)

    res = []
    size = len(particles)
    for t in range(times):
        time = []
        for i in range(size):
            time.append(result[size*5*t+i*5:size*5*t+i*5+4])
        res.append(time)
    # print(res)
    return [[{'x': p[0], 'y': p[1], 'u': p[2], 'v': p[3]} for p in c] for c in res]

# if __name__ == '__main__':
#     from calculations import calculate_verle, calculate_verle_cython, calculate_verle_threads, calculate_odeint
#
#     # freeze_support()
#     particles = []
#     particles_array = []
#     filename = 'inputs/solar_system.json'
#     with open(filename, 'r') as f:
#         data = json.load(f)
#     # print(data)
#     # print(type(data))
#     for d in data['particles'].values():
#         particles.append(Particle(int(d['x']), int(d['y']), int(d['u']), int(d['v']), int(d['m']),
#                                   int(d['lifetime']), d['color']))
#
#     for p in particles:
#         particles_array.append([p.x, p.y, p.u, p.v, p.m])
#     particles_array = np.array(particles_array)
#     # N = 100
#     T = 100
#     dt = 1
#     result = func(particles_array, 10000, 1)
