import math
from multiprocessing import Process, Pool, freeze_support
import copy
import numpy as np
from functools import partial
import json
from classes import Particle
import time
import random
import matplotlib.pyplot as plt

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

def verle_xy_thread(all_particles_, t_number, a_prev, delta_t, i):
    if t_number == 0:
        a = calculate_a([[all_particles_[0][j].x, all_particles_[0][j].y,
                                                     all_particles_[0][j].m] for j, pa in enumerate(all_particles_[0]) if j != i],
                    [all_particles_[0][i].x, all_particles_[0][i].y,
                     all_particles_[0][i].m])

        # a_prev[i] = a
    else:
        a = a_prev[i]
    lk = my_verle_for_xy(
        [all_particles_[0][i].x, all_particles_[0][i].y,all_particles_[0][i].u, all_particles_[0][i].v],
        delta_t, a)
    return (lk[0], lk[1], a[0], a[1], i)

def verle_uv_thread(all_particles_, t_number, a_prev, delta_t, i):
    a_next = calculate_a([[all_particles_[1][j].x, all_particles_[1][j].y,
                                                     all_particles_[1][j].m] for j, pa in enumerate(all_particles_[1]) if j != i],
                    [all_particles_[1][i].x, all_particles_[1][i].y,
                     all_particles_[1][i].m])
    lk = my_verle_for_uv([all_particles_[0][i].u, all_particles_[0][i].v], delta_t, a_prev[i], a_next)
    return (lk[0], lk[1], a_next[0], a_next[1], i)

def verle_xy_thread2(all_particles, t_number, a_prev, i, delta_t):
    return ([1,2], [3,4], i)

    # print('xy_done------------------------------------------------------------------------')




def calculate_verle_processes(particles, t_, delta_t):
    # print('here')
    t = np.linspace(0, t_, t_ / delta_t + 1)
    all_particles = [copy.deepcopy(particles) for t_ in t]
    a = np.zeros((len(particles), 2))
    for k, tk in enumerate(t):
        if k == len(t)-1:
            break
        with Pool(processes=4) as pool:
            # multiple_results = [pool.apply_async(partial(verle_xy_thread, all_particles=all_particles,
            #                                              t_number=k, a_prev = a,
            #                                              delta_t = delta_t), (j,)) for j in range(len(particles))]

            multiple_results = [pool.apply_async(partial(verle_xy_thread, all_particles[k:k+2],
                                                         k, a,
                                                         delta_t), (i,)) for i in range(len(particles))]
            for res in multiple_results:
                part = res.get(timeout=1)
                print(part)
                all_particles[k+1][part[4]].x, all_particles[k+1][part[4]].y = part[0], part[1]
                a[0], a[1] = part[2], part[3]

        with Pool(processes=4) as pool:
            multiple_results = [pool.apply_async(partial(verle_uv_thread, all_particles[k:k+2],
                                                         k, a,
                                                         delta_t), (j,)) for j in range(len(particles))]
            for res in multiple_results:
                part = res.get(timeout=1)
                all_particles[k+1][part[4]].u, all_particles[k+1][part[4]].v = part[0], part[1]
                a[0], a[1] = part[2], part[3]

            # all_particles[0] = copy.deepcopy(all_particles[1])
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

# if __name__ == '__main__':
#     # print('not here')
#     from calculations import calculate_verle, calculate_verle_cython, calculate_verle_threads
#     freeze_support()
#     # particles = []
#     # filename = 'inputs/solar_system2.json'
#     # with open(filename, 'r') as f:
#     #     data = json.load(f)
#     # print(data)
#     # print(type(data))
#     # for d in data['particles'].values():
#     #     particles.append(Particle(int(d['x']), int(d['y']),int(d['u']), int(d['v']), int(d['m']),
#     #                               int(d['lifetime']), d['color']))
#     N = 100
#     T = 100
#     dt = 1
#     particles = generate_particles(N)
#     parts = [{'x': p.x, 'y': p.y, 'u': p.u, 'v': p.v} for p in particles]
#
#     times = np.zeros(5)
#     for i in range(1):
#         t = time.time()
#         a = calculate_verle_processes(particles, T, dt)
#         times[i] = time.time()-t
#
#     print(f'Время для multiprocessing с {N} частиц: ', times.mean())
#
#     times = np.zeros(5)
#     for i in range(5):
#         t = time.time()
#         a = calculate_verle(particles, T, dt)
#         times[i] = time.time() - t
#
#     print(f'Время для последовательного с {N} частиц: ', times.mean())
#
#     times = np.zeros(5)
#     for i in range(5):
#         t = time.time()
#         a = calculate_verle_cython(particles, T, dt)
#         times[i] = time.time() - t
#
#     print(f'Время для последовательного cython с {N} частиц: ', times.mean())
#
#     times = np.zeros(5)
#     for i in range(5):
#         t = time.time()
#         a = calculate_verle_threads(particles, T, dt)
#         times[i] = time.time() - t
#
#     print(f'Время для threading с {N} частиц: ', times.mean())
#     # t = time.time()
#     # a = calculate_verle(particles, 1000, 1)
#     # print(time.time() - t)
#     # print(a[-1])
#     # t = time.time()
#     # a = calculate_verle_cython(particles, 1000, 1)
#     # print(time.time() - t)
#     # print(a[-1])
#     # print(parts)

def metrika(a,b):

    norm = []
    for i in range(len(a)):
        norm.append(math.sqrt((a[i]['x']-b[i]['x'])**2+(a[i]['y']-b[i]['y'])**2))
    return sum(norm)

def draw(t_, xes, legends):
    fig, ax = plt.subplots()
    linestyles = ['-','--','-.', ':']
    labels = ['x', 'y']
    # Сплошная линия ('-' или 'solid',
    # установлен по умолчанию):

    for i, xy_ in enumerate(xes):
        ax.plot(t_, xy_, linestyle=linestyles[i], linewidth=1.5, label = legends[i])


    ax.legend()
    fig.set_figwidth(12)
    fig.set_figheight(6)
    # fig.set_facecolor('linen')
    # ax.set_facecolor('ivory')
    ax.set_xlabel('t')
    ax.set_ylabel('errors')

    # if x_lim is None:
    #     pass
    # else:
    #     plt.xlim(x_lim)
    # if y_lim is None:
    #     pass
    # else:
    #     plt.ylim(y_lim)
    plt.show()

if __name__ == '__main__':
    # print('not here')
    from calculations import calculate_verle, calculate_verle_cython, calculate_verle_threads, calculate_odeint
    from processes_calculation import calc_to_draw
    freeze_support()
    particles = []
    # filename = 'inputs/solar_system.json'
    # with open(filename, 'r') as f:
    #     data = json.load(f)
    # print(data)
    # print(type(data))
    # for d in data['particles'].values():
    #     particles.append(Particle(int(d['x']), int(d['y']),int(d['u']), int(d['v']), int(d['m']),
    #                               int(d['lifetime']), d['color']))
    N = 100
    T = 100
    dt = 1
    particles = generate_particles(N)
    # parts = [{'x': p.x, 'y': p.y, 'u': p.u, 'v': p.v} for p in particles]

    times = np.zeros(5)
    # for i in range(1):
    #     t = time.time()
    # a1 = calculate_verle_processes(particles, T, dt)
        # times[i] = time.time()-t

    # print(f'Время для multiprocessing с {N} частиц: ', times.mean())

    times = np.zeros(5)
    for i in range(5):
        t = time.time()
        a2 = calculate_verle(particles, T, dt)
        times[i] = time.time() - t

    print(f'Время для последовательного с {N} частиц: ', times.mean())
    times = np.zeros(5)
    for i in range(5):
        t = time.time()
        a1 = calc_to_draw(particles, T, dt)
        times[i] = time.time() - t

    print(f'Время для процесса с {N} частиц: ', times.mean())
    times = np.zeros(5)
    for i in range(5):
        t = time.time()
        a3 = calculate_verle_cython(particles, T, dt)
        times[i] = time.time() - t

    print(f'Время для последовательного cython с {N} частиц: ', times.mean())
    #
    times = np.zeros(5)
    for i in range(5):
        t = time.time()
        a4 = calculate_verle_threads(particles, T, dt)
        times[i] = time.time() - t

    print(f'Время для потоков с {N} частиц: ', times.mean())
    a5 = calculate_odeint(particles, T, dt)

    x1 = []
    x2 = []
    x3 = []
    x4 = []

    for j, t_ in enumerate(a5):
        x1.append(metrika(a2[j], a5[j]))
        x2.append(metrika(a1[j], a5[j]))
        x3.append(metrika(a3[j], a5[j]))
        x4.append(metrika(a4[j], a5[j]))
    #
    t_ = np.linspace(0, T, int(T / dt) + 1)
    x1 = np.array(x1)
    x2 = np.array(x2)
    x3 = np.array(x3)
    x4 = np.array(x4)
    draw(t_,[x1,x2,x3,x4], ['verle', 'process', 'cython', 'threads'])

    # print(f'Время для threading с {N} частиц: ', times.mean())
    # t = time.time()
    # a = calculate_verle(particles, 1000, 1)
    # print(time.time() - t)
    # print(a[-1])
    # t = time.time()
    # a = calculate_verle_cython(particles, 1000, 1)
    # print(time.time() - t)
    # print(a[-1])
    # print(parts)