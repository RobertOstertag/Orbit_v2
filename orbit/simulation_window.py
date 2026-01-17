#for relative imports
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

import copy
import math
from pyglet.window import Window, key
import pyglet

from orbit.gravity_engine import CelestialBody, BodyAccessories, GravityEngine
from orbit.data_logging import DataLogger

#initial window size
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 800
#how often the simulation will be called (60 times per second)
UPDATE_TIME = 1/60.0
#value how much dt is changed when +/- is pressed
DT_CHANGE = 0.01
#initial simulation size factor
SIZE_FACTOR = 1.4
#trail delta in pixels
TRAIL_DELTA = 10

class SimulationWindow:
    def __init__(self, gravity_engine:GravityEngine):
        #Pyglet window setup
        self.window = Window(width = WINDOW_WIDTH, height = WINDOW_HEIGHT, caption = "Orbit Simulation", resizable=True)
        self.batch = pyglet.graphics.Batch()
        self.keys = key.KeyStateHandler()
        self.window.push_handlers(self.keys)
        self.engine = gravity_engine
        #for registering events
        self.window.push_handlers(self)

        self.width = WINDOW_WIDTH
        self.height = WINDOW_HEIGHT

        #resize simulation size to show initial positions of celestial bodies
        self.simulation_window_resize()
        #scale trail delta intially
        self.trail_delta_scale()

        self.scaling = 1.0
        self.data_logger = DataLogger()
        self.running = True

        self.body_shape_list = []
        self.trail_shape_list = [None] * len(gravity_engine.body_list)

        #create initial bodies
        for index, body in enumerate(self.engine.body_list):
            pos_x = self.scale_x(body.pos.x)
            pos_y = self.scale_x(body.pos.y)
            radius = self.engine.accesory_list[index].radius * self.scaling
            color = self.engine.accesory_list[index].color.get_rgb_8bit()
            self.body_shape_list.append(pyglet.shapes.Circle(pos_x, pos_y, radius=radius, color=color, batch=self.batch))
    
    def update(self, dt, start_time):
        #update screen visualisation
        for index, body in enumerate(self.engine.body_list):
            self.draw_body(body, self.engine.accesory_list[index], index)
            self.draw_trail(self.engine.accesory_list[index], index)

        #write logging information on the screen
        self.draw_log(dt, start_time, self.engine.dt)

    def simulation_start(self, loop_function, gravity_engine, simulation_window):
        #schedule a function call to be called every x seconds
        pyglet.clock.schedule_interval(loop_function, UPDATE_TIME, gravity_engine, simulation_window)
        #run the pyglet app
        pyglet.app.run()

    def draw_body(self, body:CelestialBody, accessory:BodyAccessories, shape_index):
        pos_x = self.scale_x(body.pos.x)
        pos_y = self.scale_y(body.pos.y)

        #only draw when the object is visible on screen
        radius = accessory.radius*self.scaling
        if self.check_boundary(pos_x, pos_y, radius):
            self.body_shape_list[shape_index].visible = True
            self.body_shape_list[shape_index].position = (pos_x, pos_y)
            self.body_shape_list[shape_index].radius = accessory.radius * self.scaling
        else:
            self.body_shape_list[shape_index].visible = False


    def draw_trail(self, accessory:BodyAccessories, shape_index):
        trail_index = copy.deepcopy(accessory.trail_index)
        trail_list = []

        valid = False
        for i in (range(len(accessory.trail) - 1)):
            point_x = float(accessory.trail[int(trail_index)].x)
            point_y = float(accessory.trail[int(trail_index)].y)

            #go to next element in trail Array
            trail_index = (trail_index - 1) % len(accessory.trail)

            #check if trail element was written once (initial all zeroes)
            if ((point_x != 0) or (point_y != 0)):
                scaled_x = self.scale_x(point_x)
                scaled_y = self.scale_y(point_y)
                trail_list.append([scaled_x, scaled_y])

                if (self.check_boundary(scaled_x, scaled_y, 0) == True):
                    valid = True

        #create multiline if one point of trail_list is on the screen
        if valid == True:
            self.trail_shape_list[shape_index] = pyglet.shapes.MultiLine(*trail_list, color=accessory.color.get_rgb_8bit(), batch=self.batch)
        else:
            self.trail_shape_list[shape_index] = None

    def check_boundary(self, x, y, r):
        if (((x + r >= 0) and (x - r <= self.width)) and
            ((y + r >= 0) and (y - r <= self.height))):
            return True
        return False

    def draw_log(self, dt, start_time, speed):
        log = self.data_logger.log(dt, start_time, UPDATE_TIME, speed)
        self.label = pyglet.text.Label(
                        log, font_name='Consolas', font_size=12,
                        x=10, y=self.height-10, anchor_x='left', anchor_y='top',
                        batch=self.batch, multiline=True, width=300)


    def simulation_window_resize(self):
        min_x, max_x, min_y, max_y = 0.0, 0.0, 0.0, 0.0
        for body in self.engine.body_list:
            if body.pos.x < min_x:
                min_x = copy.deepcopy(body.pos.x)
            if body.pos.x > max_x:
                max_x = copy.deepcopy(body.pos.x)
            if body.pos.y < min_y:
                min_y = copy.deepcopy(body.pos.y)
            if body.pos.y > max_y:
                max_y = copy.deepcopy(body.pos.y)
        
        if (max_x > -min_x):
            min_x = -max_x
        else:
            max_x = -min_x
        if (max_y > -min_y):
            min_y = -max_y
        else:
            max_y = -min_y

        if (max_x - min_x) > (max_y - min_y):
            self.min_x = min_x * SIZE_FACTOR
            self.max_x = max_x * SIZE_FACTOR
            self.min_y = min_x * SIZE_FACTOR
            self.max_y = max_x * SIZE_FACTOR
        else:
            self.min_x = min_y * SIZE_FACTOR
            self.max_x = max_y * SIZE_FACTOR
            self.min_y = min_y * SIZE_FACTOR
            self.max_y = max_y * SIZE_FACTOR

    def trail_delta_scale(self):
        simulation_per_pixel = (self.max_x - self.min_x) / self.width
        self.engine.trail_delta = simulation_per_pixel * TRAIL_DELTA

    def scale_x(self, orig_x):
        return ((orig_x - self.min_x) / (self.max_x - self.min_x)) * self.width
    
    def scale_y(self, orig_y):
        return ((orig_y - self.min_y) / (self.max_y - self.min_y)) * self.height

        # def find_celestial_body(self, x, y):
        #     for i in range(len(self.celestialBodies)):
        #         scaled_radius = self.celestialBodies[i].radius * self.scaling
        #         mouse_max_x = (((x + scaled_radius) / self.width) * (self.max_x - self.min_x)) + self.min_x
        #         mouse_min_x = (((x - scaled_radius) / self.width) * (self.max_x - self.min_x)) + self.min_x
        #         mouse_max_y = (((y + scaled_radius) / self.height) * (self.max_y - self.min_y)) + self.min_y 
        #         mouse_min_y = (((y - scaled_radius) / self.height) * (self.max_y - self.min_y)) + self.min_y
        #         if ((self.celestialBodies[i].pos.x > mouse_min_x) and
        #             (self.celestialBodies[i].pos.x < mouse_max_x) and
        #             (self.celestialBodies[i].pos.y > mouse_min_y) and
        #             (self.celestialBodies[i].pos.y < mouse_max_y)):
        #             return i
        #     return None

    def on_draw(self):
        self.window.clear()
        self.batch.draw()

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        #depending on scroll wheel direction set scaling value
        if (scroll_y > 0):
            scale_value = 2/3
        else:
            scale_value = 3/2

        #not needed here but used for radius scaling
        self.scaling = self.scaling / scale_value
        
        #transform mouse position from window to simulation frame
        mouse_pos_x = ((x / self.width) * (self.max_x - self.min_x)) + self.min_x
        mouse_pos_y = ((y / self.height) * (self.max_y - self.min_y)) + self.min_y

        #update simulation size according to mouse position
        self.max_x = mouse_pos_x + ((self.max_x - mouse_pos_x) * scale_value)
        self.min_x = mouse_pos_x - ((mouse_pos_x - self.min_x) * scale_value)
        self.max_y = mouse_pos_y + ((self.max_y - mouse_pos_y) * scale_value)
        self.min_y = mouse_pos_y - ((mouse_pos_y - self.min_y) * scale_value)

    def on_resize(self, new_width, new_height):
        #calculate change of window screen and accordingly change simulation sizes
        change_x = ((new_width - self.width) / self.width)
        self.max_x += self.max_x * change_x
        self.min_x += self.min_x * change_x
        change_y = ((new_height - self.height) / self.height)
        self.max_y += self.max_y * change_y
        self.min_y += self.min_y * change_y

        #udpate internal window size
        self.width = new_width
        self.height = new_height

    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        #shift simulation min and max according to scaled dx or dy
        dx_scaled = (dx / self.width) * (self.max_x - self.min_x)
        self.max_x -= dx_scaled
        self.min_x -= dx_scaled
        dy_scaled = (dy / self.height) * (self.max_y - self.min_y)
        self.max_y -= dy_scaled
        self.min_y -= dy_scaled

    def on_key_press(self, symbol, modifiers):
        if symbol == key.SPACE:
            self.running = not self.running

        elif (symbol == key.PLUS) or (symbol == key.NUM_ADD):
            #skip over 0.0
            if (math.isclose(self.engine.dt + DT_CHANGE, 0.0, abs_tol=1e-5)):
                self.engine.change_dt(self.engine.dt + (DT_CHANGE * 2))
            else:
                self.engine.change_dt(self.engine.dt + DT_CHANGE)

        elif (symbol == key.MINUS) or (symbol == key.NUM_SUBTRACT):
            #skip over 0.0
            if (math.isclose(self.engine.dt - DT_CHANGE, 0.0, abs_tol=1e-5)):
                self.engine.change_dt(self.engine.dt - (DT_CHANGE * 2))
            else:
                self.engine.change_dt(self.engine.dt - DT_CHANGE)
    

    def on_close(self):
        pass