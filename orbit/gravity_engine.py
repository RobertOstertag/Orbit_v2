#for relative imports
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from orbit.utils import Vector2D, Color
import math
import copy

TRAIL_LENGTH = 20
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
    def __init__(self, body_list ,alghorithm):
        #0=Euler, 1=Verlet Integration, 2=Velocity Verlet Integration
        self.alghorithm = alghorithm
        #timestep per engine call
        self.dt = 0.5

        #list of all celestial bodies in the simulation
        self.body_list = body_list

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

        self.update_acc()
        #update positions of every body

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

            body.vel = (body.pos - body.prev_pos) / self.dt

    def update_velocity_verlet(self):
        for body in self.body_list:
            #pos(t+dt) = pos(t) + vel(t)*dt + 1/2*acc(t)*dt^2
            body.pos = body.pos + (body.vel * self.dt) + (0.5 * body.acc * self.dt * self.dt)

        #update forces acting on every celestial body
        self.update_acc()

        for body in self.body_list:
            #vel(t+dt) = vel(t) + 1/2*(acc(t) + acc(t+dt))*dt
            body.vel = body.vel + (0.5 * (body.prev_acc + body.acc) * self.dt)


    def update_acc(self):
        direction_x = 0.0
        direction_y = 0.0
        direction_magn = 0.0
        direction_norm_x = 0.0
        direction_norm_y = 0.0

        for body in self.body_list:
            body.prev_acc = copy.deepcopy(body.acc)
            body.acc = Vector2D(0.0, 0.0)

        i = 0
        for body in self.body_list:
            j = 0
            for other_body in self.body_list:
                #only calculate half of every combination because it is redundant
                if i < j:
                    direction_x = other_body.pos.x - body.pos.x
                    direction_y = other_body.pos.y - body.pos.y
                    direction_magn = math.sqrt(direction_x * direction_x + direction_y * direction_y)
                    #to avoid division by 0 and inaccurate accerleration
                    if (direction_magn > 1.0):
                        direction_norm_x = direction_x / direction_magn
                        direction_norm_y = direction_y / direction_magn

                        #Calculate gravitational acceleration (force) to other object
                        #              m1 * m2
                        #    F = G * -----------
                        #                r^2
                        #
                        #    F = m * a --> a = F / m1
                        #
                        #    a = G * m2 / r^2
                        #
                        #G is changed to 1 (attraction force can be adapted by changing the mass) 
                        body.acc.x += direction_norm_x * (other_body.mass / (direction_magn * direction_magn))
                        body.acc.y += direction_norm_y * (other_body.mass / (direction_magn * direction_magn))

                        #acceleration calculation of other object also done here to save time
                        other_body.acc.x += -direction_norm_x * (body.mass / (direction_magn * direction_magn))
                        other_body.acc.y += -direction_norm_y * (body.mass / (direction_magn * direction_magn))
                    
                    # #nicer looking but sadly slower than above solution
                    # direction = other_body.pos - body.pos
                    # direction_magn = direction.magnitude()
                    # direction_norm = direction / direction_magn
                    # body.acc += direction_norm * (other_body.mass / (direction_magn * direction_magn))
                    # other_body.acc += (Vector2D(0, 0) - direction_norm) * (body.mass / (direction_magn * direction_magn))
                j += 1
            i += 1


    def update_trail(self, body:CelestialBody):
        #ToDo: real distance calculation would be more accurate but this will do for now
        if ((math.fabs(body.pos.x - body.trail[body.trail_index].x) >= TRAIL_DELTA) or
            (math.fabs(body.pos.y - body.trail[body.trail_index].y) >= TRAIL_DELTA)):
            body.trail_index = (body.trail_index + 1) % (TRAIL_LENGTH)
            body.trail[body.trail_index].x = body.pos.x
            body.trail[body.trail_index].y = body.pos.y

    def change_dt(self, new_dt):
        #for Verlet Integration the previous position needs to be changed according to the change of dt
        for body in self.body_list:
            self.update_prev_pos(body, (new_dt / self.dt))

        self.dt = new_dt


    def update_prev_pos(self, body, scale):
        temp_vel = body.pos - body.prev_pos
        new_vel = temp_vel * scale
        body.prev_pos = body.pos - new_vel

if __name__ == "__main__":
    print("this is the gravity engine")