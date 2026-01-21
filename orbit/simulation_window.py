#for relative imports
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

import copy
import math
import pyglet
import threading
import time

import orbit.gravity_engine
from orbit.gravity_engine import CelestialBody, GravityEngine
from orbit.data_logging import DataLogger
from orbit.utils import Vector2D

#initial window size
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 800
#value how much dt is changed when +/- is pressed
DT_CHANGE = 0.01
#initial simulation size factor
SIZE_FACTOR = 1.4
#trail delta in pixels
TRAIL_DELTA = 10
TRAIL_LENGTH = 50

class SimulationWindow(threading.Thread):
    def __init__(self, gravity_engine:GravityEngine, trail_active, shutdown_event:threading.Event, marked_event:threading.Event, init_draw_event:threading.Event):
        super().__init__()
        self.engine = gravity_engine
        self.trail_active = trail_active
        self.shutdown_event = shutdown_event
        self.marked_event = marked_event
        self.init_draw_event = init_draw_event

        self.width = WINDOW_WIDTH
        self.height = WINDOW_HEIGHT
        self.scaling = 1.0
        self.data_logger = DataLogger()
        self.body_shape_list = []
        self.trail_pos_list = [[] for i in range(TRAIL_LENGTH)]
        self.trail_shape_list = [[] for i in range(TRAIL_LENGTH - 1)]
        self.trail_index_list = []
        self.trail_delta = 0
        self.drawing_time = 0
        self.init_counter = 0
        self.marked_body = None
        
        self.pos_x = 0
        self.pos_y = 0

    def run(self):
        #Pyglet window setup
        self.window = pyglet.window.Window(width = self.width, height = self.height, caption = "Orbit Simulation", resizable=True)
        self.batch = pyglet.graphics.Batch()
        self.keys = pyglet.window.key.KeyStateHandler()
        self.window.set_location(orbit.control_window.WINDOW_WIDTH + 200, 200)
        #for registering events
        self.window.push_handlers(self)

        #create initial body shapes and trail shapes
        self.intial_setup()

        #schedule a function call to be called every x seconds
        pyglet.clock.schedule_interval(self.update, orbit.gravity_engine.UPDATE_RATE)
        #run the pyglet app
        pyglet.app.run()

    def intial_setup(self):
        #resize simulation size to show initial positions of celestial bodies
        self.simulation_window_resize()
        #scale trail delta intially
        self.trail_delta_scale()

        self.scaling = 1.0

        self.body_shape_list = []
        self.trail_pos_list = [[] for i in range(TRAIL_LENGTH)]
        self.trail_shape_list = [[] for i in range(TRAIL_LENGTH - 1)]
        self.trail_index_list = []

        for body_index, body in enumerate(self.engine.body_list):
            pos_x = int(self.scale_x(body.pos.x))
            pos_y = int(self.scale_x(body.pos.y))
            radius = body.radius * self.scaling
            color = body.color.get_rgb_8bit()
            self.body_shape_list.append(pyglet.shapes.Circle(pos_x, pos_y, radius=radius, color=color, batch=self.batch))

            if self.trail_active:
                for i in range(TRAIL_LENGTH):
                    self.trail_pos_list[body_index].append(Vector2D(body.pos.x, body.pos.y))
                    self.trail_shape_list[body_index].append(pyglet.shapes.Line(pos_x, pos_y, pos_x, pos_y, color=color, batch=self.batch))
                self.trail_index_list = [0] * len(self.engine.body_list)

    def update(self, dt):
        if self.init_draw_event.is_set():
            self.init_draw_event.clear()
            self.intial_setup()

        start_time = time.perf_counter()
        #wait 2 cycles for pyglet to properly setup (without this wait the gravity engine will run multiple times before the window is drawn)
        if self.init_counter <= 2:
            self.init_counter += 1
            if self.init_counter > 2:
                self.engine.running = True

        #for control window attachement
        self.pos_x, self.pos_y = self.window.get_location()

        #create copy of body_list so even when bodies get deleted, the drawing can still work
        if (len(self.engine.body_list) != 0):
            body_list = copy.deepcopy(self.engine.body_list)
            #update screen visuals
            for body_index, body in enumerate(body_list):
                self.draw_body(body, body_index)
                if self.trail_active:
                    self.update_trail(body, body_index)
                    self.draw_trail(body_index)
        
        self.drawing_time = time.perf_counter() - start_time

        #write logging information on the screen
        self.draw_log(dt)

        #check if other window was closed and if so, close myself
        if self.shutdown_event.is_set():
            self.stop()

    def draw_body(self, body:CelestialBody, body_index):
        pos_x = self.scale_x(body.pos.x)
        pos_y = self.scale_y(body.pos.y)

        #only draw when the object is visible on screen
        radius = body.radius*self.scaling
        if self.check_boundaries(pos_x, pos_y, radius):
            self.body_shape_list[body_index].visible = True
            self.body_shape_list[body_index].position = (pos_x, pos_y)
            self.body_shape_list[body_index].radius = body.radius * self.scaling
        else:
            self.body_shape_list[body_index].visible = False

    def update_trail(self, body:CelestialBody, body_index):
        #check if body position moved a delta away from the last trail index
        #ToDo: real distance calculation would be more accurate but this will do for now
        if ((math.fabs(body.pos.x - self.trail_pos_list[body_index][self.trail_index_list[body_index]].x) >= self.trail_delta) or
            (math.fabs(body.pos.y - self.trail_pos_list[body_index][self.trail_index_list[body_index]].y) >= self.trail_delta)):
            #get index of oldest position
            oldest_index = (self.trail_index_list[body_index] + 1) % (TRAIL_LENGTH)
            #overwrite oldest position to new body position
            self.trail_pos_list[body_index][oldest_index].x = body.pos.x
            self.trail_pos_list[body_index][oldest_index].y = body.pos.y
            #oldest index is now the next index to be checked against
            self.trail_index_list[body_index] = oldest_index

    def draw_trail(self, body_index):
        newest_index = self.trail_index_list[body_index]
        #go over every position in the list and draw a line between 2 points
        for i in range(len(self.trail_pos_list[body_index]) - 1):
            #next point is the second oldest one
            next_index = (newest_index - 1) % (TRAIL_LENGTH)
            x1 = self.scale_x(self.trail_pos_list[body_index][newest_index].x)
            y1 = self.scale_y(self.trail_pos_list[body_index][newest_index].y)
            x2 = self.scale_x(self.trail_pos_list[body_index][next_index].x)
            y2 = self.scale_y(self.trail_pos_list[body_index][next_index].y)
            #check either point is in the window screen
            if (self.check_boundaries(x1, y1, 0) or
                self.check_boundaries(x2, y2, 0)):
                self.trail_shape_list[body_index][i].visible = True
                self.trail_shape_list[body_index][i].x = x1
                self.trail_shape_list[body_index][i].y = y1
                self.trail_shape_list[body_index][i].x2 = x2
                self.trail_shape_list[body_index][i].y2 = y2
            #if none is on the window the line can be disabled
            else:
                self.trail_shape_list[body_index][i].visible = False
            newest_index = next_index

    def check_boundaries(self, x, y, r):
        if (((x + r >= 0) and (x - r <= self.width)) and
            ((y + r >= 0) and (y - r <= self.height))):
            return True
        return False

    def draw_log(self, dt):
        log = self.data_logger.log(dt, self.engine.simulation_time, self.drawing_time, self.engine.dt)
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
        
        range = max(max(abs(max_x), abs(min_x)), max(abs(max_y), abs(min_y)))
        self.min_x = - range * SIZE_FACTOR
        self.max_x = range * SIZE_FACTOR
        self.min_y = - range * SIZE_FACTOR
        self.max_y = range * SIZE_FACTOR

    def trail_delta_scale(self):
        simulation_per_pixel = (self.max_x - self.min_x) / self.width
        self.trail_delta = simulation_per_pixel * TRAIL_DELTA

    def scale_x(self, orig_x):
        return ((orig_x - self.min_x) / (self.max_x - self.min_x)) * self.width
    
    def scale_y(self, orig_y):
        return ((orig_y - self.min_y) / (self.max_y - self.min_y)) * self.height

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
        self.min_x = mouse_pos_x + ((self.min_x - mouse_pos_x) * scale_value)
        self.max_y = mouse_pos_y + ((self.max_y - mouse_pos_y) * scale_value)
        self.min_y = mouse_pos_y + ((self.min_y - mouse_pos_y) * scale_value)

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
        if symbol == pyglet.window.key.SPACE:
            self.engine.running = not self.engine.running

        elif (symbol == pyglet.window.key.PLUS) or (symbol == pyglet.window.key.NUM_ADD):
            #skip over 0.0
            if (math.isclose(self.engine.dt + DT_CHANGE, 0.0, abs_tol=1e-5)):
                self.engine.change_dt(self.engine.dt + (DT_CHANGE * 2))
            else:
                self.engine.change_dt(self.engine.dt + DT_CHANGE)

        elif (symbol == pyglet.window.key.MINUS) or (symbol == pyglet.window.key.NUM_SUBTRACT):
            #skip over 0.0
            if (math.isclose(self.engine.dt - DT_CHANGE, 0.0, abs_tol=1e-5)):
                self.engine.change_dt(self.engine.dt - (DT_CHANGE * 2))
            else:
                self.engine.change_dt(self.engine.dt - DT_CHANGE)
    
    def on_mouse_press(self, x, y, button, modifiers):
        #on mouse left click
        if (button == 1):
           self.marked_body = self.find_body(x, y)
           self.marked_event.set()

    def find_body(self, x, y):
        for i, body in enumerate(self.engine.body_list):
            body_x = self.scale_x(body.pos.x)
            body_y = self.scale_y(body.pos.y)
            radius = body.radius * self.scaling
            if ((x >= body_x - radius) and (x <= body_x + radius) and
                (y >= body_y - radius) and (y <= body_y + radius)):
                return i
        return None

    def on_close(self):
        #notify other thread that this window is closed
        self.shutdown_event.set()
        self.stop()

    def stop(self):
        pyglet.app.exit()