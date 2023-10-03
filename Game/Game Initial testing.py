import pygame
import numpy as np
import json
import os
import shutil

class Display():

    def __init__(self):

        pygame.init()
        self.display_size = (1000, 500)
        self.pg_display = pygame.display.set_mode(self.display_size)
        self.offset = [0,0]
        self.offset_increment = 1
        self.init_scale = 30
        self.scale = 30
        self.grid = True
        self.pg_clock = pygame.time.Clock()
        self.scale_increment = 0.3
        self.zoom_world_centre_offset = [17,8.5]
class Level():

    def __init__(self):
        self.block_dict = None
        self.block_ID_grid = None
        self.block_surface_dict = None
        self.block_surface_dict_originals = None
        self.block_screen_positions = None

        self.interactables = []
        self.interactables_screen_positions = []
        self.player = None
        self.background_surface = None
        self.background_surface_original = None
        self.background_world_position = None

    def render(self,display):
        display.pg_display.blit(self.background_surface ,WTS(self.background_world_position, display))

        block_grid_blit_sequence = [(self.block_surface_dict[str(self.block_ID_grid.flatten()[i])],self.block_screen_positions[i]) for i in range(len(self.block_ID_grid.flatten())) if self.block_ID_grid.flatten()[i] != 0]
        display.pg_display.blits(block_grid_blit_sequence)

        interactables_blit_sequence = [(interactable.surface,self.interactables_screen_positions[i]) for i, interactable in enumerate(self.interactables)]
        display.pg_display.blits(interactables_blit_sequence)
        display.pg_display.blit(self.player.surface, WTS((self.player.world_position[0],self.player.world_position[1] + self.player.hitbox[1] - 1), display))
class Interactable():

    def __init__(self,name,filename,surface,world_position):
        self.name = name
        self.world_position = world_position
        self.surface = surface
        self.filename = filename
        self.original_surface = surface.copy()

    def get_dict_item(self):
        return (self.name,{"image_filename":self.filename,"world_position":self.world_position})
class Player():

    def __init__(self):
        self.world_position = None
        self.animation = None
        self.texture = None
        self.inventory = None
        self.surface = None
        self.world_velocity = None
        self.max_world_velocity = None
        self.hitbox = None
        self.acceleration = None
        self.drag = [12 / 60, 4/60]
        self.gravity = 2 / 60
class Background():

    def __init__(self):
        self.image = None
        self.surface = None
        self.world_position = None

class Heads_Up_Display():

    def __init__(self):
        self.buttons = None
        self.background = pygame.image.load("editor_assets\\editor_background.bmp")

    def render(self,display,level):
        pass

def main():
    quit_game = False
    level_folder_name = "level_1"
    display = Display()

    while not quit_game:
        level = load_level(level_folder_name,display)
        level, level_folder_name, display = run_level(level, level_folder_name, display)

def run_level(level, level_folder_name, display):
    quit_level = False
    HUD = Heads_Up_Display()

    while not quit_level:
        pg_events = get_pg_events()
        level, level_folder_name, display, HUD = process_game_events(pg_events, level, level_folder_name, display, HUD)
        render(HUD,level,display,level_folder_name)
        display.pg_clock.tick(60)


    return level, level_folder_name, display

def process_game_events(pg_events, level, level_folder_name, display, HUD):

    user_acceleration = False
    if pg_events["keys_pressed"][pygame.K_d]:
        if level.player.max_world_velocity[0] > abs(level.player.world_velocity[0] + level.player.acceleration):
            level.player.world_velocity[0] += level.player.acceleration
        user_acceleration = True
    if pg_events["keys_pressed"][pygame.K_a]:
        if level.player.max_world_velocity[0] > abs(level.player.world_velocity[0] - level.player.acceleration):
            level.player.world_velocity[0] -= level.player.acceleration
        user_acceleration = True
    if pg_events["keys_down"]["SPACE"]:
        level.player.world_velocity[1] = 2 / 60

    # level.player.world_velocity[1] -= level.player.gravity

    if not user_acceleration:
        level.player.world_velocity[0] -= np.sign(level.player.world_velocity[0]) * level.player.drag[0] * abs(level.player.world_velocity[0])
    level.player.world_velocity[1] -= np.sign(level.player.world_velocity[1]) * level.player.drag[1] * abs(level.player.world_velocity[1])

    level.player.world_position[0] += level.player.world_velocity[0]
    level.player.world_position[1] += level.player.world_velocity[1]

    # level = apply_collision(level)
    level = apply_collision_GPT(level)

    # print(level.player.world_velocity)

    return level, level_folder_name, display, HUD

def apply_collision(level):
    # works on the assumption that the player is less than 1 block wide and less than 2 blocks tall

    pos = level.player.world_position
    hitbox = level.player.hitbox
    world_limits = level.block_ID_grid.shape
    restore = [0, 0]
    print("---------------------------\nplayer pos:", pos,"hitbox extent:",(pos[0]+hitbox[0],pos[1]-hitbox[1]))

    for x in range(int(pos[0]),int(pos[0])+2):
        for y in range(int(pos[1]),int(pos[1])+3):
            print("AT:", (x, y))
            if x >= 0 and x < world_limits[1] and y >=0 and y < world_limits[0]:
                if level.block_ID_grid[y, x] != 0:
                    print("CHECKING", (x, y))

                    if (pos[0] + hitbox[0]) > x:
                        print("valid horizontal check")

                        if int(pos[1]) == y:
                            restore[1] = (y+1) - pos[1]
                            print("restore up")

                        elif int(pos[1] + hitbox[1]) == y:
                            restore[1] = y - (pos[1] + hitbox[1])
                            print("restore down")

                    if (pos[1] + hitbox[1]) > y:
                        print("valid vertical check")

                        if int(pos[0]) == x:
                            restore[0] = (x+1) - pos[0]
                            print("restore right")

                        elif (pos[0] + hitbox[0]) > x:
                            restore[0] = x - pos[0]
                            print("restore left")



    level.player.world_position[0] += restore[0]
    level.player.world_position[1] += restore[1]

    return level

def apply_collision_GPT(level):
    world = level.block_ID_grid.transpose()
    player_x, player_y = level.player.world_position
    player_width, player_height = level.player.hitbox

    # Calculate the bottom left and top right corners of the player's hitbox
    player_left = player_x
    player_right = player_x + player_width
    player_bottom = player_y
    player_top = player_y + player_height

    # Initialize the offset to restore player's position
    offset_x = 0.0
    offset_y = 0.0

    # Iterate through the blocks within the player's hitbox
    for i in range(int(player_left), int(player_right) + 1):
        for j in range(int(player_bottom), int(player_top) + 1):
            # Check if the current block is within the world bounds
            if i < 0 or i >= len(world) or j < 0 or j >= len(world[0]):
                # Collision with world bounds, update offset_x and offset_y
                if i < 0:
                    offset_x = max(offset_x, abs(i) - player_left)
                elif i >= len(world):
                    offset_x = min(offset_x, len(world) - i - (player_right - player_x))
                if j < 0:
                    offset_y = max(offset_y, abs(j) - player_bottom)
                elif j >= len(world[0]):
                    offset_y = min(offset_y, len(world[0]) - j - (player_top - player_y))
                continue

            # Check if the current block is not empty (collision with a block)
            if world[i][j] != 0:
                # Collision with a block, update offset_x and offset_y
                if i < player_x:
                    offset_x = max(offset_x, abs(i + 1) - player_left)
                elif i >= player_x + player_width:
                    offset_x = min(offset_x, i - (player_right - player_x + 1))
                if j < player_y:
                    offset_y = max(offset_y, abs(j + 1) - player_bottom)
                elif j >= player_y + player_height:
                    offset_y = min(offset_y, j - (player_top - player_y + 1))

    level.player.world_position[0] += offset_x
    level.player.world_position[1] += offset_y

    return level


def load_level(level_folder,display):

    level = Level()

    with open("game_data\\block_dict.json", "r") as block_dict_file:
        level.block_dict = json.load(block_dict_file)
    level.block_surface_dict = dict((item[0],pygame.image.load("game_data\\"+item[1])) for item in level.block_dict.items() if item[0] != "0")
    level.block_surface_dict_originals = level.block_surface_dict.copy()
    level.block_ID_grid = np.load(level_folder+"\\level_blocks_grid.npy")
    level.block_screen_positions = get_block_screen_positions(level.block_ID_grid.shape,display)

    with open(level_folder+"\\interactables_dict.json", "r") as interactables_file:
        interactables_items= json.load(interactables_file).items()

    for interactable_item in interactables_items:
        interactable_name = interactable_item[0]
        interactable_dict = interactable_item[1]
        surface = pygame.image.load(level_folder+"\\"+interactable_dict["image_filename"])
        level.interactables.append(Interactable(interactable_name,interactable_dict["image_filename"],surface,interactable_dict["world_position"]))
        level.interactables_screen_positions.append(WTS(interactable_dict["world_position"],display))

    level.background_surface = pygame.image.load(level_folder+"\\level_background.bmp")
    level.background_surface_original = level.background_surface.copy()
    level.background_world_position = [0, 17]


    player = Player()

    with open(level_folder+"\\player_info.json","r") as player_info_file:
        player_info = json.load(player_info_file)
    player.world_position = player_info["position"]
    player.animation = player_info["animation"]
    player.image_filename = player_info["image_filename"]
    player.inventory = player_info["inventory"]
    player.surface = pygame.image.load(level_folder+"\\"+player.image_filename)
    player.hitbox = player_info["hitbox"]
    player.world_velocity = player_info["velocity"]
    player.acceleration = player_info["acceleration"]
    player.max_world_velocity = player_info["max_velocity"]

    level.player = player
    print("LEVEL LOADED")

    return level
def render(HUD, level, display, level_name):
    display.pg_display.blit(HUD.background, (0, 0))
    level.render(display)
    HUD.render(display,level)
    pygame.display.update()

def get_pg_events():
    exit_editor = False
    mouse_up = False
    keys_down = {"SPACE":False}


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit_editor = True
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_up = True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                keys_down["SPACE"] = True

    return {"exit_editor":exit_editor,"keys_pressed":pygame.key.get_pressed(),"mouse_pos":pygame.mouse.get_pos(),"mouse_click":mouse_up,"mouse_pressed":pygame.mouse.get_pressed(),"keys_down":keys_down}


def STW(screen_position,display):
    x1 = screen_position[0]
    y1 = display.display_size[1] - screen_position[1]
    x2 = x1 / display.scale
    y2 = y1/ display.scale
    x3 = x2 + display.offset[0]
    y3 = y2 + display.offset[1]

    world_position = [x2, y2]
    return world_position
def WTS(world_position,display):
    x5 = world_position[0] + display.offset[0]
    y5 = world_position[1] + display.offset[1]
    x4 = x5
    y4 = y5
    x3 = x4 * display.scale
    y3 = y4 * display.scale
    x2 = x3
    y2 = y3
    x1 = x2
    y1 = display.display_size[1] - y2 - display.scale
    screen_position = [x1, y1]
    return screen_position
def get_block_screen_positions(dimensions,display):
    return [WTS([x,y],display) for y in range(dimensions[0]) for x in range(dimensions[1])]
def get_interactables_screen_positions(interactables,display):
    return [WTS(interactable.world_position, display) for interactable in interactables]
def edit_block(mouse_world_position,level,editor):
    if mouse_world_position[0] < level.block_ID_grid.shape[1] and mouse_world_position[1] < level.block_ID_grid.shape[0]:
        int_location = (int(mouse_world_position[1]), int(mouse_world_position[0]))
        # print("ID of old block:",level.block_ID_grid[int_location])
        if not level.block_ID_grid[int_location] == editor.active_block:
            level.block_ID_grid[int_location] = editor.active_block
            # print("ID of new block:",level.block_ID_grid[int_location])

    return level, editor
def resize_all(level,display):
    for item in level.block_surface_dict.items():
        level.block_surface_dict[item[0]] = pygame.transform.scale(level.block_surface_dict_originals[item[0]],(display.scale+1,display.scale+1))

    for i in range(len(level.interactables)):
        level.interactables[i].surface = pygame.transform.scale(level.interactables[i].original_surface,(display.scale+1,display.scale+1))

    background_size = [((level.background_surface_original.get_size()[i] * display.scale) /(display.init_scale)) for i in range(2)]
    level.background_surface = pygame.transform.scale(level.background_surface_original, background_size)

    return level, display

main()
