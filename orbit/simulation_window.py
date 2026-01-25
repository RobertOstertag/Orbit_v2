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
import queue

import orbit.gravity_engine
from orbit.gravity_engine import CelestialBody, GravityEngine
from orbit.data_logging import DataLogger
from orbit.utils import Vector2D, ControlEvents

#initial window size
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 800
#initial simulation size factor
SIZE_FACTOR = 1.4
#trail delta in pixels
TRAIL_DELTA = 10
TRAIL_LENGTH = 50
    
class SimulationWindow(threading.Thread):
    def __init__(self, gravity_engine:GravityEngine, trail_active, body_pos_queue:queue.Queue, events:ControlEvents):
        super().__init__()
        self.engine = gravity_engine
        self.trail_active = trail_active
        self.body_pos_queue = body_pos_queue
        self.events = events

        self.width = WINDOW_WIDTH
        self.height = WINDOW_HEIGHT
        self.scaling = 1.0
        self.data_logger = DataLogger()
        self.body_shape_list = []
        self.trail_shape_list = [[] for i in range(TRAIL_LENGTH)]
        self.trail_index_list = []
        self.drawing_time = 0
        self.marked_body = None
        self.min_x = -1
        self.max_x = +1
        self.min_y = -1
        self.max_y = +1
        self.running = True
        
        self.pos_x = 0
        self.pos_y = 0

    def run(self):
        #Pyglet window setup
        self.window = pyglet.window.Window(width = self.width, height = self.height, caption = "Orbit Simulation", resizable=True)
        self.batch = pyglet.graphics.Batch()
        self.keys = pyglet.window.key.KeyStateHandler()
        self.window.set_location(orbit.control_window.WINDOW_WIDTH + 200, 200)
        #for registering events like on_draw, on_scroll, etc.
        self.window.push_handlers(self)
        #schedule the update function to be called every x ms
        #pyglet.clock.schedule(self.update)
        pyglet.clock.schedule_interval(self.update, orbit.gravity_engine.UPDATE_RATE)
        #run the pyglet app
        pyglet.app.run()

    def update(self, dt):
        #check if window needs to be closed
        if not self.events.stop.is_set():
            #check if new body positions are available
            try: self.bodies = self.body_pos_queue.get_nowait()
            except queue.Empty:
                pass
            
            #initialize all shapes and other necessary parts when requested
            self.initialize_if_needed(self.bodies)
            #for control_window attachement
            self.pos_x, self.pos_y = self.window.get_location()

            start_time = time.perf_counter()
            #update screen visuals
            if self.running:
                for body_index, body in enumerate(self.bodies):
                    self.draw_body(body, body_index)
                if self.trail_active:
                    for shape_index, body_shape in enumerate(self.body_shape_list):
                        self.draw_trail(body_shape, shape_index)
            self.drawing_time = time.perf_counter() - start_time

            #write logging information on the screen
            self.draw_log()
        else:
            self.stop()

    def initialize_if_needed(self, bodies):
        if self.events.initialize.is_set():
            #resize simulation size to show initial positions of celestial bodies
            self.simulation_window_resize()

            self.scaling = 1.0
            self.body_shape_list = []
            self.trail_shape_list = [[] for i in range(TRAIL_LENGTH - 1)]
            self.trail_index_list = []

            #create a shape for every body
            for body_index, body in enumerate(bodies):
                pos_x = int(self.world_to_screen(body.pos.x, self.min_x, self.max_x, self.width))
                pos_y = int(self.world_to_screen(body.pos.y, self.min_y, self.max_y, self.height))
                radius = body.radius * self.scaling
                color = body.color.get_rgb_8bit()
                self.body_shape_list.append(pyglet.shapes.Circle(pos_x, pos_y, radius=radius, color=color, batch=self.batch))

                #for every body create a list of trail shapes
                if self.trail_active:
                    for i in range(TRAIL_LENGTH):
                        self.trail_shape_list[body_index].append(pyglet.shapes.Line(pos_x, pos_y, pos_x, pos_y, color=color, batch=self.batch))
                #add a list of ring buffer indices
                self.trail_index_list = [0] * len(bodies)

            #clear event
            self.events.initialize.clear()

    def draw_body(self, body:CelestialBody, body_index):
        pos_x = self.world_to_screen(body.pos.x, self.min_x, self.max_x, self.width)
        pos_y = self.world_to_screen(body.pos.y, self.min_y, self.max_y, self.height)
        radius = body.radius * self.scaling

        self.body_shape_list[body_index].position = (pos_x, pos_y)
        self.body_shape_list[body_index].radius = radius

    def draw_trail(self, body_shape:pyglet.shapes.Circle, shape_index):
        #get index of oldest position
        oldest_index = (self.trail_index_list[shape_index] + 1) % (TRAIL_LENGTH)
        #connect last position to current body shape position
        self.trail_shape_list[shape_index][oldest_index].x = self.trail_shape_list[shape_index][self.trail_index_list[shape_index]].x2
        self.trail_shape_list[shape_index][oldest_index].y = self.trail_shape_list[shape_index][self.trail_index_list[shape_index]].y2
        self.trail_shape_list[shape_index][oldest_index].x2 = body_shape.x
        self.trail_shape_list[shape_index][oldest_index].y2 = body_shape.y

        #check if body position moved a delta away from the last trail index
        #ToDo: real distance calculation would be more accurate but this will do for now
        if ((math.fabs(body_shape.x - self.trail_shape_list[shape_index][self.trail_index_list[shape_index]].x2) >= TRAIL_DELTA * self.scaling) or
            (math.fabs(body_shape.y - self.trail_shape_list[shape_index][self.trail_index_list[shape_index]].y2) >= TRAIL_DELTA * self.scaling)):
            #oldest index is now the next index to be checked against
            self.trail_index_list[shape_index] = oldest_index

    def check_boundaries(self, x, y, r):
        if (((x + r >= 0) and (x - r <= self.width)) and
            ((y + r >= 0) and (y - r <= self.height))):
            return True
        return False

    def draw_log(self):
        log = self.data_logger.log(self.engine.simulation_time, self.drawing_time, self.engine.dt)
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

    def world_to_screen(self, world_coord, world_min, world_max, screen_size):
        return ((world_coord - world_min) / (world_max - world_min)) * screen_size

    def screen_to_world(self, screen_coord, world_min, world_max, screen_size):
        return ((screen_coord / screen_size) * (world_max - world_min) + world_min)
    
    def on_draw(self):
        self.window.clear()
        self.batch.draw()

    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        #shift simulation min and max according to scaled dx or dy
        dx_scaled = dx * ((self.max_x - self.min_x) / self.width)
        self.min_x = self.min_x - dx_scaled 
        self.max_x = self.max_x - dx_scaled
        dy_scaled = dy * ((self.max_y - self.min_y) / self.height)
        self.min_y = self.min_y - dy_scaled
        self.max_y = self.max_y - dy_scaled

        #redraw all shapes
        for body_shape in self.body_shape_list:
            body_shape.x += dx
            body_shape.y += dy
        for trail_list in self.trail_shape_list:
            for trail_shape in trail_list:
                trail_shape.x += dx
                trail_shape.y += dy
                trail_shape.x2 += dx
                trail_shape.y2 += dy


    def on_resize(self, new_width, new_height):
        #calculate change of window screen and accordingly change simulation sizes
        dx = self.width - new_width
        dx_scaled = dx * ((self.max_x - self.min_x) / self.width)
        #dont change min_x, only on the right new space is added
        self.max_x = self.max_x - dx_scaled
        dy = self.height - new_height
        dy_scaled = dy * ((self.max_y - self.min_y) / self.height)
        #dont change min_y, only on the top new space is added
        self.max_y = self.max_y - dy_scaled

        #udpate internal window size
        self.width = new_width
        self.height = new_height

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
        new_min_x = mouse_pos_x + ((self.min_x - mouse_pos_x) * scale_value)
        new_max_x = mouse_pos_x + ((self.max_x - mouse_pos_x) * scale_value)
        new_min_y = mouse_pos_y + ((self.min_y - mouse_pos_y) * scale_value)
        new_max_y = mouse_pos_y + ((self.max_y - mouse_pos_y) * scale_value)

        #redraw every shape
        for body_shape in self.body_shape_list:
            body_shape.x = self.world_to_screen(self.screen_to_world(body_shape.x, self.min_x, self.max_x, self.width), new_min_x, new_max_x, self.width)
            body_shape.y = self.world_to_screen(self.screen_to_world(body_shape.y, self.min_y, self.max_y, self.height), new_min_y, new_max_y, self.height)
            body_shape.radius = body_shape.radius / scale_value
        for trail_list in self.trail_shape_list:
            for trail_shape in trail_list:
                trail_shape.x = self.world_to_screen(self.screen_to_world(trail_shape.x, self.min_x, self.max_x, self.width), new_min_x, new_max_x, self.width)
                trail_shape.y = self.world_to_screen(self.screen_to_world(trail_shape.y, self.min_y, self.max_y, self.height), new_min_y, new_max_y, self.height)
                trail_shape.x2 = self.world_to_screen(self.screen_to_world(trail_shape.x2, self.min_x, self.max_x, self.width), new_min_x, new_max_x, self.width)
                trail_shape.y2 = self.world_to_screen(self.screen_to_world(trail_shape.y2, self.min_y, self.max_y, self.height), new_min_y, new_max_y, self.height)

        self.min_x = new_min_x
        self.max_x = new_max_x
        self.min_y = new_min_y
        self.max_y = new_max_y

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.SPACE:
            if self.events.running.is_set():
                self.events.running.clear()
            else:
                self.events.running.set()
            self.running = not self.running

        elif (symbol == pyglet.window.key.PLUS) or (symbol == pyglet.window.key.NUM_ADD):
            self.events.dt_increment.set()

        elif (symbol == pyglet.window.key.MINUS) or (symbol == pyglet.window.key.NUM_SUBTRACT):
            self.events.dt_decrement.set()

    def on_mouse_press(self, x, y, button, modifiers):
        pass
        #on mouse left click
        # if (button == 1):
        #    self.marked_body = self.find_body(x, y)
        #    self.marked_event.set()

    def find_body(self, x, y):
        for i, body in enumerate(self.engine.body_list):
            body_x = self.world_to_screen_x(body.pos.x, self.width, self.min_x, self.max_x)
            body_y = self.world_to_screen_y(body.pos.y, self.height, self.min_y, self.max_y)
            radius = body.radius * self.scaling
            if ((x >= body_x - radius) and (x <= body_x + radius) and
                (y >= body_y - radius) and (y <= body_y + radius)):
                return i
        return None

    def on_close(self):
        #notify other thread that this window is closed
        self.events.stop.set()
        self.stop()

    def stop(self):
        for body_shape in self.body_shape_list:
            body_shape.delete()
        for trail_list in self.trail_shape_list:
            for trail_shape in trail_list:
                trail_shape.delete()

        pyglet.app.exit()