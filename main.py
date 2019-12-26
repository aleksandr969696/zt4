from tkinter import *

# from tkinter.ttk import Combobox
from tkinter import Tk, W, E, Frame, colorchooser, Button, Entry, Label, filedialog
# from tkinter.ttk import Button, Style, Entry, Label
import math
import numpy as np
import matplotlib.pyplot as plt
# import matplotlib.animation as animation
# import matplotlib
from matplotlib.animation import FuncAnimation
# from scipy.integrate import odeint
# import random
# from numpy import arange, sin, pi
# from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# import pylab
# from matplotlib.figure import Figure
# from numpy import arange, sin, pi
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import time
import copy
import json
from classes import Emitter, Particle
from calculations import calculate_odeint, calculate_verle, calculate_verle_threads, calculate_verle_cython
from verle_processes import calculate_verle_processes
from multiprocessing import freeze_support

U_MAX = 100
U_MIN = -100
V_MAX = 100
V_MIN = -100
R_MAX = 200
R_V_MAX = 20
G = 6.6743015*math.pow(10,-11)
# class Particle:
#
#     def __init__(self, x=0, y=0, u=0, v=0, m=0, color=NONE, lifetime=0):
#         self.x = x
#         self.y = y
#         self.u = u
#         self.v = v
#
#
#         # self.x_10 = x_10
#         # self.y_10 = y_10
#         # self.u_10 = u_10
#         # self.v_10 = v_10
#         self.m = m
#         # self.m_10 = m_10
#         self.color = color
#         self.lifetime = lifetime
#
#     def __str__(self):
#         s = 'x: '+str(self.x)+' y:'+ str(self.y) + ' u:'+str(self.u)+' v:'+str(self.v)
#         return s
#
#     def to_array_coords(self):
#         return [self.x, self.y, self.u, self.v]
#
#     def to_dict(self):
#         return {'x': self.x, 'y': self.y, 'u': self.u, 'v': self.v, 'm': self.m,
#                 'lifetime': self.lifetime, 'color': self.color}
#
#
#
# class Emitter:
#
#     def __init__(self, x=0, y=0, u=0, v=0, x_10=0, y_10=0, u_10=0, v_10=0):
#         self.x_ = x
#         self.y_ = y
#         self.u_ = u
#         self.v_ = v
#         self.x_10 = x_10
#         self.y_10 = y_10
#         self.u_10 = u_10
#         self.v_10 = v_10
#         self.particles = []
#         self.particles_init = []
#
#     def to_dict(self):
#         d = {}
#         for i, p in enumerate(self.particles):
#             d[i] = p.to_dict()
#         return d
#
#     def to_array_coords(self, coords = None):
#         if coords is None:
#             a = self.particles[0].to_array()
#             a.extend(self.to_array_coords(self.particles[1:]))
#             return a
#         else:
#             if len(coords)>1:
#                 return coords[0].to_array().extend(self.to_array_coords(coords[1:]))
#             else:
#                 return coords[0].to_array()
#
#     def to_array_masses(self):
#         return [p.m for p in self.particles]
#
#     def generate_particle(self, m, color, lifetime):
#         x=self.x_*math.pow(10,self.x_10)
#         y = self.y_ * math.pow(10, self.y_10)
#         u = self.u_ * math.pow(10, self.u_10)
#         v = self.v_ * math.pow(10, self.v_10)
#
#         self.particles.append(Particle(x, y, u, v,m,color, lifetime))
#         self.particles_init.append(Particle(x, y, u, v, m, color, lifetime))
#     def __str__(self):
#         s = ''
#         for p in self.particles:
#             s+=str(p)+'\n'
#         return s
#     @property
#     def x(self):
#         return self.x_ * math.pow(10, self.x_10)
#
#     @property
#     def y(self):
#         return self.y_ * math.pow(10, self.y_10)
#
#     @property
#     def u(self):
#         return self.u_ * math.pow(10, self.u_10)
#
#     @property
#     def v(self):
#         return self.v_ * math.pow(10, self.v_10)





class Application(Frame):

    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.check_button_u_v_value = False
        self.check_button_x_y_value = False
        self.check_button_m_value = False

        self.graph_wided = False

        self.emitter = Emitter()

        self.method = calculate_odeint

        self.real_x_max = 1
        self.real_y_max = 1
        self.real_u_max = 0
        self.real_v_max = 0
        self.real_m_max = 0
        # self.x = 0
        # self.y = 0
        # self.u = 0
        # self.v = 0
        self.m_ = 0
        self.m_10 = 0
        self.color = ((0.0, 0.0, 0.0), 'black')
        self.to_calculate = False

        self.lifetime = 100
        self.particles = []

        self.vector_u = 0
        self.vector_v = 0
        self.point_x = 0
        self.point_y = 0

        self.u_10_min = 0
        self.u_max = 1000
        self.v_10_min = 0
        self.v_max = 1000
        self.x_10_min = 0
        self.x_max = 1000
        self.y_10_min = 0
        self.y_max = 1000
        self.m_10_min = 0
        self.t = 0

        # self.graph_fig = plt.Figure()
        # self.x_values = np.arange(-self.x_max, self.x_max, 200/(self.x_max))
        # self.y_values = np.arange(-self.y_max, self.y_max, 200 / (self.y_max))

        self.m_max = 1000

        self.disabled = False
        self.whats_wrong = {'m': False, 'x': False, 'y': False, 'u': False, 'v': False,
                            'm_10': False, 'x_10': False, 'y_10': False, 'u_10': False, 'v_10': False}

        self.parent = parent
        self.initUI()
        self.centerWindow(900,730)

    @property
    def m(self):
        return self.m_*math.pow(10,self.m_10)

    def centerWindow(self, w, h):
        # w = w
        # h = h
        sw = self.parent.winfo_screenwidth()
        sh = self.parent.winfo_screenheight()
        # self.parent.minsize(800,600)
        x = (sw - w) / 2
        y = (sh - h) / 2
        self.parent.geometry('%dx%d+%d+%d' % (w, h, x, y))

    def initUI(self):

        self.parent.title("Задача N тел")
        self.pack(fill=BOTH, expand=True)
        # Style().configure("TButton", padding=(0, 5, 0, 5), font='serif 10')
        self.main_frame = Frame(self, background='AntiqueWhite1',
                               highlightbackground='AntiqueWhite3', highlightthickness=2)
        self.main_frame.place(relheight=7/7.3, relwidth=1, relx=0, rely=0.3/7.3)
        self.initParamsI()
        # self.initMaxesI()
        self.initGraphI()
        menubar = Menu(self.parent)
        self.parent.config(menu=menubar)

        fileMenu = Menu(menubar)
        fileMenu.add_command(label="Open", command=self.onOpen)
        submenu = Menu(fileMenu)

        submenu.add_command(label="odeint", command=(lambda : self.onMethod(calculate_odeint)))
        submenu.add_command(label="верле", command=(lambda : self.onMethod(calculate_verle)))

        submenu.add_command(label="верле_thread", command=(lambda: self.onMethod(calculate_verle_threads)))
        submenu.add_command(label="верле_cython", command=(lambda: self.onMethod(calculate_verle_cython)))
        submenu.add_command(label="верле_processes", command=(lambda: self.onMethod(calculate_verle_processes)))

        fileMenu.add_cascade(label='Метод', menu=submenu, underline=0)

        fileMenu.add_separator()

        menubar.add_cascade(label="File", underline=0, menu=fileMenu)
        self.post_rendering()

    def initParamsI(self):
        self.params_frame = Frame(self.main_frame, background='AntiqueWhite1')
                               # highlightbackground='AntiqueWhite3', highlightthickness=2)
        self.params_frame.place(height=204, relwidth=1, relx=0, rely=0)

        self.u_v_canvas_frame = Frame(self.params_frame, background='AntiqueWhite1',
                               highlightbackground='AntiqueWhite3', highlightthickness=1)
        self.u_v_canvas_frame.place(height=202, width=300, relx=1, rely=0, anchor='ne')

        self.u_v_canvas = Canvas(self.u_v_canvas_frame, background='AntiqueWhite2')
        self.u_v_canvas.place(relheight=1, width=200, relx=0.999, rely=0, anchor = 'ne')
        self.u_v_canvas.bind('<Button-1>', self.onClick_uv_canvas)

        # u and v entries  -------------------------------------------------------------------------------------------
        self.u_label = Label(self.u_v_canvas_frame, text='u:', font=("Arial Bold", 12), background='AntiqueWhite1')
        self.u_label.place(relx=0.008, rely=0.06)

        self.u_entry = Entry(self.u_v_canvas_frame)
        self.u_entry.insert(0, self.emitter.u_)
        self.u_entry.place(relx=0.078, rely=0.08, width=30)
        self.u_entry.bind('<KeyRelease>', self.onKeyRelease_u)

        self.u_10_label = Label(self.u_v_canvas_frame, text='x10', font=("Arial Bold", 12), background='AntiqueWhite1')
        self.u_10_label.place(relx=0.168, rely=0.06)

        self.u_10_entry = Entry(self.u_v_canvas_frame)
        self.u_10_entry.insert(0, self.emitter.u_10)
        self.u_10_entry.place(relx=0.258, rely=0.04, width=20)
        self.u_10_entry.bind('<KeyRelease>', self.onKeyRelease_u_10)

        self.v_label = Label(self.u_v_canvas_frame, text='v:', font=("Arial Bold", 12), background='AntiqueWhite1')
        self.v_label.place(relx=0.008, rely=0.23)

        self.v_entry = Entry(self.u_v_canvas_frame, width=10)
        self.v_entry.insert(0, self.emitter.v_)
        self.v_entry.place(relx=0.078, rely=0.25, width = 30)
        self.v_entry.bind('<KeyRelease>', self.onKeyRelease_v)

        self.v_10_label = Label(self.u_v_canvas_frame, text='x10', font=("Arial Bold", 12), background='AntiqueWhite1')
        self.v_10_label.place(relx=0.168, rely=0.23)

        self.v_10_entry = Entry(self.u_v_canvas_frame)
        self.v_10_entry.insert(0, self.emitter.v_10)
        self.v_10_entry.place(relx=0.258, rely=0.19, width=20)
        self.v_10_entry.bind('<KeyRelease>', self.onKeyRelease_v_10)
        # ---------------------------------------------------------------------------------------------------------------

        self.x_y_canvas_frame = Frame(self.params_frame, background='AntiqueWhite1',
        highlightbackground='AntiqueWhite3', highlightthickness=1)
        self.x_y_canvas_frame.place(height=202, width=300, relx=0, rely=0)

        self.x_y_canvas = Canvas(self.x_y_canvas_frame, background='AntiqueWhite2')
        self.x_y_canvas.place(relheight=1, width=200, x=0.001, rely=0)
        self.x_y_canvas.bind('<Button-1>', self.onClick_xy_canvas)

        # x and y entries  -------------------------------------------------------------------------------------------
        self.x_label = Label(self.x_y_canvas_frame, text='x:', font=("Arial Bold", 12), background='AntiqueWhite1')
        self.x_label.place(x=200, rely=0.06)

        self.x_entry = Entry(self.x_y_canvas_frame, width=10)
        self.x_entry.insert(0, self.emitter.x_)
        self.x_entry.place(x=214, rely=0.08, width = 30)
        self.x_entry.bind('<KeyRelease>', self.onKeyRelease_x)

        self.x_10_label = Label(self.x_y_canvas_frame, text='x10', font=("Arial Bold", 12), background='AntiqueWhite1')
        self.x_10_label.place(x=245, rely=0.06)

        self.x_10_entry = Entry(self.x_y_canvas_frame)
        self.x_10_entry.insert(0, self.emitter.x_10)
        self.x_10_entry.place(x=275, rely=0.04, width=20)
        self.x_10_entry.bind('<KeyRelease>', self.onKeyRelease_x_10)

        self.y_label = Label(self.x_y_canvas_frame, text='y:', font=("Arial Bold", 12), background='AntiqueWhite1')
        self.y_label.place(x=200, rely=0.23)

        self.y_entry = Entry(self.x_y_canvas_frame, width=10)
        self.y_entry.insert(0, self.emitter.y_)
        self.y_entry.place(x=214, rely=0.25, width = 30)
        self.y_entry.bind('<KeyRelease>', self.onKeyRelease_y)

        self.y_10_label = Label(self.x_y_canvas_frame, text='x10', font=("Arial Bold", 12), background='AntiqueWhite1')
        self.y_10_label.place(x=245, rely=0.23)

        self.y_10_entry = Entry(self.x_y_canvas_frame)
        self.y_10_entry.insert(0, self.emitter.y_10)
        self.y_10_entry.place(x=275, rely=0.19, width=20)
        self.y_10_entry.bind('<KeyRelease>', self.onKeyRelease_y_10)
        # -------------------------------------------------------------------------------------------------------------


        # parameters  -------------------------------------------------------------------------------------------------
        self.m_frame = Frame(self.params_frame, background='AntiqueWhite1',
                             highlightbackground='AntiqueWhite3', highlightthickness=2)
        self.m_frame.place(relheight=1, width=300, relx=0.5, rely=0, anchor = 'n')

        self.m_scale = Scale(self.m_frame, from_=0, to=self.m_max, orient=HORIZONTAL,
                             background='AntiqueWhite1', command=self.onScale_m, foreground='AntiqueWhite1',
                             highlightthickness=0)
        self.m_scale.place(relwidth=7 / 11, relx=4 / 11, rely=0.5)

        self.m_label = Label(self.m_frame, text='m:', font=("Arial Bold", 12), background='AntiqueWhite1')
        self.m_label.place(relx=0, rely=0.585)

        self.m_entry = Entry(self.m_frame)
        self.m_entry.insert(0, self.m_)
        self.m_entry.place(relx=0.07, rely=0.6, width=30)
        self.m_entry.bind('<KeyRelease>', self.onKeyRelease_m)

        self.m_10_label = Label(self.m_frame, text='x10', font=("Arial Bold", 12), background='AntiqueWhite1')
        self.m_10_label.place(relx=0.17, rely=0.585)

        self.m_10_entry = Entry(self.m_frame)
        self.m_10_entry.insert(0, self.m_10)
        self.m_10_entry.place(relx=0.27, rely=0.56, width=20)
        self.m_10_entry.bind('<KeyRelease>', self.onKeyRelease_m_10)

        self.color_label = Label(self.m_frame, text='Выберите цвет:', font=("Arial Bold", 12),
                                 background='AntiqueWhite1')
        self.color_label.place(relx=0.48, rely=0.04, anchor = 'ne')

        self.button_choose_color = Button(self.m_frame, command=self.onClick_choose_color)
        self.button_choose_color.config(background=self.color[1])
        self.button_choose_color.place(relx=0.55, rely=0.05, height=20, relwidth=0.3)

        self.lifetime_label = Label(self.m_frame, text='Время жизни:', font=("Arial Bold", 12),
                                    background='AntiqueWhite1')
        self.lifetime_label.place(relx=0.48, rely=0.35, anchor = 'ne')

        self.lifetime_entry = Entry(self.m_frame, width=10)
        self.lifetime_entry.insert(0, self.lifetime)
        self.lifetime_entry.place(relx=0.55, rely=0.385, relwidth=0.3)

        self.button_add = Button(self.m_frame, text='Добавить', command=self.onClick_add)
        self.button_add.config(background='AntiqueWhite2')
        self.button_add.place(relx=0.5, rely=0.8, anchor='n')
        # -------------------------------------------------------------------------------------------------------------

    def initMaxesI(self):
        self.maxes_frame = Frame(self.main_frame, background='AntiqueWhite1',
                                 highlightbackground='AntiqueWhite3', highlightthickness=2)
        self.maxes_frame.place(height=30, relwidth=1, relx=0, y=200)

        # x and y max  -------------------------------------------------------------------------------------------
        self.x_y_max_frame = Frame(self.maxes_frame, background='AntiqueWhite1')
        self.x_y_max_frame.place(relheight=1, width=300, relx=0, y=0)

        self.x_label_max = Label(self.x_y_max_frame, text='x_max:', font=("Arial Bold", 12), background='AntiqueWhite1')
        self.x_label_max.place(x=10, rely=0.5, anchor = 'w')

        self.x_entry_max = Entry(self.x_y_max_frame, width=10)
        self.x_entry_max.insert(0, self.x_max)
        self.x_entry_max.place(x=65, rely=0.5, width = 70, anchor = 'w')
        self.x_entry_max.bind('<KeyRelease>', self.onKeyRelease_x_max)

        self.y_label_max = Label(self.x_y_max_frame, text='y_max:', font=("Arial Bold", 12), background='AntiqueWhite1')
        self.y_label_max.place(x=220, rely=0.5, anchor = 'e')

        self.y_entry_max = Entry(self.x_y_max_frame, width=10)
        self.y_entry_max.insert(0, self.y_max)
        self.y_entry_max.place(x=290, rely=0.5, width=70, anchor = 'e')
        self.y_entry_max.bind('<KeyRelease>', self.onKeyRelease_y_max)
        # -------------------------------------------------------------------------------------------------------------

        # u and v max  -------------------------------------------------------------------------------------------
        self.u_v_max_frame = Frame(self.maxes_frame, background='AntiqueWhite1')
        self.u_v_max_frame.place(relheight=1, width=300, relx=1, y=0, anchor = 'ne')

        self.u_label_max = Label(self.u_v_max_frame, text='u_max:', font=("Arial Bold", 12), background='AntiqueWhite1')
        self.u_label_max.place(x=10, rely=0.5, anchor='w')

        self.u_entry_max = Entry(self.u_v_max_frame, width=10)
        self.u_entry_max.insert(0, self.u_max)
        self.u_entry_max.place(x=65, rely=0.5, width=70, anchor='w')
        self.u_entry_max.bind('<KeyRelease>', self.onKeyRelease_u_max)

        self.v_label_max = Label(self.u_v_max_frame, text='v_max:', font=("Arial Bold", 12), background='AntiqueWhite1')
        self.v_label_max.place(x=220, rely=0.5, anchor='e')

        self.v_entry_max = Entry(self.u_v_max_frame, width=10)
        self.v_entry_max.insert(0, self.v_max)
        self.v_entry_max.place(x=290, rely=0.5, width=70, anchor='e')
        self.v_entry_max.bind('<KeyRelease>', self.onKeyRelease_v_max)
        # -------------------------------------------------------------------------------------------------------------

        # m max  -------------------------------------------------------------------------------------------
        self.m_max_frame = Frame(self.maxes_frame, background='AntiqueWhite1')
        self.m_max_frame.place(relheight=1, width=300, relx=0.5, y=0, anchor='n')

        self.m_label_max = Label(self.m_max_frame, text='m_max:', font=("Arial Bold", 12), background='AntiqueWhite1')
        self.m_label_max.place(x=90, rely=0.5, anchor='w')

        self.m_entry_max = Entry(self.m_max_frame, width=10)
        self.m_entry_max.insert(0, self.m_max)
        self.m_entry_max.place(x=150, rely=0.5, width=70, anchor='w')
        self.m_entry_max.bind('<KeyRelease>', self.onKeyRelease_m_max)

        # -------------------------------------------------------------------------------------------------------------

    def initGraphI(self):
        self.graph_frame = Frame(self.main_frame, background='AntiqueWhite1',
                                      highlightbackground='AntiqueWhite3', highlightthickness=1)
        self.graph_frame.place(height=460, width=460, relx=0.5, y=232, anchor='n')

        self.button_to_calculate = Button(self.main_frame, text="Рисовать", command = self.button_calculate)
        self.button_to_calculate.place(relx=0.1, rely=0.5, height=20, width = 100)

        self.button_to_clean = Button(self.main_frame, text="Очистить", command=self.delete_particles)
        self.button_to_clean.place(relx=0.1, rely=0.6, height=20, width=100)

        self.button_to_calculate_without_draw = Button(self.main_frame, text="Вычислить",
                                                       command=self.button_calculate_without_draw)
        self.button_to_calculate_without_draw.place(relx=0.9, rely=0.5, height=20, width=100, anchor = 'ne')

        self.button_to_wide = Button(self.main_frame, text="Увеличить",
                                                       command=self.wide_graph)
        self.button_to_wide.place(relx=0.5, y=210, height=20, width=100, anchor='n')



        self.t_label = Label(self.main_frame, text='t:', font=("Arial Bold", 12), background='AntiqueWhite1')
        self.t_label.place(relx=0.85, rely=0.6)

        self.t_entry = Entry(self.main_frame)
        self.t_entry.insert(0, 100000)
        self.t_entry.place(relx=0.9, rely=0.6, width=60)

        self.delta_t_label = Label(self.main_frame, text='dt:', font=("Arial Bold", 12), background='AntiqueWhite1')
        self.delta_t_label.place(relx=0.85, rely=0.7)

        self.delta_t_entry = Entry(self.main_frame)
        self.delta_t_entry.insert(0, 1000)
        self.delta_t_entry.place(relx=0.9, rely=0.7, width=60)

        self.fig = plt.figure(facecolor='black')

        self.graph_canvas = FigureCanvasTkAgg(self.fig, master=self.graph_frame)
        self.graph_canvas.get_tk_widget().place(relx=0, rely=0, relheight=1, relwidth=1)

        # self.toolbar = NavigationToolbar2Tk(self.graph_canvas, self.graph_frame)
        # self.toolbar.update()
        # self.graph_canvas._tkcanvas.place(relx=0.5, rely=1, relwidth = 1, height = 50, anchor = 's')

        self.ax = self.fig.add_axes([0,0,1,1], frameon=False)
        self.ax.set_xlim(0, 1), self.ax.set_xticks([])
        self.ax.set_ylim(0, 1), self.ax.set_yticks([])
        self.graph_positions = np.random.uniform(0, 1, (50, 2))
        self.graph_sizes =  np.random.uniform(50, 200, 50)
        self.graph_colors = np.array([(0,0,0,1) for i in range(50)])
        self.scat = self.ax.scatter(self.graph_positions[:, 0], self.graph_positions[:, 1],
                          s=self.graph_sizes, lw=0.5, edgecolors=self.graph_colors,
                          facecolors=self.graph_colors)
        self.anima= FuncAnimation(self.fig, self.update, interval=1)


    def delete_particles(self):
        self.real_x_max = 1
        self.real_y_max = 1
        self.real_u_max = 0
        self.real_v_max = 0
        self.real_m_max = 0
        self.emitter.particles = []


    def onMethod(self, param):
        self.method = param
        return param

    def onOpen(self):
        ftypes = [('Text files', '*.json'), ('All files', '*')]
        dlg = filedialog.Open(self, filetypes=ftypes)
        fl = dlg.show()

        if fl != '':
            text = self.readFile(fl)
            # self.txt.insert(END, text)

    def onSave(self):
        ftypes = [('Text files', '*.json'), ('All files', '*')]
        dlg = filedialog.SaveAs(self, filetypes=ftypes)
        fl = dlg.show()
        return fl

    def readFile(self, filename):
        with open(filename, 'r') as f:
            data = json.load(f)
        print(data)
        print(type(data))
        for d in data['particles'].values():
            print(d)
                # print(data)
                # print(data[0], int(data[0]))
            self.emitter.x_ = int(d['x'])
            self.emitter.y_ = int(d['y'])
            self.emitter.u_ = int(d['u'])
            self.emitter.v_ = int(d['v'])
            self.m_ = int(d['m'])
            self.lifetime = int(d['lifetime'])
                # self.color = ((int(d['color'][0]),int(data[6]),int(data[7])),'red')
            self.color = d['color']
            self.onClick_add()
                # self.emitter.generate_particle(self.m, 100, (0.0, 0.0, 0.0))

    def wide_graph(self):
        if self.graph_wided == False:
            self.params_frame.place_forget()
            self.graph_frame.place(height=800, width=800, relx=0.5, y=0, anchor='n')
            self.graph_wided = True
            self.button_to_wide.place(relx=0.5, y=5, height=20, width=100, anchor='n')
            self.button_to_wide.config(text = 'Уменьшить')

            self.button_to_calculate.place_forget()
            self.button_to_clean.place_forget()
            self.button_to_calculate_without_draw.place_forget()
            self.t_label.place_forget()
            self.t_entry.place_forget()
            self.delta_t_label.place_forget()
            self.delta_t_entry.place_forget()
            self.centerWindow(900,800)
        else:
            self.params_frame.place(height=204, relwidth=1, relx=0, rely=0)
            self.graph_frame.place(height=460, width=460, relx=0.5, y=232, anchor='n')
            self.graph_wided = False
            self.button_to_wide.place(relx=0.5, y=210, height=20, width=100, anchor='n')
            self.button_to_wide.config(text='Увеличить')

            self.button_to_calculate.place(relx=0.1, rely=0.5, height=20, width=100)
            self.button_to_clean.place(relx=0.1, rely=0.6, height=20, width=100)
            self.button_to_calculate_without_draw.place(relx=0.9, rely=0.5, height=20, width=100, anchor='ne')
            self.t_label.place(relx=0.85, rely=0.6)
            self.t_entry.place(relx=0.9, rely=0.6, width=60)
            self.delta_t_label.place(relx=0.85, rely=0.7)
            self.delta_t_entry.place(relx=0.9, rely=0.7, width=60)

            self.centerWindow(900,730)

    def button_calculate(self):
        if self.to_calculate == False:
            self.to_calculate = True
        else:
            self.to_calculate = False

    def button_calculate_without_draw(self):
        self.emitter.particles = copy.deepcopy(self.emitter.particles_init)
        t=float(self.t_entry.get())
        dt=float(self.delta_t_entry.get())
        timer = time.time()
        coords = self.method(self.emitter.particles, t, dt)
        for i, c in enumerate(coords[-1]):
            self.emitter.particles[i].x = c['x']
            self.emitter.particles[i].y = c['y']
            self.emitter.particles[i].u = c['u']
            self.emitter.particles[i].v = c['v']
        timer = time.time()-timer
        print(timer)
        filename = self.onSave()
        if filename is None:
            pass
        else:
            d = {'particles': self.emitter.to_dict(), 'time': timer, 't': self.t_entry.get(),
                 'delta_t': self.delta_t_entry.get()}
            with open(filename, 'w') as f:
                json.dump(d, f)



    # def calculate_odeint(self , t_, delta_t):
    #     t = np.linspace(0, t_, t_/delta_t+1)
    #     lk = odeint(self.f_x, self.emitter.to_array_coords(), t,
    #                 args=(self.emitter.to_array_masses(),))
    #     for i, p in enumerate(self.emitter.particles):
    #         p.x = lk[-1][i*4]
    #         p.y = lk[-1][i*4+1]
    #         p.u = lk[-1][i*4+2]
    #         p.v = lk[-1][i*4+3]
    #
    #     # return [[p.x, p.y] for p in self.emitter.particles]

    # def calculate_a(self, points_array):
    #     """
    #
    #     :param points_array:
    #     points_array[0] - x_i,
    #     points_array[1] - y_i,
    #     points_array[2] - x_j,
    #     points_array[3] - y_j,
    #     points_array[4] - m_j,
    #     :return:
    #     """
    #     summ_x = np.sum(points_array[:, 4] * (points_array[:, 0] - points_array[:, 2]) /
    #                     np.power(np.power(points_array[:, 0] - points_array[:, 2], 2)
    #                              + np.power(points_array[:, 1] - points_array[:, 3], 2), 3 / 2))
    #     summ_y = np.sum(points_array[:, 4] * (points_array[:, 1] - points_array[:, 3]) /
    #                     np.power(np.power(points_array[:, 0] - points_array[:, 2], 2) +
    #                              np.power(points_array[:, 1] - points_array[:, 3], 2), 3 / 2))
    #
    #     return (-G*summ_x,-G*summ_y)

    # def my_verle_for_xy(self, z, delta_t, a_prev):
    #     # points_array = np.array([[z[0], z[1], i[0], i[1], i[4]] for i in particles])
    #     # a = self.calculate_a(points_array)
    #     a = a_prev
    #     x_next = z[0]+z[2]*delta_t+1/2*a[0]
    #     y_next = z[1]+z[3]*delta_t+1/2*a[1]
    #     return (x_next, y_next)

    # def my_verle_for_uv(self, uv_prev, delta_t, particles, a_prev, a_next):
    #
    #     u_next = uv_prev[0] + 1/2*(a_next[0]+a_prev[0])*delta_t
    #     v_next = uv_prev[1] + 1 /2*(a_next[1] + a_prev[1]) * delta_t
    #     return (u_next, v_next)


    # def calculate_verle(self, t_, delta_t):
    #     t=np.linspace(0, t_, t_/delta_t+1)
    #     coords = np.zeros((len(self.emitter.particles),2))
    #     a = np.zeros((len(self.emitter.particles),2))
    #     a_next = np.zeros((len(self.emitter.particles),2))
    #     for tk in t[:-1]:
    #         for i, p in enumerate(self.emitter.particles):
    #             if tk == t[0]:
    #                 points_array = np.array([[p.x, p.y, pa.x, pa.y, pa.m]
    #                                          for j, pa in enumerate(self.emitter.particles) if j != i])
    #                 a[i,0], a[i,1] = self.calculate_a(points_array)
    #             lk = self.my_verle_for_xy([p.x, p.y, p.u, p.v], delta_t, a[i])
    #             coords[i,0], coords[i,1] = lk[0], lk[1]
    #         for i, p in enumerate(coords):
    #             points_array = np.array([[p.x, p.y, pa.x, pa.y, self.emitter.particles[j].m]
    #                                      for j, pa in enumerate(coords) if j != i])
    #             a_next[i, 0], a_next[i, 1] = self.calculate_a(points_array)
    #             lk = self.my_verle_for_uv([p.u, p.v], delta_t, a[i], a_next[i])
    #             self.emitter.particles[i].x = coords[i,0]
    #             self.emitter.particles[i].y = coords[i, 1]
    #             self.emitter.particles[i].u = lk[0]
    #             self.emitter.particles[i].v = lk[1]
    #
    #     # return coords


    def update(self, frame):
        coords = []
        if self.to_calculate == True:
            # particles = self.calculate_odeint(self.t, 3600)
            # t = np.linspace(0,3600,100)
            t = float(self.t_entry.get())
            dt = float(self.delta_t_entry.get())
            # particles = self.calculate_verle(t,dt)
            coords = self.method(self.emitter.particles, t, dt)
            for i, c in enumerate(coords[-1]):
                self.emitter.particles[i].x = c['x']
                self.emitter.particles[i].y = c['y']
                self.emitter.particles[i].u = c['u']
                self.emitter.particles[i].v = c['v']

        sizes = np.linspace(1,20,11)
        self.graph_positions = np.array([[i.x/self.real_x_max/2/1.1+0.5, i.y/self.real_x_max/2/1.1+0.5]
                                         for i in self.emitter.particles])

        self.graph_sizes = np.array([sizes[int(math.sqrt(i.m / self.real_m_max) * 10)] for i in self.emitter.particles])

        self.graph_colors = np.array([(i.color[0]/255,i.color[1]/255,i.color[2]/255,1) for i in self.emitter.particles])

        self.scat.set_edgecolors(self.graph_colors)
        self.scat.set_facecolors(self.graph_colors)
        self.scat.set_sizes(self.graph_sizes)
        self.scat.set_offsets(self.graph_positions)

    # def f_x(self, z, t, masses):
    #     z_ = z
    #     a=[]
    #     for i in range(int(len(z)/4)):
    #         points_array = np.array([[z_[i*4], z_[i*4+1], z_[j*4], z_[j*4+1], masses[j]]
    #                                  for j in range(int(len(z)/4)) if i != j])
    #         # a.append(self.calculate_a(points_array))
    #         summ_x = 0
    #         # summ_x = np.sum(points_array[:, 4] * (points_array[:, 0] - points_array[:, 2]) /
    #         #                 np.power(np.power(points_array[:, 0] - points_array[:, 2], 2)
    #         #                          + np.power(points_array[:, 1] - points_array[:, 3], 2), 3 / 2))
    #         # summ_y = np.sum(points_array[:, 4] * (points_array[:, 1] - points_array[:, 3]) /
    #         #                 np.power(np.power(points_array[:, 0] - points_array[:, 2], 2) +
    #         #                          np.power(points_array[:, 1] - points_array[:, 3], 2), 3 / 2))
    #         summ_y = 0
    #         for j in range(int(len(z)/4)):
    #             if i!=j:
    #                 r_3 = math.pow(math.pow(math.fabs(z_[j*4+1]-z_[i*4+1]),2)+math.pow(math.fabs(z_[j*4]-z_[i*4]),2),3/2)
    #                 summ_x+= G*masses[j]*(z_[j*4]-z_[i*4])/r_3
    #                 summ_y+=G*masses[j]*(z_[j*4+1]-z_[i*4+1])/r_3
    #         a.append([summ_x, summ_y])
    #
    #     ret = []
    #     for i in range(int(len(z_)/4)):
    #         ret.extend([z_[i*4+2],z_[i * 4 + 3],a[i][0],a[i][1]])
    #     print('here', t, z[4], z[5], z[6], z[7], len(z))
    #     return ret



    def onClick_add(self):
        smth_wrong = False
        print(self.whats_wrong)
        for value in self.whats_wrong:
            if self.whats_wrong[value]==True:
                smth_wrong=True
                break
        if smth_wrong==False:
            self.emitter.generate_particle(self.m, self.color, self.lifetime)
            if self.m>self.real_m_max:
                self.real_m_max = self.m
            if math.fabs(self.emitter.x)>self.real_x_max:
                self.real_x_max = math.fabs(self.emitter.x)
            if math.fabs(self.emitter.y)>self.real_x_max:
                self.real_x_max = math.fabs(self.emitter.y)

            if math.fabs(self.emitter.u) > self.real_u_max:
                self.real_u_max = math.fabs(self.emitter.u)
            if math.fabs(self.emitter.v)>self.real_v_max:
                self.real_v_max = math.fabs(self.emitter.v)
        else:
            print('smth_wrong')


    def onClick_choose_color(self):
        self.color = colorchooser.askcolor()[1]
        self.button_choose_color.config(background = self.color[1])
        self.draw_point()
        print(self.color)

    def smth_wrong(self, what, value):
        self.whats_wrong[what]=value

    def onKeyRelease_u(self, event):
        entry = self.u_entry.get()
        if entry.isdigit()and math.fabs(int(entry))<=self.u_max or entry != '' and ((entry[0] == '-'
                                                                          or entry[0] == '+') and entry[1:].isdigit())\
                and math.fabs(int(entry))<=self.u_max :
            self.smth_wrong('u', False)
            self.emitter.u_ = int(entry)
            self.draw_vector()
            self.draw_vector_on_graph()
            self.u_entry.config(background='white')
        else:
            self.smth_wrong('u', True)
            self.u_entry.config(background='red')

    def onKeyRelease_u_10(self, event):
        entry = self.u_10_entry.get()
        if entry.isdigit() or entry != '' and ((entry[0] == '-' or entry[0] == '+') and entry[1:].isdigit()):
            self.smth_wrong('u_10', False)
            self.emitter.u_10 = int(entry)
            self.u_10_entry.config(background='white')
        else:
            self.smth_wrong('u_10', True)
            self.u_10_entry.config(background='red')

    def onKeyRelease_v_10(self, event):
        entry = self.v_10_entry.get()
        if entry.isdigit() or entry != '' and ((entry[0] == '-' or entry[0] == '+') and entry[1:].isdigit()):
            self.smth_wrong('v_10', False)
            self.emitter.v_10 = int(entry)
            self.v_10_entry.config(background='white')
        else:
            self.smth_wrong('v_10', True)
            self.v_10_entry.config(background='red')

    def onKeyRelease_x_10(self, event):
        entry = self.x_10_entry.get()
        if entry.isdigit() or entry != '' and ((entry[0] == '-' or entry[0] == '+') and entry[1:].isdigit()):
            self.smth_wrong('x_10', False)
            self.emitter.x_10 = int(entry)
            self.x_10_entry.config(background='white')
        else:
            self.smth_wrong('x_10', True)
            self.x_10_entry.config(background='red')

    def onKeyRelease_y_10(self, event):
        entry = self.y_10_entry.get()
        if entry.isdigit() or entry != '' and ((entry[0] == '-' or entry[0] == '+') and entry[1:].isdigit()):
            self.smth_wrong('y_10', False)
            self.emitter.y_10 = int(entry)
            self.y_10_entry.config(background='white')
        else:
            self.smth_wrong('y_10', True)
            self.y_10_entry.config(background='red')
        pass

    def onKeyRelease_m_10(self, event):
        entry = self.m_10_entry.get()
        if entry.isdigit() or entry != '' and ((entry[0] == '-' or entry[0] == '+') and entry[1:].isdigit()):
            self.smth_wrong('m_10', False)
            self.m_10 = int(entry)
            self.m_10_entry.config(background='white')
        else:
            self.smth_wrong('m_10', True)
            self.m_10_entry.config(background='red')
        pass

    def onKeyRelease_v(self, event):
        entry = self.v_entry.get()
        if entry.isdigit()and math.fabs(int(entry))<=self.v_max or entry != '' and ((entry[0] == '-'
                                                                          or entry[0] == '+') and entry[1:].isdigit())\
                and math.fabs(int(entry))<=self.v_max:
            self.smth_wrong('v', False)
            self.emitter.v_ = int(entry)
            self.draw_vector()
            self.draw_vector_on_graph()
            self.v_entry.config(background='white')
        else:
            self.smth_wrong('v', True)
            self.v_entry.config(background='red')


    def onClick_uv_canvas(self, event):
        if self.disabled == True:
            return
        self.emitter.u_ = int(((event.x)-self.u_v_canvas.winfo_width()/2)/
                             (self.u_v_canvas.winfo_width()/2)*self.u_max)
        self.emitter.v_ = int((-int(event.y)+self.u_v_canvas.winfo_height()/2)/
                             (self.u_v_canvas.winfo_height()/2)*self.v_max)
        self.u_entry.delete(0,END)
        self.u_entry.insert(0, self.emitter.u)
        self.v_entry.delete(0, END)
        self.v_entry.insert(0, self.emitter.v)
        self.draw_vector()
        self.draw_vector_on_graph()
        self.u_entry.config(background='white')
        self.v_entry.config(background='white')
        print(self.x_y_canvas.winfo_width(), self.x_y_canvas.winfo_height(),
              self.u_v_canvas.winfo_width(), self.u_v_canvas.winfo_height(),
              self.params_frame.winfo_width(), self.params_frame.winfo_height())

    def onClick_xy_canvas(self, event):

        if self.disabled == True:
            return
        print(self.x_y_canvas.winfo_width())
        self.emitter.x_ = int((int(event.x)-self.x_y_canvas.winfo_width()/2)/
                             (self.x_y_canvas.winfo_width()/2)*self.x_max)
        self.emitter.y_ = int((-int(event.y)+self.x_y_canvas.winfo_height()/2)/
                             (self.x_y_canvas.winfo_height()/2)*self.y_max)
        self.x_entry.delete(0,END)
        self.x_entry.insert(0, self.emitter.x)
        self.y_entry.delete(0, END)
        self.y_entry.insert(0, self.emitter.y)
        self.draw_point()
        self.draw_vector_on_graph()
        self.x_entry.config(background='white')
        self.y_entry.config(background='white')

    def onKeyRelease_x_max(self, event):
        x = 0
        entry = self.x_entry_max.get()
        if entry.isdigit()and float(entry)!=0 or entry!='' and ((entry[0]=='-' or entry[0]=='+') and entry[1:].isdigit()):
            self.x_max = int(entry)
            self.draw_point()
            self.draw_vector_on_graph()
            self.x_entry_max.config(background = 'white')
            if self.disabled == True:
                self.to_disable()
            self.onKeyRelease_x(None)
        else:
            if self.disabled == False:
                self.to_disable()
            self.x_entry_max.config(background = 'red')

    def onKeyRelease_y_max(self, event):
        x = 0
        entry = self.y_entry_max.get()
        if entry.isdigit()and float(entry)!=0 or entry!='' and ((entry[0]=='-' or entry[0]=='+') and entry[1:].isdigit()):
            self.y_max = int(entry)
            self.draw_point()
            self.draw_vector_on_graph()
            self.y_entry_max.config(background = 'white')
            if self.disabled == True:
                self.to_disable()

            self.onKeyRelease_y(None)
        else:
            if self.disabled == False:
                self.to_disable()
            self.y_entry_max.config(background = 'red')

    def onKeyRelease_u_max(self, event):
        x = 0
        entry = self.u_entry_max.get()
        if entry.isdigit()and float(entry)!=0 or entry!='' and ((entry[0]=='-' or entry[0]=='+') and entry[1:].isdigit()):
            self.u_max = int(entry)
            self.draw_point()
            self.draw_vector_on_graph()
            self.u_entry_max.config(background = 'white')
            if self.disabled == True:
                self.to_disable()

            self.onKeyRelease_u(None)
        else:
            if self.disabled == False:
                self.to_disable()
            self.u_entry_max.config(background = 'red')

    def onKeyRelease_v_max(self, event):
        x = 0
        entry = self.v_entry_max.get()
        if entry.isdigit()and float(entry)!=0 or entry!='' and ((entry[0]=='-' or entry[0]=='+') and entry[1:].isdigit()):
            self.v_max = int(entry)
            self.draw_point()
            self.draw_vector_on_graph()
            self.v_entry_max.config(background = 'white')
            if self.disabled == True:
                self.to_disable()
            self.onKeyRelease_v(None)
        else:
            if self.disabled == False:
                self.to_disable()
            self.v_entry_max.config(background = 'red')

    def onKeyRelease_m_max(self, event):
        x = 0
        entry = self.m_entry_max.get()
        if entry.isdigit()and float(entry)!=0 or entry!='' and ((entry[0]=='-' or entry[0]=='+') and entry[1:].isdigit()):
            self.m_max = int(entry)
            self.draw_point()
            self.draw_vector_on_graph()
            self.m_entry_max.config(background = 'white')
            # self.m_scale = Scale(self.m_frame, from_=0, to=self.m_max, orient=HORIZONTAL,
            #                      background='AntiqueWhite1', command=self.onScale_m, foreground='AntiqueWhite1',
            #                      highlightthickness=0)
            self.m_scale.config(from_=0, to=self.m_max,)
            if self.disabled == True:
                self.to_disable()
            self.onKeyRelease_m(None)
        else:
            if self.disabled == False:
                self.to_disable()
            self.m_entry_max.config(background = 'red')

    def onKeyRelease_x(self, event):
        x = 0
        entry = self.x_entry.get()
        if entry.isdigit() and math.fabs(int(entry))<=self.x_max\
                or entry!='' and ((entry[0]=='-' or entry[0]=='+') and entry[1:].isdigit())\
                and math.fabs(int(entry))<=self.x_max:

            self.smth_wrong('x', False)
            self.emitter.x_ = int(entry)
            self.draw_point()
            self.draw_vector_on_graph()
            self.x_entry.config(background = 'white')
        else:
            self.smth_wrong('x', True)
            self.x_entry.config(background = 'red')

    def onKeyRelease_y(self, event):
        entry = self.y_entry.get()
        if entry.isdigit()and math.fabs(int(entry))<=self.y_max or entry != '' and ((entry[0] == '-'
                                                                          or entry[0] == '+') and entry[1:].isdigit())\
                and math.fabs(int(entry))<=self.y_max:
            self.smth_wrong('y', False)
            self.emitter.y_ = int(entry)
            self.draw_point()
            self.draw_vector_on_graph()
            self.y_entry.config(background='white')
        else:
            self.smth_wrong('y', True)
            self.y_entry.config(background='red')
        # y = 0
        # entry = self.y_entry.get()
        # if entry!='-' and entry!='+':
        #     try:
        #         y = int(entry)
        #     except ValueError:
        #         if entry != '':
        #             self.y_entry.delete(len(entry)-1,END)
        #     else:
        #         self.emitter.y = int(entry)
        #         self.draw_point()
        #         self.draw_vector_on_graph()

    def onKeyRelease_m(self, event):
        x = 0
        entry = self.m_entry.get()
        if entry.isdigit()and int(entry)<=self.m_max or entry!='' and ((entry[0]=='+') and entry[1:].isdigit()):
            self.smth_wrong('m', False)
            self.m_ = int(entry)
            self.draw_point()
            self.m_entry.config(background = 'white')
            self.m_scale.set(self.m_)
        else:
            self.smth_wrong('m', True)
            self.m_entry.config(background = 'red')

    def onScale_m(self, val):
        va = int(float(val))
        self.m_entry.delete(0, END)
        self.m_entry.insert(0, str(va))
        self.m_ = va
        self.draw_point()
        self.m_entry.config(background = 'white')
        self.smth_wrong('m', False)

    def to_disable(self):
        if self.disabled == False:
            self.x_entry.config(state = DISABLED)
            self.y_entry.config(state=DISABLED)
            self.u_entry.config(state=DISABLED)
            self.v_entry.config(state=DISABLED)
            self.button_add.config(state=DISABLED)
            self.m_scale.config(state=DISABLED)
            self.m_entry.config(state=DISABLED)

            self.disabled = True
        else:
            self.x_entry.config(state=NORMAL)
            self.y_entry.config(state=NORMAL)
            self.u_entry.config(state=NORMAL)
            self.v_entry.config(state=NORMAL)
            self.button_add.config(state=NORMAL)
            self.m_scale.config(state=NORMAL)
            self.m_entry.config(state=NORMAL)
            self.disabled = False

    def draw_vector(self):
        self.u_v_canvas.coords(self.vector_of_uv_canvas, self.u_v_canvas.winfo_width()/2,self.u_v_canvas.winfo_height()/2,
                                    self.u_v_canvas.winfo_width()/2+
                                    self.emitter.u_*(self.u_v_canvas.winfo_width()/(2*self.u_max)),
                                    self.u_v_canvas.winfo_height()/2 -
                                    self.emitter.v_*(self.u_v_canvas.winfo_height()/(2*self.v_max)))


        # self.oval_on_graph = self.u_v_canvas.create_oval(1,
        #                             1,
        #                             self.u_v_canvas.winfo_width()-1,
        #                             self.u_v_canvas.winfo_height()-1)
    def draw_vector_on_graph(self):
        a=self.emitter.u_/self.u_max*R_V_MAX

        b=self.emitter.v_/self.v_max*R_V_MAX
        if a==0 and b==0:
            cos = 0
            sin = 0
            r=0
        else:
            r = math.sqrt(a*a+b*b)
            cos = a/r
            sin = b/r

        self.x_y_canvas.coords(self.vector_of_xy_canvas, self.x_y_canvas.winfo_width() / 2 +
                               self.emitter.x_ * (self.x_y_canvas.winfo_width() / (2 * self.x_max)),
                               self.x_y_canvas.winfo_height() / 2 -
                               self.emitter.y_ * (self.x_y_canvas.winfo_height() / (2 * self.v_max)),
                               self.x_y_canvas.winfo_width() / 2 +
                               self.emitter.x_ * (self.x_y_canvas.winfo_width() / (2 * self.x_max))+
                               cos*r
                               ,
                               self.x_y_canvas.winfo_height() / 2 -
                               self.emitter.y_ * (self.x_y_canvas.winfo_height() / (2 * self.v_max))
                               -sin*r)


        # self.oval_on_graph = self.u_v_canvas.create_oval(1,
        #                             1,
        #                             self.u_v_canvas.winfo_width()-1,
        #                             self.u_v_canvas.winfo_height()-1)

    # def draw_point_and

    def draw_point(self):
        self.x_y_canvas.coords(self.point_of_xy_canvas,
                               self.x_y_canvas.winfo_width() / 2 +
                               self.emitter.x_ * (self.x_y_canvas.winfo_width() / (2 * self.x_max))
                               -self.m_/self.m_max*math.sqrt(R_MAX),
                               self.x_y_canvas.winfo_height() / 2 -
                               self.emitter.y_ * (self.x_y_canvas.winfo_height() / (2 * self.y_max))
                               +self.m_/self.m_max*math.sqrt(R_MAX),
                                    self.x_y_canvas.winfo_width()/2+
                                    self.emitter.x_*(self.x_y_canvas.winfo_width()/(2*self.x_max))
                               +self.m_/self.m_max*math.sqrt(R_MAX),
                                    self.x_y_canvas.winfo_height()/2 -
                                    self.emitter.y_*(self.x_y_canvas.winfo_height()/(2*self.y_max))
                               -self.m_/self.m_max*math.sqrt(R_MAX))

        self.x_y_canvas.itemconfig(self.point_of_xy_canvas, outline = self.color[1])

    def post_rendering(self):

        if self.x_y_canvas.winfo_width()==1:
            u_v_canvas_width = 200
            u_v_canvas_height = 200
            x_y_canvas_width = 200
            x_y_canvas_height = 200
            self.center_of_uv_canvas = self.u_v_canvas.create_oval(u_v_canvas_width / 2 - 1,
                                                                   u_v_canvas_height / 2 + 1,
                                                                   u_v_canvas_width / 2 + 1,
                                                                   u_v_canvas_height / 2 - 1, width=2)
            self.radius_of_uv_canvas = self.u_v_canvas.create_oval(1,
                                                                   1,
                                                                   u_v_canvas_width - 1,
                                                                   u_v_canvas_height - 1, width=2, outline='gray64')
            self.vector_of_uv_canvas = self.u_v_canvas.create_line(u_v_canvas_width / 2,
                                                                   u_v_canvas_height / 2,
                                                                   u_v_canvas_width / 2,
                                                                   u_v_canvas_height / 2, width=2)
            self.center_of_xy_canvas = self.x_y_canvas.create_oval(x_y_canvas_width / 2 - 1,
                                                                   x_y_canvas_height / 2 + 1,
                                                                   x_y_canvas_width / 2 + 1,
                                                                   x_y_canvas_height / 2 - 1, width=2)
            self.radius_of_xy_canvas = self.x_y_canvas.create_oval(1,
                                                                   1,
                                                                   x_y_canvas_width - 1,
                                                                   x_y_canvas_height - 1, width=2, outline='gray64')
            self.point_of_xy_canvas = self.x_y_canvas.create_oval(x_y_canvas_width / 2,
                                                                  x_y_canvas_height / 2,
                                                                  x_y_canvas_width / 2,
                                                                  x_y_canvas_height / 2, width=2)
            self.vector_of_xy_canvas = self.x_y_canvas.create_line(x_y_canvas_width / 2,
                                                                   x_y_canvas_height / 2,
                                                                   x_y_canvas_width / 2,
                                                                   x_y_canvas_height / 2, width=2)
        # else:
        #     u_v_canvas_width = self.u_v_canvas.winfo_width()
        #     u_v_canvas_height = self.u_v_canvas.winfo_height()
        #     x_y_canvas_width = self.x_y_canvas.winfo_width()
        #     x_y_canvas_height = self.x_y_canvas.winfo_height()
        #     self.x_y_canvas.coords(self.center_of_xy_canvas, x_y_canvas_width / 2 - 1,
        #                                                            x_y_canvas_height / 2 + 1,
        #                                                            x_y_canvas_width / 2 + 1,
        #                                                            x_y_canvas_height / 2 - 1)





if __name__== '__main__':
    freeze_support()
    root = Tk()
    app = Application(root)
    root.update_idletasks()
    root.mainloop()