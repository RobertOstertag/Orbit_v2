#for relative imports
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

import math
import pyglet
import threading
import time

import orbit.gravity_engine
from orbit.data_logging import DataLogger
from orbit.utils import Interface

#initial window size
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 800
WINDOW_POS_X = 550
WINDOW_POS_Y = 230
#initial simulation size factor
SIZE_FACTOR = 1.4
#scaling factor
SCALE_FACTOR = 1.1
#trail delta in pixels
TRAIL_DELTA = 10
TRAIL_LENGTH = 50

class World():
    def __init__(self, min_x, max_x, min_y, max_y, screen_width, screen_height, scaling):
        self.min_x = min_x
        self.max_x = max_x
        self.min_y = min_y
        self.max_y = max_y
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.scaling = scaling
    
    def fit(self, min_pos_x, max_pos_x, min_pos_y, max_pos_y):
        range = max(max(abs(max_pos_x), abs(min_pos_x)), max(abs(max_pos_y), abs(min_pos_y)))
        range = range * SIZE_FACTOR
        self.min_x = -range
        self.max_x = range
        self.min_y = -range
        self.max_y = range
        self.scaling = 1.0

    def world_to_screen(self, wx, wy):
        sx = ((wx - self.min_x) / (self.max_x - self.min_x)) * self.screen_width
        sy = ((wy - self.min_y) / (self.max_y - self.min_y)) * self.screen_height
        return (sx, sy)

    def screen_to_world(self, sx, sy):
        wx = ((sx / self.screen_width) * (self.max_x - self.min_x) + self.min_x)
        wy = ((sy / self.screen_height) * (self.max_y - self.min_y) + self.min_y)
        return (wx, wy)
    
    def resize(self, new_width, new_height):
        #calculate change of window screen and accordingly change simulation sizes
        sdx = self.screen_width - new_width
        wdx = (sdx / self.screen_width) * (self.max_x - self.min_x)
        self.max_x -= wdx
        #dont change min_x, only on the right new space is added
        sdy = self.screen_height - new_height
        wdy = (sdy / self.screen_height) * (self.max_y - self.min_y)
        self.max_y -= wdy
        #dont change min_y, only on the top new space is added
        #udpate internal window size
        self.screen_width = new_width
        self.screen_height = new_height

    def shift(self, sdx, sdy):
        wdx = (sdx / self.screen_width) * (self.max_x - self.min_x)
        self.min_x -= wdx 
        self.max_x -= wdx
        wdy = (sdy / self.screen_height) * (self.max_y - self.min_y)
        self.min_y -= wdy 
        self.max_y -= wdy
    
    def scale(self, scaling, sx, sy):
        #used for radius scaling
        self.scaling = self.scaling * scaling
        #transform position from window to screen frame
        wx, wy = self.screen_to_world(sx, sy)
        #update world size according to position
        self.min_x = wx + ((self.min_x - wx) / scaling)
        self.max_x = wx + ((self.max_x - wx) / scaling)
        self.min_y = wy + ((self.min_y - wy) / scaling)
        self.max_y = wy + ((self.max_y - wy) / scaling)

    def check_boundaries(self, x, y, r):
        if (((x + r >= 0) and (x - r <= self.screen_width)) and
            ((y + r >= 0) and (y - r <= self.screen_height))):
            return True
        return False
    

class BodyShapes():
    def __init__(self, world:World, wx, wy, radius, color, batch):
        self.world = world
        sx, sy = self.world.world_to_screen(wx, wy)
        self.radius = radius / self.world.scaling
        self.body = pyglet.shapes.Circle(sx, sy, radius=self.radius, color=color, batch=batch)
        self.trails = []
        for _ in range(TRAIL_LENGTH):
            self.trails.append(pyglet.shapes.Line(sx, sy, sx, sy, color=color, batch=batch))
        self.trail_index = 0

    def draw(self, wx, wy):
        sx, sy = self.world.world_to_screen(wx, wy)
        self.update_body(sx, sy)
        self.update_trail(sx, sy)

    def update_body(self, x, y):
        self.body.position = (x, y)
        self.body.radius = self.radius * self.world.scaling

    def update_trail(self, x, y):
        #connect current line shape position to current body shape position
        self.trails[self.trail_index].x2 = x
        self.trails[self.trail_index].y2 = y
        #check if body position moved a delta away from the last trail index
        #ToDo: real distance calculation would be more accurate but this will do for now
        if ((math.fabs(x - self.trails[self.trail_index].x) >= TRAIL_DELTA * self.world.scaling) or
            (math.fabs(y - self.trails[self.trail_index].y) >= TRAIL_DELTA * self.world.scaling)):
            #get index of next line to be drawn
            next_index = (self.trail_index + 1) % (TRAIL_LENGTH)
            #set start of next line to position of current body position
            self.trails[next_index].x = x
            self.trails[next_index].y = y
            self.trails[next_index].x2 = x
            self.trails[next_index].y2 = y
            #update index
            self.trail_index = next_index

    def shift(self, dx, dy):
        self.body.position = (self.body.x + dx, self.body.y + dy)
        for trail in self.trails:
            trail.x += dx
            trail.y += dy
            trail.x2 += dx
            trail.y2 += dy

    def scale(self, scaling, sx, sy):
        body_x_scale = sx + ((self.body.x - sx) * scaling)
        body_y_scale = sy + ((self.body.y - sy) * scaling)
        self.body.position = (body_x_scale, body_y_scale)
        self.body.radius = self.body.radius * scaling

        for trail in self.trails:
            trail.x = sx + ((trail.x - sx) * scaling)
            trail.y = sy + ((trail.y - sy) * scaling)
            trail.x2 = sx + ((trail.x2 - sx) * scaling)
            trail.y2 = sy + ((trail.y2 - sy) * scaling)

    def delete(self):
        self.body.delete()
        for trail_shape in self.trails:
            trail_shape.delete()

    
class SimulationWindow(threading.Thread):
    def __init__(self, trail_active, interface:Interface):
        super().__init__()
        self.trail_active = trail_active
        self.interface = interface

        self.bodies = None
        self.body_shapes = []
        self.world = World(-1, +1, -1, +1, WINDOW_WIDTH, WINDOW_HEIGHT, 1.0)
        self.drawing_time = 0
        self.marked_body_index = 0
        self.data_logger = DataLogger()

    def run(self):
        #Pyglet window setup
        self.window = pyglet.window.Window(width = WINDOW_WIDTH, height = WINDOW_HEIGHT, caption = "Orbit Simulation", resizable=True)
        self.batch = pyglet.graphics.Batch()
        self.keys = pyglet.window.key.KeyStateHandler()
        self.window.set_location(WINDOW_POS_X, WINDOW_POS_Y)
        #for registering events (on_draw, on_scroll, etc.)
        self.window.push_handlers(self)
        #schedule the update function to be called every x ms
        pyglet.clock.schedule_interval(self.update, orbit.gravity_engine.UPDATE_RATE)
        #run the pyglet app
        pyglet.app.run()

    def update(self, dt):
        #check if window needs to be closed
        if not self.interface.events.stop.is_set():
            #check if new body positions are available
            self.bodies = self.interface.bodies.receive()
            #check if shapes need to be deleted or added
            self.handle_commands()

            start_time = time.perf_counter()
            #update screen visuals
            if ((self.interface.events.running.is_set()) and
                (self.bodies != None)):
                #initialize all shapes and other necessary parts when requested
                self.initialize_if_needed(self.bodies)

                #draw all bodies and trails
                for index, shape in enumerate(self.body_shapes):
                    shape.draw(self.bodies[index].pos.x, self.bodies[index].pos.y)

            self.drawing_time = time.perf_counter() - start_time

            #write logging information on the screen
            self.draw_log()
        else:
            self.stop()

    def initialize_if_needed(self, bodies):
        if self.interface.events.initialize_window.is_set():
            #resize simulation size to show all initial positions of celestial bodies
            self.world_resize(bodies)

            for body_shape in self.body_shapes:
                body_shape.delete()
            self.body_shapes = []
            for body in bodies:
                self.body_shapes.append(BodyShapes(self.world, body.pos.x, body.pos.y, body.radius, body.color.get_rgb_8bit(), self.batch))

            #clear event
            self.interface.events.initialize_window.clear()

    def draw_log(self):
        log_string = self.data_logger.get_string(self.interface.engine_duration.receive(), self.drawing_time, self.interface.engine_timestep.receive())
        self.label = pyglet.text.Label(
                        log_string, font_name='Consolas', font_size=12,
                        x=10, y=self.world.screen_height-10, anchor_x='left', anchor_y='top',
                        batch=self.batch, multiline=True, width=350)

    def world_resize(self, bodies):
        min_pos_x, max_pos_x, min_pos_y, max_pos_y = 0.0, 0.0, 0.0, 0.0
        for body in bodies:
            if body.pos.x < min_pos_x:
                min_pos_x = body.pos.x
            if body.pos.x > max_pos_x:
                max_pos_x = body.pos.x
            if body.pos.y < min_pos_y:
                min_pos_y = body.pos.y
            if body.pos.y > max_pos_y:
                max_pos_y = body.pos.y
        self.world.fit(min_pos_x, max_pos_x, min_pos_y, max_pos_y)
    
    def on_draw(self):
        self.window.clear()
        self.batch.draw()

    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        #shift world according to dx and dy
        self.world.shift(dx, dy)
        #shift all shapes
        body_shape:BodyShapes
        for body_shape in self.body_shapes:
            body_shape.shift(dx, dy)

    def on_resize(self, new_width, new_height):
        self.world.resize(new_width, new_height)

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        #only scale when mouswheel is moved up or down
        if (scroll_y != 0):
            #1.1^-1 or 1.1^+1
            scaling = SCALE_FACTOR ** scroll_y
            self.world.scale(scaling, x, y)

            for body_shape in self.body_shapes:
                body_shape.scale(scaling, x, y)

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.SPACE:
            if self.interface.events.running.is_set():
                self.interface.events.running.clear()
            else:
                self.interface.events.running.set()

        elif (symbol == pyglet.window.key.PLUS) or (symbol == pyglet.window.key.NUM_ADD):
            self.interface.events.dt_increment.set()

        elif (symbol == pyglet.window.key.MINUS) or (symbol == pyglet.window.key.NUM_SUBTRACT):
            self.interface.events.dt_decrement.set()

    def on_mouse_press(self, x, y, button, modifiers):
        #on mouse left click
        if (button == 1):
            self.marked_body_index = self.find_body(x, y, self.body_shapes)
            self.interface.marked_body_index.send(self.marked_body_index)

    def find_body(self, x, y, body_shapes):
        for i, body in enumerate(body_shapes):
            if ((x >= body.body.x - body.body.radius) and (x <= body.body.x + body.body.radius) and
                (y >= body.body.y - body.body.radius) and (y <= body.body.y + body.body.radius)):
                return i
        #if no valid body is found, return current body
        return self.marked_body_index

    def handle_commands(self):
            #body shape needs to be deleted
            if self.interface.events.delete_shape.is_set():
                user_input = self.interface.user_input.receive()
                self.body_shapes.pop(user_input.index)
                self.interface.events.delete_shape.clear()
            #body shape needs to be added
            if self.interface.events.add_shape.is_set():
                user_input = self.interface.user_input.receive()
                new_body = self.bodies[-1]
                self.body_shapes.append(BodyShapes(self.world, new_body.pos.x, new_body.pos.y, new_body.radius, new_body.color.get_rgb_8bit(), self.batch))
                self.interface.events.add_shape.clear()
            #update body shape but only radius necessary
            if self.interface.events.update_shape.is_set():
                user_input = self.interface.user_input.receive()
                self.body_shapes[user_input.index].radius = self.bodies[user_input.index].radius / self.world.scaling
                self.body_shapes[user_input.index].draw(self.bodies[user_input.index].pos.x, self.bodies[user_input.index].pos.y)
                self.interface.events.update_shape.clear()
                
    def on_close(self):
        #notify other thread that this window is closed
        self.interface.events.stop.set()
        self.stop()

    def stop(self):
        for body_shape in self.body_shapes:
            body_shape.delete()
        pyglet.app.exit()