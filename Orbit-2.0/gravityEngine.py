from utils import Vector2D, Color
import math
import copy
import random

G_CONSTANT = 1.0
TRAIL_LENGTH = 10
TRAIL_DELTA = 10

class CelestialBody:
    def __init__(self, pos:Vector2D, vel:Vector2D, mass, radius = None, color_h = 360, color_s = 1.0, color_v = 1.0):
        self.pos = pos
        self.vel = vel
        self.acc = Vector2D(0.0, 0.0)

        self.prev_pos = self.pos - vel #only used for verlet integration
        self.prev_acc = Vector2D(0.0, 0.0) #used for velocity verlet integration

        self.mass = mass
        self.radius = radius if radius is not None else (math.log(mass) + 10) #x squared maybe?
        self.color = Color(color_h, color_s, color_v)

        self.trail = [Vector2D(0, 0) for i in range(TRAIL_LENGTH)]
        self.trail[0].x = pos.x
        self.trail[0].y = pos.y
        self.trail_index = 0
    
    
class GravityEngine:
    def __init__(self, alghorithm):
        #0=Euler, 1=Verlet Integration, 2=Velocity Verlet Integration
        self.alghorithm = alghorithm
        #timestep per engine call
        self.dt = 0.5

        #initialize celestial Bodies
        random.seed(3)

        #list of all celestial bodies in the simulation
        self.body_list = [
            CelestialBody(  Vector2D(+0,  +0),  Vector2D(+0,  +0),  1000,   color_h = 1, color_s = 0),
            CelestialBody(  Vector2D(+85, +0),  Vector2D(+0,  +4),  1,      color_h = 0),

            #Cool Visuals
            # CelestialBody(  Vector2D(+0,  +0),  Vector2D(+0,  +0),  1000,   color_h = 1, color_s = 0),
            # CelestialBody(  Vector2D(+50, +0),  Vector2D(+0,  +5),  1,      color_h = 0),
            # CelestialBody(  Vector2D(-50, +0),  Vector2D(+0,  -5),  1,      color_h = 55),


            # CelestialBody(  Vector2D(-70, +0),    Vector2D(+0,  -4),    1,      color_h = 105),
            # CelestialBody(  Vector2D(-40, +0),    Vector2D(+0,  -6.5),  1,      color_h = 180),
            # CelestialBody(  Vector2D(+60, +60),   Vector2D(-2,  +2),    1,      color_h = 265),
            # CelestialBody(  Vector2D(-80, -80),   Vector2D(+5,  -4),    1,      color_h = 285),
            # CelestialBody(  Vector2D(-30, +0),    Vector2D(+0,  +7.0),  1,      color_h = 325),
        ]

        #rescale prev_pos if verlet integration is active
        if self.alghorithm == 1:
            for body in self.body_list:
                self.update_prev_pos(body, self.dt / 1.0)


    def update(self):
        #Euler Method
        if (self.alghorithm == 0):
            self.update_euler()

        #Verlet Integration
        elif (self.alghorithm == 1):
            self.update_verlet()

        #Velocity Verlet Integration
        elif (self.alghorithm == 2):
            self.update_velocity_verlet()

        #update trail of every body (alghorithm independent)
        for body in self.body_list:
            self.update_trail(body)


    def update_euler(self):
        for body in self.body_list:
            body.pos = body.pos + (body.vel * self.dt)

        #update positions of every body
        self.update_acc()

        for body in self.body_list:
            body.vel = body.vel + (body.acc * self.dt)

    def update_verlet(self):
        #update forces acting on every celestial body
        self.update_acc()
        #update positions of every object
        for body in self.body_list:
            #pos(t+dt) = 2*pos(t) - pos(t-dt) + a*dt^2
            new_pos = (body.pos * 2) - body.prev_pos + (body.acc * self.dt * self.dt)
            body.prev_pos = copy.deepcopy(body.pos)
            body.pos = new_pos

    def update_velocity_verlet(self):
        for body in self.body_list:
            #pos(t+dt) = pos(t) + vel(t)*dt + 1/2*acc(t)*dt^2
            body.pos = body.pos + (body.vel * self.dt) + (body.acc * self.dt * self.dt * 0.5)

        #update forces acting on every celestial body
        self.update_acc()

        for body in self.body_list:
            #vel(t+dt) = vel(t) + 1/2*(acc(t) + acc(t+dt))*dt
            body.vel = body.vel + ((body.prev_acc + body.acc) * self.dt * 0.5)


    def update_acc(self):
        distance_x = 0.0
        distance_y = 0.0
        distance_total = 0.0
        angle_to_object = 0.0

        for body in self.body_list:
            body.prev_acc = copy.deepcopy(body.acc)
            body.acc = Vector2D(0.0, 0.0)

        i = 0
        for body in self.body_list:
            j = 0
            for other_body in self.body_list:
                #only calculate half of every combination because it is redundant
                if i < j:
                    distance_x = other_body.pos.x - body.pos.x
                    distance_y = other_body.pos.y - body.pos.y
                    distance_total = math.sqrt((distance_x * distance_x) + (distance_y  * distance_y))

                    # to avoid division by 0 and inaccurate accerleration
                    # ToDo: maybe make it variable to mass or radius
                    if (distance_total > 1.0):
                        # calculate angle to other object to separate the force correctly among both axis
                        if (distance_x > 0.0):
                            angle_to_object = math.atan(distance_y / distance_x)
                        elif (distance_x < 0.0):
                            angle_to_object = math.atan(distance_y / distance_x) + math.pi
                        else:
                            if (distance_y >= 0):
                                angle_to_object = math.pi / 2
                            else:
                                angle_to_object = math.pi * 1.5

                        # Calculate gravitational acceleration (force) to other object
                        #              m1 * m2
                        #    F = G * -----------
                        #                r^2
                        #
                        #    F = m * a --> a = F / m1
                        #
                        #    a = G * m2 / r^2
                        #
                        #    G is changed to 1 (attraction force can be adapted by changing the mass) 
                        body.acc.x += math.cos(angle_to_object) * (other_body.mass / (distance_total * distance_total)) * G_CONSTANT
                        body.acc.y += math.sin(angle_to_object) * (other_body.mass / (distance_total * distance_total)) * G_CONSTANT

                        # acceleration calculation of other object also done here to save time
                        other_body.acc.x += math.cos(angle_to_object + math.pi) * (body.mass / (distance_total * distance_total)) * G_CONSTANT
                        other_body.acc.y += math.sin(angle_to_object + math.pi) * (body.mass / (distance_total * distance_total)) * G_CONSTANT
                j += 1
            i += 1


    def update_trail(self, body:CelestialBody):
        #ToDo: real distance calculation would be more accurate but this will do for now
        if ((math.fabs(body.pos.x - body.trail[body.trail_index].x) >= TRAIL_DELTA) or
            (math.fabs(body.pos.y - body.trail[body.trail_index].y) >= TRAIL_DELTA)):
            body.trail_index = (body.trail_index + 1) % (TRAIL_LENGTH)
            body.trail[body.trail_index].x = body.pos.x
            body.trail[body.trail_index].y = body.pos.y

    def change_dt(self, change):
        new_dt = self.dt + change

        #for Verlet Integration the previous position needs to be changed according to the change of dt
        for body in self.body_list:
            self.update_prev_pos(body, (new_dt / self.dt))

        self.dt = new_dt


    def update_prev_pos(self, body, scale):
        temp_vel = body.pos - body.prev_pos
        new_vel = temp_vel * scale
        body.prev_pos = body.pos - new_vel