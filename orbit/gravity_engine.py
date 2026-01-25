#for relative imports
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

import math
import copy
import time
import threading
import queue

from orbit.utils import Vector2D, Color, ControlEvents
import orbit.presets

UPDATE_RATE = 1/60.0
GRAVITIONAL_CONSTANT = 1 #6.6743e-11
START_DT = 0.01
#value how much dt is changed when +/- is pressed
DT_CHANGE = 0.01
    
class CelestialBody:
    def __init__(self, pos:Vector2D, vel:Vector2D, mass, radius, color_h = 360, color_s = 1.0, color_v = 1.0):
        self.pos = pos
        self.vel = vel
        self.acc = Vector2D(0.0, 0.0)
        self.prev_pos = self.pos - vel #only used for verlet integration
        self.prev_acc = Vector2D(0.0, 0.0) #used for velocity verlet integration
        self.mass = mass
        self.radius = radius
        self.color = Color(color_h, color_s, color_v)

class GravityEngine(threading.Thread):
    def __init__(self, alghorithm, body_pos_queue:queue.Queue, events:ControlEvents):
        super().__init__()
        #0=Euler, 1=Verlet Integration, 2=Velocity Verlet Integration
        self.alghorithm = alghorithm
        #queue
        self.body_pos_queue = body_pos_queue
        #save references to all events
        self.events = events
        #timestep per engine call
        self.dt = START_DT
        #list of all celestial bodies in the simulation
        self.body_list = []
        #for color picking when new bodies are added
        self.hue = 0
        #for time measurement how long the simulation took
        self.simulation_time = 0
        #for preset loading
        self.preset = orbit.presets.PRESETS[2]
        self.events.load_preset.set()

        self.events.running.set()

    def run(self):
        accumalator = 0
        last = time.perf_counter()

        #run engine until either simulation window or control window is closed
        while not self.events.stop.is_set():
            now = time.perf_counter()
            accumalator += now - last
            last = now
            while accumalator >= UPDATE_RATE:
                self.update()
                accumalator -= UPDATE_RATE
            #without this line the program freezes
            time.sleep(0)

    def update(self):
        self.handle_presets()
        self.handle_dt()

        if self.events.running.is_set():
            start_time = time.perf_counter()

            #Euler Method
            if (self.alghorithm == 0):
                self.euler_method()

            #Verlet Integration
            elif (self.alghorithm == 1):
                self.verlet_integration()

            #Velocity Verlet Integration
            elif (self.alghorithm == 2):
                self.velocity_verlet_integration()

            #Runge-Kutta 4 Method
            elif (self.alghorithm == 3):
                self.runge_kutta_4_method()


            #delete remaining queue object if possible
            try: self.body_pos_queue.get_nowait()
            except queue.Empty: pass
            #put new bodies into queue
            self.body_pos_queue.put_nowait(self.body_list)
            
            self.simulation_time = time.perf_counter() - start_time


    def euler_method(self):
        self.calculate_acc(self.body_list)

        for body in self.body_list:
            body.vel = body.vel + (body.acc * self.dt)

        for body in self.body_list:
            body.pos = body.pos + (body.vel * self.dt)


    def verlet_integration(self):
        #calculate acceleration for every celestial body
        self.calculate_acc(self.body_list)
        #update positions of every object
        for body in self.body_list:
            #pos(t+dt) = 2*pos(t) - pos(t-dt) + a*dt^2
            new_pos = (body.pos * 2) - body.prev_pos + (body.acc * self.dt * self.dt)
            body.prev_pos = copy.deepcopy(body.pos)
            body.pos = new_pos

            #not needed for verlet integration but used for energy calculation and other evaluations
            body.vel = (body.pos - body.prev_pos) / self.dt


    def velocity_verlet_integration(self):
        for body in self.body_list:
            #pos(t+dt) = pos(t) + vel(t)*dt + 1/2*acc(t)*dt^2
            body.pos = body.pos + (body.vel * self.dt) + (0.5 * body.acc * self.dt * self.dt)

        #update forces acting on every celestial body
        self.calculate_acc(self.body_list)

        for body in self.body_list:
            #vel(t+dt) = vel(t) + 1/2*(acc(t) + acc(t+dt))*dt
            body.vel = body.vel + (0.5 * (body.prev_acc + body.acc) * self.dt)


    def runge_kutta_4_method(self):
        body_list_1 = copy.deepcopy(self.body_list)
        body_list_2 = copy.deepcopy(self.body_list)
        body_list_3 = copy.deepcopy(self.body_list)
        body_list_4 = copy.deepcopy(self.body_list)

        #RK step 1
        self.calculate_acc(body_list_1)
        
        #RK step 2
        for i, body in enumerate(body_list_2):
            body.pos += 0.5 * self.dt * body_list_1[i].vel
            body.vel += 0.5 * self.dt * body_list_1[i].acc
        self.calculate_acc(body_list_2)

        #RK step 3
        for i, body in enumerate(body_list_3):
            body.pos += 0.5 * self.dt * body_list_2[i].vel
            body.vel += 0.5 * self.dt * body_list_2[i].acc
        self.calculate_acc(body_list_3)

        #RK step 4
        for i, body in enumerate(body_list_4):
            body.pos += self.dt * body_list_3[i].vel
            body.vel += self.dt * body_list_3[i].acc
        self.calculate_acc(body_list_4)

        #RK final averaging
        for i, body in enumerate(self.body_list):
            body.pos += ((self.dt / 6) * (body_list_1[i].vel + (2 * body_list_2[i].vel) + (2 * body_list_3[i].vel) + body_list_4[i].vel))
            body.vel += ((self.dt / 6) * (body_list_1[i].acc + (2 * body_list_2[i].acc) + (2 * body_list_3[i].acc) + body_list_4[i].acc))


    def calculate_acc(self, body_list):
        direction_x = 0.0
        direction_y = 0.0
        direction_magn = 0.0
        direction_norm_x = 0.0
        direction_norm_y = 0.0

        for body in body_list:
            body.prev_acc = copy.deepcopy(body.acc)
            body.acc = Vector2D(0.0, 0.0)

        i = 0
        for body in body_list:
            j = 0
            for other_body in body_list:
                #only calculate half of every combination because it is redundant
                if i < j:
                    direction_x = other_body.pos.x - body.pos.x
                    direction_y = other_body.pos.y - body.pos.y
                    direction_magn = math.sqrt(direction_x * direction_x + direction_y * direction_y)
                    #to avoid division by 0 and inaccurate accerleration
                    if (direction_magn > 0.00001):
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
                        body.acc.x += direction_norm_x * GRAVITIONAL_CONSTANT * (other_body.mass / (direction_magn * direction_magn))
                        body.acc.y += direction_norm_y * GRAVITIONAL_CONSTANT * (other_body.mass / (direction_magn * direction_magn))

                        #acceleration calculation of other object also done here to save time
                        other_body.acc.x += -direction_norm_x * GRAVITIONAL_CONSTANT * (body.mass / (direction_magn * direction_magn))
                        other_body.acc.y += -direction_norm_y * GRAVITIONAL_CONSTANT * (body.mass / (direction_magn * direction_magn))
                    
                    # #nicer looking but sadly slower than above solution
                    # direction = other_body.pos - body.pos
                    # direction_magn = direction.magnitude()
                    # direction_norm = direction / direction_magn
                    # body.acc += direction_norm * (other_body.mass / (direction_magn * direction_magn))
                    # other_body.acc += (Vector2D(0, 0) - direction_norm) * (body.mass / (direction_magn * direction_magn))
                j += 1
            i += 1

    def add_body(self, pos_x, pos_y, vel_x, vel_y, mass):
        body = CelestialBody(Vector2D(pos_x, pos_y), Vector2D(vel_x, vel_y), mass=mass, radius=math.sqrt(mass)+4, color_h=self.hue)
        #rescale prev_pos if verlet integration is active
        if self.alghorithm == 1:
            self.update_prev_pos(body, self.dt)
        #add body to list
        self.body_list.append(body)
        self.hue += 55

    def delete_body(self, index):
        if index < len(self.body_list):
            self.body_list.pop(index)
            
    def handle_presets(self):
        if self.events.load_preset.is_set():
            self.events.load_preset.clear()
            #delete all bodies
            self.body_list.clear()
            #get new preset
            match self.preset:
                case "Simple":
                    preset_list = orbit.presets.SIMPLE
                case "Many Bodies":
                    preset_list = orbit.presets.MANY_BODIES
                case "Figure Eight":
                    preset_list = orbit.presets.FIGURE_8
                case "Broucke 1":
                    preset_list = orbit.presets.BROUCKE_1
                case "Broucke 2":
                    preset_list = orbit.presets.BROUCKE_2
                case "Broucke 3":
                    preset_list = orbit.presets.BROUCKE_3
                case "Broucke 4":
                    preset_list = orbit.presets.BROUCKE_4
                case "Sheen 1":
                    preset_list = orbit.presets.SHEEN_1

            #add all bodies from presets to body_list
            for index, preset_body in enumerate(range(len(preset_list))):
                self.add_body(preset_list[index][0], preset_list[index][1], preset_list[index][2], preset_list[index][3], preset_list[index][4])
            
            self.hue = 0

            #notify simulation window to redraw everything
            self.events.initialize.set()

    def handle_dt(self):
        if self.events.dt_increment.is_set():
            #skip over 0.0
            if (math.isclose(self.dt + DT_CHANGE, 0.0, abs_tol=1e-5)):
                self.change_dt(self.dt + (DT_CHANGE * 2))
            else:
                self.change_dt(self.dt + DT_CHANGE)
            self.events.dt_increment.clear()
        
        if self.events.dt_decrement.is_set():
            #skip over 0.0
            if (math.isclose(self.dt - DT_CHANGE, 0.0, abs_tol=1e-5)):
                self.change_dt(self.dt - (DT_CHANGE * 2))
            else:
                self.change_dt(self.dt - DT_CHANGE)
            self.events.dt_decrement.clear()

    def change_dt(self, new_dt):
        #for Verlet Integration the previous position needs to be changed according to the change of dt
        for body in self.body_list:
            self.update_prev_pos(body, (new_dt / self.dt))
        self.dt = new_dt

    def update_prev_pos(self, body, scale):
        temp_vel = body.pos - body.prev_pos
        new_vel = temp_vel * scale
        body.prev_pos = body.pos - new_vel

    def get_body_information(self, index):
        if index < len(self.body_list):
            mass = self.body_list[index].mass
            pos_x = self.body_list[index].pos.x
            pos_y = self.body_list[index].pos.y
            vel_x = self.body_list[index].vel.x
            vel_y = self.body_list[index].vel.y
            return (mass, pos_x, pos_y, vel_x, vel_y)
        else:
            return (0, 0, 0, 0, 0)
    
    def set_preset(self, preset_name):
        self.preset = preset_name


if __name__ == "__main__":
    print("This is the gravity engine")