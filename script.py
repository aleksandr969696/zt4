# from main import Application
from tkinter import *
from tkinter.ttk import Combobox
from tkinter import Tk, W, E, Frame, colorchooser, Button, Entry, Label, filedialog
# from tkinter.ttk import Button, Style, Entry, Label
import math
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib
from matplotlib.animation import FuncAnimation
# from scipy.integrate import odeint
import random
from numpy import arange, sin, pi
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pylab
from matplotlib.figure import Figure
from numpy import arange, sin, pi
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import time
import copy
import json
# from calculations import calculate_verle, calculate_odeint, calculate_verle_processes
# from classes import Particle, Emitter
import pylab
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.colors import LinearSegmentedColormap
from matplotlib import cm






def readFile(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
    emitter = Emitter()
    for d in data['particles'].values():
        print(d)
        particle = Particle(int(d['x']), int(d['y']), int(d['u']), int(d['v']),
                            int(d['m']), int(d['lifetime']),d['color'])
        emitter.x_ = int(d['x'])
        emitter.y_ = int(d['y'])
        emitter.u_ = int(d['u'])
        emitter.v_ = int(d['v'])
        m = int(d['m'])
        lifetime = int(d['lifetime'])
        # self.color = ((int(d['color'][0]),int(data[6]),int(data[7])),'red')
        color = d['color']
        print(m, color, lifetime)
        emitter.generate_particle(m,color, lifetime)
    return emitter

def calculate(particles,t, delta_t):
    t1 = time.time()
    odeint_result = calculate_odeint(particles, t, delta_t)
    t1_res = time.time()-t1
    t2 = time.time()
    verle_result = calculate_verle(particles, t, delta_t)
    t2_res = time.time()-t2
    return {'odeint_result': odeint_result, 'odeint_time': t1_res,
            'verle_result': verle_result, 'verle_time': t2_res}

def main3():

    file_name_from = r'C:\Users\Александр\PycharmProjects\Education\MM\zachet_task1\solar_system.json'

    emitter = readFile(file_name_from)
    file_name_to = r'C:\Users\Александр\PycharmProjects\Education\MM\zachet_task1\results\script_result'
    delta_t_dict = dict()
    # for t in [math.pow(10,i) for i in [0,3,6,9,12,15]]:
    for t in [math.pow(10, i) for i in [15,]]:
        delta_t_dict[t] = [t/math.pow(10,i) for i in [5,4,3,2,1,0]]
    # delta_t_dict[100000] = [100, 1000]
    for t, delta_t_array in delta_t_dict.items():
        for delta_t in delta_t_array:
            print(t,delta_t)
            result = calculate(emitter.particles, t, delta_t)
            file_name = f'{file_name_to}_{t}_{delta_t}_odeint.json'
            with open(file_name, 'w') as f:
                json.dump({'t': t, 'delta_t': delta_t, 'odeint_result': result['odeint_result'],
                           'odeint_time': result['odeint_time']}, f)
            file_name = f'{file_name_to}_{t}_{delta_t}_verle.json'
            with open(file_name, 'w') as f:
                json.dump({'t': t, 'delta_t': delta_t, 'verle_result': result['verle_result'],
                           'verle_time': result['verle_time']}, f)

def main2():
    file_name_to = r'C:\Users\Александр\PycharmProjects\Education\MM\zachet_task1\results\script_result'
    delta_t_dict = dict()
    for t in [math.pow(10, i) for i in [0, 3, 6, 9, 12,15]]:
        delta_t_dict[t] = [t / math.pow(10, i) for i in [5, 4, 3, 2, 1, 0]]
    # delta_t_dict[100000] = [100, 1000]
    times_odeint = np.zeros((len(delta_t_dict), len(delta_t_dict[1])))
    times_odeint_dict = dict()
    for i, t in enumerate(delta_t_dict):
        for j, dt in enumerate(delta_t_dict[t]):
            file_name = f'{file_name_to}_{t}_{dt}_odeint.json'
            with open(file_name, 'r') as f:
                result_odeint = json.load(f)
                # for r in result_odeint:
                #     print(r)
                times_odeint[i, j] = result_odeint['odeint_time']
            # file_name = f'{file_name_to}_{t}_{delta_t}_verle.json'
            # with open(file_name, 'r') as f:
            #     result_verle = json.load(f)

    print(times_odeint)
    t_array=np.array([[t for delta in delta_t_dict[1]] for t in delta_t_dict])
    delta_t_array=np.array([[math.pow(10, i) for i in [5, 4, 3, 2, 1, 0]] for t in delta_t_dict])

    print('times',times_odeint)
    print(t_array)
    print(delta_t_array)
    # times_odeint = np.zeros((len(delta_t_dict),len(delta_t_dict[1])))
    # times_odeint_dict = dict()
    # times_verle = np.zeros((len(delta_t_dict), len(delta_t_dict[1])))
    # for i, r in enumerate(result_odeint):
    #     print(r)
    #     times_odeint_dict[r['t']][r['delta_t']]=r['odeint_time']
    # for i, t in enumerate(t_array[0,:]):
    #     for j, dt in enumerate(delta_t_array[:,0]):
    #         times_odeint[i,j]=times_odeint_dict[t][dt]

    fig = pylab.figure()
    axes = Axes3D(fig)
    x, y, z = delta_t_array, t_array,  times_odeint
    axes.set_ylabel('Threads')
    axes.set_xlabel('Scale')
    axes.set_zlabel('MTEPS')
    axes.plot_surface(x, y, z, rstride=1, cstride=1, cmap=cm.Spectral)

    pylab.show()

def main(t, delta_t, filename):

    emitter = readFile(filename)
    result = calculate(emitter.particles, t, delta_t)
    time_odeint = result['odeint_time']
    time_verle = result['verle_time']
    result_odeint = result['odeint_result']
    result_verle = result['verle_result']
    print('time_odeint', time_odeint)
    print('time_verle', time_verle)
    t_array = np.linspace(0,t,t/delta_t+1)
    errors = np.zeros(len(t_array))
    print(len(errors), len(result_odeint), len(result_verle))
    for i, e in enumerate(errors):
        r1 = result_odeint[i]
        r2 = result_verle[i]
        error = 0
        for j, r in enumerate(r1):
            dx = r['x'] - r2[j]['x']
            dy = r['y'] - r2[j]['y']
            # print('dx', dx, 'dy', dy)
            error += dx*dx+dy*dy
        errors[i] = math.sqrt(error)
        # print(errors[i])

    fig, ax = plt.subplots()

    #  Сплошная линия ('-' или 'solid',
    #  установлен по умолчанию):
    ax.plot(t_array, errors,
            linestyle='-',
            linewidth=1,
            color='red')


    fig.set_figwidth(12)
    fig.set_figheight(6)
    fig.set_facecolor('linen')
    ax.set_facecolor('ivory')
    ax.set_xlabel('t')
    ax.set_ylabel('Квадратичная ошибка')
    ax.set_title(f'time verle: {time_verle},    time odeint: {time_odeint},     delta t: {delta_t}')
    plt.show()


def calculate2(particles,t, delta_t):
    t1 = time.time()
    odeint_result = calculate_verle_processes(particles, t, delta_t)
    # t1_res = time.time()-t1
    # t2 = time.time()
    # verle_result = calculate_verle(particles, t, delta_t)
    # t2_res = time.time()-t2
    # return {'odeint_result': odeint_result, 'odeint_time': t1_res,
    #         'verle_result': verle_result, 'verle_time': t2_res}

def main4(t, delta_t, filename):

    emitter = readFile(filename)
    result = calculate2(emitter.particles, t, delta_t)




from train import main1 as maxim

def main6():
    # a = input('aaa: ')
    # if a == 'y':
    maxim()
    # else:
    #     print('nope')

if __name__ == '__main__':
    main6()
    # file_name_from = r'inputs\solar_system.json'
    # t = float(input('Введите t: '))
    # dt = float(input('Введите dt: '))
    # filename = input('Введите имя файла с данными. По умолчанию inputs\solar_system.json. Если не хотите менять, оставьте ввод пустым')
    # if filename == '':
    #     filename=file_name_from
    # print('t:', t, 'dt:', dt, 'filename:', filename)
    # main4(t, dt, filename)






