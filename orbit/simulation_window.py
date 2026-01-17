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

        number_of_bodies = len(gravity_engine.body_list)
        self.body_shape_list = [None] * number_of_bodies
        self.trail_shape_list = [None] * number_of_bodies

        self.width = WINDOW_WIDTH
        self.height = WINDOW_HEIGHT

        #resize simulation size to show initial positions of celestial bodies
        self.simulation_window_resize()
        #scale trail delta intially
        self.trail_delta_scale()

        self.scaling = 1.0

        self.data_logger = DataLogger()

        self.running = True
        self.adding = False
        self.removing = False
        self.velocity_change = False
        self.velocity_change_index = None
        self.velocity_change_start = None
        self.velocity_line_shape = None

        @self.window.event
        def on_draw():
            self.window.clear()
            self.batch.draw()

        @self.window.event
        def on_mouse_scroll(x, y, scroll_x, scroll_y):
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

        @self.window.event
        def on_resize(new_width, new_height):
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

        @self.window.event
        def on_mouse_drag(x, y, dx, dy, button, modifiers):
            #STRG is pressed while mouse dragged -> shift simulation min and max according to scaled dx or dy
            #if (modifiers & key.MOD_CTRL):
            dx_scaled = (dx / self.width) * (self.max_x - self.min_x)
            self.max_x -= dx_scaled
            self.min_x -= dx_scaled
            dy_scaled = (dy / self.height) * (self.max_y - self.min_y)
            self.max_y -= dy_scaled
            self.min_y -= dy_scaled

        @self.window.event
        def on_key_press(symbol, modifiers):
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

            elif symbol == key.A:
                self.adding = True

            elif symbol == key.R:
                self.removing = True

            elif symbol == key.V:
                self.velocity_change = True
        
        @self.window.event
        def on_key_release(symbol, modifiers):
            if symbol == key.A:
                self.adding = False
            elif symbol == key.R:
                self.removing = False
            elif symbol == key.V:
                self.velocity_change = False

        @self.window.event
        def on_close():
            pass

    def scale_x(self, orig_x):
        if ((orig_x <= self.max_x) and (orig_x >= self.min_x)):
            return ((orig_x - self.min_x) / (self.max_x - self.min_x)) * self.width
        else:
            return None
    
    def scale_y(self, orig_y):
        if ((orig_y <= self.max_y) and (orig_y >= self.min_y)):
            return ((orig_y - self.min_y) / (self.max_y - self.min_y)) * self.height
        else:
            return None
        
    def simulation_start(self, loop_function, gravity_engine, simulation_window):
        #schedule a function call to be called every x seconds
        pyglet.clock.schedule_interval(loop_function, UPDATE_TIME, gravity_engine, simulation_window)
        #run the pyglet app
        pyglet.app.run()
    

    def update(self, dt, start_time):
        #update screen visualisation
        shape_index = 0
        for i, body in enumerate(self.engine.body_list):
            self.draw_body(body, self.engine.accesory_list[i], shape_index)
            self.draw_trail(self.engine.accesory_list[i], shape_index)
            shape_index += 1
        
        #write logging information on the screen
        self.draw_log(dt, start_time, self.engine.dt)

    def draw_body(self, body:CelestialBody, accessory:BodyAccessories, shape_index):
        pos_x = self.scale_x(body.pos.x)
        pos_y = self.scale_y(body.pos.y)

        #only draw when the object is visible on screen
        if ((pos_x != None) and (pos_y != None)):
            self.body_shape_list[shape_index] = pyglet.shapes.Circle(pos_x, pos_y, radius=accessory.radius*self.scaling, color=accessory.color.get_rgb_8bit(), batch=self.batch)
        else:
            #delete object so that it will be removed from the screen
            self.body_shape_list[shape_index] = None


    def draw_trail(self, accessory:BodyAccessories, shape_index):
        trail_index = copy.deepcopy(accessory.trail_index)
        trail_list = []

        for i in (range(len(accessory.trail) - 1)):
            point_x = float(accessory.trail[int(trail_index)].x)
            point_y = float(accessory.trail[int(trail_index)].y)

            #go to next element in trail Array
            trail_index = (trail_index - 1) % len(accessory.trail)

            #check if trail element was written once
            if ((point_x != 0) or (point_y != 0)):
                scaled_x = self.scale_x(point_x)
                scaled_y = self.scale_y(point_y)
                if ((scaled_x != None) and (scaled_y != None)):
                    trail_list.append([scaled_x, scaled_y])

        #only create multiline if trail_list is big enough
        if (len(trail_list) >= 1):
            self.trail_shape_list[shape_index] = pyglet.shapes.MultiLine(*trail_list, color=accessory.color.get_rgb_8bit(), batch=self.batch)
        else:
            self.trail_shape_list[shape_index] = None


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

            # @self.window.event
            # def on_mouse_drag(x, y, dx, dy, button, modifiers):
            #     #STRG is pressed while mouse dragged -> shift simulation min and max according to scaled dx or dy
            #     if (modifiers & key.MOD_CTRL):
            #         dx_scaled = (dx / self.width) * (self.max_x - self.min_x)
            #         self.max_x -= dx_scaled
            #         self.min_x -= dx_scaled
            #         dy_scaled = (dy / self.height) * (self.max_y - self.min_y)
            #         self.max_y -= dy_scaled
            #         self.min_y -= dy_scaled
                
            #     #only change bodies when paused
            #     if (self.running == False):
            #         #draw line to show velocity
            #         if (self.velocity_change_index != None):
            #             body = self.celestialBodies[self.velocity_change_index]
            #             start_x = self.velocity_change_start.x
            #             start_y = self.velocity_change_start.y
            #             self.velocity_line_shape = pyglet.shapes.Line( start_x, start_y,
            #                                                     x, y,
            #                                                     color = (int(body.color.r), int(body.color.g), int(body.color.b)),
            #                                                     batch = self.batch)
            #         else:
            #             self.velocity_line_shape = None
                        
                
            # @self.window.event
            # def on_mouse_press(x, y, button, modifiers):
            #     #only change bodies when paused
            #     if (self.running == False):
            #         #add body
            #         if (self.adding == True):
            #             pos_x = ((x / self.width) * (self.max_x - self.min_x)) + self.min_x
            #             pos_y = ((y / self.height) * (self.max_y - self.min_y)) + self.min_y
            #             vel_x = (random.random() * 10) - 5
            #             vel_y = (random.random() * 10) - 5
            #             self.celestialBodies.append(CelestialBody(Vector2D(pos_x, pos_y), Vector2D(vel_x,  vel_y), 1, color_h = random.random()))
            #         #remove body
            #         elif (self.removing == True):
            #             index = self.find_celestial_body(x, y)
            #             if ((index != None) and (index < len(self.celestialBodies))):
            #                 self.celestialBodies.pop(index)
            #         #change velocity of body
            #         if (self.velocity_change == True):
            #             index = self.find_celestial_body(x, y)
            #             print("Found: ", index)
            #             if (index != None):
            #                 self.velocity_change_index = index
            #                 body = self.celestialBodies[index]
            #                 self.velocity_change_start = Vector2D(self.scale_x(body.pos.x), self.scale_y(body.pos.y))
                        

            # @self.window.event
            # def on_mouse_release(x, y, button, modifiers):
            #     #change velocity of body
            #     if (self.velocity_change_index != None):
            #         self.celestialBodies[self.velocity_change_index].prev_pos.x = self.celestialBodies[self.velocity_change_index].pos.x - ((x - self.velocity_change_start.x) / 20)
            #         self.celestialBodies[self.velocity_change_index].prev_pos.y = self.celestialBodies[self.velocity_change_index].pos.y - ((y - self.velocity_change_start.y) / 20)
            #         self.velocity_change_index = None
            #         self.velocity_change_start = None
            #         self.velocity_line_shape = None



            
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