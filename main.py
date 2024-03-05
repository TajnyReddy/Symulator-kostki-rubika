from ursina import *
from itertools import product
import time
import random

class RubiksCube(Entity):
    def __init__(self):
        super().__init__()
        self.last_click_time = time.time()
        self.moves_history = []
        self.moves_to_show = []
        self.enable_input = True
        self.current_time = time.time()
        Entity(model='sphere', scale=100, texture='brick', color=color.rgb_to_hex(70, 236, 200), double_sided=True)
        self.cubes = []
        for pos in product((-1, 0, 1), repeat=3):
            self.cubes.append(Entity(model='custom_cube', texture='rubik_texture', position=pos, scale=1))

        self.rotations = {'u': ['y', 1, 90], 'e': ['y', 0, -90], 'd': ['y', -1, -90],
                          'l': ['x', -1, -90], 'm': ['x', 0, -90], 'r': ['x', 1, 90],
                          'f': ['z', -1, 90], 's': ['z', 0, -90], 'b': ['z', 1, -90]}

        self.center = Entity()
        self.show_process_button = Button(text='Show process', color=color.gray, position=(.7, -.2),
                                          on_click=self.show_process)
        self.show_process_button.fit_to_text()
        self.reverse_last_move_button = Button(text='Reverse last move', color=color.gray, position=(.7, -.3),
                                               on_click=self.reverse_last_move_click)
        self.reverse_last_move_button.fit_to_text()
        self.randomize_button = Button(text='Randomize', color=color.gray, position=(.7, -.4), on_click=self.randomize)
        self.randomize_button.fit_to_text()
        self.instructions = Text(text='The basic moves are U - Up, D - Down, R - Right, '
                                      'L - Left, F - Front, B - Back. Holding shift changes the angle',
                                 position=(-.84, .45), background=True, background_color=(0, 0, 0, 0.8), enable=True)

        self.input = self.handle_input

    def follow_center(self, axis, layer):
        for cube in self.cubes:
            cube.position, cube.rotation = round(cube.world_position, 1), cube.world_rotation
            cube.parent = scene

        self.center.rotation = 0

        for cube in self.cubes:
            if getattr(cube.position, axis) == layer:
                cube.parent = self.center

    def perform_rotation(self, key):
        axis, layer, angle = self.rotations[key]
        self.follow_center(axis, layer)
        shift = held_keys['shift']
        rotation_method = getattr(self.center, f"animate_rotation_{axis}")
        rotation_angle = -angle if shift else angle
        rotation_method(rotation_angle, duration=0.5)

    def handle_input(self, key):
        self.current_time = time.time()
        if self.current_time - self.last_click_time >= 0.6:
            if key not in self.rotations or held_keys['right mouse'] or not self.enable_input:
                return
            self.perform_rotation(key)
            self.last_click_time = time.time()
            if held_keys['shift']:
                self.moves_history.append(key+'shift')
                self.moves_to_show.append(key + 'shift')
            else:
                self.moves_history.append(key)
                self.moves_to_show.append(key)
        else:
            return

    def randomize(self):
        possible_moves = list(self.rotations.keys())
        n = random.randint(5, 25)
        self.disable_button(n*0.6)
        moves = random.choices(possible_moves, k=n)
        self.animate_moves(moves)

    def animate_moves(self, moves):
        shift = 'shift'
        if len(moves) > 0:
            if shift in moves[0]:
                key = moves[0][:1]
                moves.pop(0)
                axis, layer, angle = self.rotations[key]
                self.follow_center(axis, layer)
                rotation_method = getattr(self.center, f"animate_rotation_{axis}")
                rotation_angle = -angle
                rotation_method(rotation_angle, duration=0.2)
                invoke(lambda: self.animate_moves(moves), delay=0.6)
            else:
                key = moves.pop(0)
                axis, layer, angle = self.rotations[key]
                self.follow_center(axis, layer)
                rotation_method = getattr(self.center, f"animate_rotation_{axis}")
                rotation_angle = angle
                rotation_method(rotation_angle, duration=0.2)
                invoke(lambda: self.animate_moves(moves), delay=0.6)

    def show_process(self):
        self.reverse_all_moves()
        n = len(self.moves_to_show)
        print(n)
        if len(self.moves_to_show) > 0:
            invoke(lambda: self.animate_moves(self.moves_to_show), delay=(n+1)*0.6)

    def reverse_all_moves(self):
        if len(self.moves_history) > 0:
            self.reverse_last_move(0.005)
            invoke(lambda: self.reverse_all_moves(), delay=0.01)

    def reverse_last_move_click(self):
        self.reverse_last_move(0.5)

    def reverse_last_move(self, dur):
        self.current_time = time.time()
        shift = 'shift'
        if self.current_time - self.last_click_time >= 0.6:
            if len(self.moves_history) > 0:
                if shift in self.moves_history[-1]:
                    last_move = self.moves_history[-1][:1]
                    self.moves_history.pop(-1)
                    axis, layer, angle = self.rotations[last_move]
                    self.follow_center(axis, layer)
                    rotation_method = getattr(self.center, f"animate_rotation_{axis}")
                    rotation_angle = angle
                    rotation_method(rotation_angle, duration=dur)
                    self.last_click_time = time.time()
                else:
                    last_move = self.moves_history[-1]
                    self.moves_history.pop(-1)
                    axis, layer, angle = self.rotations[last_move]
                    self.follow_center(axis, layer)
                    rotation_method = getattr(self.center, f"animate_rotation_{axis}")
                    rotation_angle = -angle
                    rotation_method(rotation_angle, duration=dur)
                    self.last_click_time = time.time()
            else:
                return
        else:
            return

    def disable_button(self, x):
        self.enable_input = False
        self.randomize_button.disable()
        invoke(self.enable_button, delay=x)

    def enable_button(self):
        self.randomize_button.enable()
        self.enable_input = True


if __name__ == '__main__':
    app = Ursina()
    window.fullscreen = True
    RubiksCube()
    EditorCamera()
    app.run()
