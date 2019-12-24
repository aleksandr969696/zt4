import math

class Particle:

    def __init__(self, x=0, y=0, u=0, v=0, m=0, color=None, lifetime=0):
        self.x = x
        self.y = y
        self.u = u
        self.v = v


        # self.x_10 = x_10
        # self.y_10 = y_10
        # self.u_10 = u_10
        # self.v_10 = v_10
        self.m = m
        # self.m_10 = m_10
        self.color = color
        self.lifetime = lifetime

    def __str__(self):
        s = 'x: '+str(self.x)+' y:'+ str(self.y) + ' u:'+str(self.u)+' v:'+str(self.v)
        return s

    def to_array_coords(self):
        return [self.x, self.y, self.u, self.v]

    def to_dict(self):
        return {'x': self.x, 'y': self.y, 'u': self.u, 'v': self.v, 'm': self.m,
                'lifetime': self.lifetime, 'color': self.color}



class Emitter:

    def __init__(self, x=0, y=0, u=0, v=0, x_10=0, y_10=0, u_10=0, v_10=0):
        self.x_ = x
        self.y_ = y
        self.u_ = u
        self.v_ = v
        self.x_10 = x_10
        self.y_10 = y_10
        self.u_10 = u_10
        self.v_10 = v_10
        self.particles = []
        self.particles_init = []

    def to_dict(self):
        d = {}
        for i, p in enumerate(self.particles):
            d[i] = p.to_dict()
        return d

    def to_array_coords(self, coords = None):
        if coords is None:
            a = self.particles[0].to_array()
            a.extend(self.to_array_coords(self.particles[1:]))
            return a
        else:
            if len(coords)>1:
                return coords[0].to_array().extend(self.to_array_coords(coords[1:]))
            else:
                return coords[0].to_array()

    def to_array_masses(self):
        return [p.m for p in self.particles]

    def generate_particle(self, m, color, lifetime):
        x=self.x_*math.pow(10,self.x_10)
        y = self.y_ * math.pow(10, self.y_10)
        u = self.u_ * math.pow(10, self.u_10)
        v = self.v_ * math.pow(10, self.v_10)

        self.particles.append(Particle(x, y, u, v,m,color, lifetime))
        self.particles_init.append(Particle(x, y, u, v, m, color, lifetime))
    def __str__(self):
        s = ''
        for p in self.particles:
            s+=str(p)+'\n'
        return s
    @property
    def x(self):
        return self.x_ * math.pow(10, self.x_10)

    @property
    def y(self):
        return self.y_ * math.pow(10, self.y_10)

    @property
    def u(self):
        return self.u_ * math.pow(10, self.u_10)

    @property
    def v(self):
        return self.v_ * math.pow(10, self.v_10)