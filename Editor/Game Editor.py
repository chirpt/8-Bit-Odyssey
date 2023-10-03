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
            display.pg_display.blit(self.player.surface, WTS(self.player.world_position, display))
    class Editor():
    
        def __init__(self):
    
            self.toolbar_rect = pygame.Rect(950,0,50,500)
            self.toolbar_buttons = []
            self.active_block = "1"
            self.mouse_world_position = None
            self.background = pygame.image.load("editor_assets\\editor_background.bmp")
    
            with open("editor_assets\\toolbar_buttons.json","r") as tb_file:
                toolbar_buttons_dict = json.load(tb_file)
                toolbar_buttons_list = toolbar_buttons_dict.items()
    
            with open("game_data\\block_dict.json", "r") as block_dict_file:
                block_dict = json.load(block_dict_file)
    
            highest = 0
            reload = False
            for item in block_dict.items():
                item_found = False
                for button_item in toolbar_buttons_list:
                    button_name = button_item[0]
                    button_dict = button_item[1]
                    if button_name[:12] == "block_place_" and button_name[12] == item[0]:
                        item_found = True
                        if int(item[0]) > highest:
                            highest = int(item[0])
                if not item_found:
                    input("WARNING: missing buttons detected, autogenerating block_place buttons from game_data/block_dict.json -> \neditor_assets/"+block_dict[item[0]][:-4]+"_button.bmp dependancy created - modify files to satisfy then continue...")
                    toolbar_buttons_dict["block_place_"+item[0]] = {"rect":[952,highest*50+102,46,46],"image_filename":block_dict[item[0]][:-4]+"_button.bmp","start_shown":1,"t":0}
                    reload = True
    
            if reload:
                with open("editor_assets\\toolbar_buttons.json", "w") as tb_file:
                    json.dump(toolbar_buttons_dict, tb_file)
    
                with open("editor_assets\\toolbar_buttons.json", "r") as tb_file:
                    toolbar_buttons_dict = json.load(tb_file)
                    toolbar_buttons_list = toolbar_buttons_dict.items()
    
            for button_item in toolbar_buttons_list:
                button_name = button_item[0]
                button_dict = button_item[1]
                surface = pygame.image.load("editor_assets\\"+button_dict["image_filename"])
                self.toolbar_buttons.append(Button(button_name,button_dict["rect"],button_dict["image_filename"],button_dict["start_shown"],surface,button_dict["t"]))
            print("active buttons:",self.toolbar_buttons)
    
        def render(self,display,level):
            pygame.draw.rect(display.pg_display,[50,50,50],self.toolbar_rect,0)
            button_blit_sequence = [(button.pg_surface,(button.rect[0],button.rect[1])) for button in self.toolbar_buttons]
            display.pg_display.blits(button_blit_sequence)
            if display.grid:
                v_lines = [(WTS((i,-1),display),WTS((i,level.block_ID_grid.shape[0]),display)) for i in range(level.block_ID_grid.shape[1])]
                h_lines = [(WTS((0,i),display),WTS((level.block_ID_grid.shape[1],i),display)) for i in range(level.block_ID_grid.shape[0])]
                for line in v_lines:
                    pygame.draw.line(display.pg_display,[10,10,10],line[0],line[1])
                for line in h_lines:
                    pygame.draw.line(display.pg_display,[10,10,10],line[0],line[1])
    
    class Interactable():
    
        def __init__(self,name,filename,surface,world_position):
            self.name = name
            self.world_position = world_position
            self.surface = surface
            self.filename = filename
            self.original_surface = surface.copy()
    
        def get_dict_item(self):
            return (self.name,{"image_filename":self.filename,"world_position":self.world_position})
    class Button():
    
        def __init__(self,name,rect,image,start_shown,pg_surface,toggleable):
            self.name = name
            self.pressed_bool = False
            self.rect = pygame.Rect(rect)
            self.active = bool(start_shown)
            self.image_filename = image
            self.pg_surface = pg_surface
            self.t = bool(toggleable)
    
        def check_click(self,click_pos):
            # print("checking click:",click_pos,self.rect.topright,self.rect.bottomleft)
            if self.rect.bottomleft[0] < click_pos[0] and self.rect.bottomleft[1] > click_pos[1] and self.rect.topright[0] > click_pos[0] and self.rect.topright[1] < click_pos[1]:
                return True
            else:
                return False
    class Player():
    
        def __init__(self):
            self.world_position = None
            self.animation = None
            self.texture = None
            self.inventory = None
            self.surface = None
    class Background():
    
        def __init__(self):
            self.image = None
            self.surface = None
            self.world_position = None
    
    
    def main():
        level_name = "level_(default)"
        editor = Editor()
        display = Display()
        level = load_level(level_name,display)
        level, level_name = edit_level(editor,level,level_name,display)
        save_changes(level, level_name, level_name)
    def load_level(level_folder,display):
    
        level = Level()
    
        with open("game_data\\block_dict.json", "r") as block_dict_file:
            level.block_dict = json.load(block_dict_file)
        level.block_surface_dict = dict((item[0],pygame.image.load("game_data\\"+item[1])) for item in level.block_dict.items() if item[0] != "0")
        level.block_surface_dict_originals = level.block_surface_dict.copy()
        level.block_ID_grid = np.load("levels\\"+level_folder+"\\level_blocks_grid.npy")
        level.block_screen_positions = get_block_screen_positions(level.block_ID_grid.shape,display)
    
        with open("levels\\"+level_folder+"\\interactables_dict.json", "r") as interactables_file:
            interactables_items= json.load(interactables_file).items()
    
        for interactable_item in interactables_items:
            interactable_name = interactable_item[0]
            interactable_dict = interactable_item[1]
            surface = pygame.image.load("levels\\"+level_folder+"\\"+interactable_dict["image_filename"])
            level.interactables.append(Interactable(interactable_name,interactable_dict["image_filename"],surface,interactable_dict["world_position"]))
            level.interactables_screen_positions.append(WTS(interactable_dict["world_position"],display))
    
        level.background_surface = pygame.image.load("levels\\"+level_folder+"\\level_background.bmp")
        level.background_surface_original = level.background_surface.copy()
        level.background_world_position = [0, 17]
    
    
        player = Player()
    
        with open("levels\\"+level_folder+"\\player_info.json","r") as player_info_file:
            player_info = json.load(player_info_file)
        player.world_position = player_info["position"]
        player.animation = player_info["animation"]
        player.image_filename = player_info["image_filename"]
        player.inventory = player_info["inventory"]
        player.surface = pygame.image.load("levels\\"+level_folder+"\\"+player.image_filename)
    
        level.player = player
        print("LEVEL LOADED")
    
        return level
    def edit_level(editor, level, level_name, display):
        exit_editor = False
    
        while not exit_editor:
            pg_events = get_pg_events(editor)
            editor, level, level_name, display, exit_editor = process_editor_events(editor, level, pg_events, level_name, display)
            render(editor, level, display, level_name)
            display.pg_clock.tick(60)
    
        return level, level_name
    
    
    
    def get_pg_events(editor):
        exit_editor = False
        mouse_up = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit_editor = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_up = True
    
        return {"exit_editor":exit_editor,"keys_pressed":pygame.key.get_pressed(),"mouse_pos":pygame.mouse.get_pos(),"mouse_click":mouse_up,"mouse_pressed":pygame.mouse.get_pressed()}
    
    def process_editor_events(editor, level, pg_events, level_name, display):
        button_pressed = False
        screen_changed = False
        scale_changed = False
        editor.mouse_world_position = pg_events["mouse_pos"]
        if pg_events["mouse_click"]:
            for button in editor.toolbar_buttons:
                if button.active and button.check_click(pg_events["mouse_pos"]):
                    print("Button click")
                    editor, level, pg_events, level_name, display = act_on_button_press(button, editor, level, pg_events, level_name, display)
                    button_pressed = True
    
        if pg_events["keys_pressed"][pygame.K_UP]:
            display.offset[1] -= display.offset_increment
            screen_changed = True
        elif pg_events["keys_pressed"][pygame.K_DOWN]:
            display.offset[1] += display.offset_increment
            screen_changed = True
        if pg_events["keys_pressed"][pygame.K_RIGHT]:
            display.offset[0] -= display.offset_increment
            screen_changed = True
        elif pg_events["keys_pressed"][pygame.K_LEFT]:
            display.offset[0] += display.offset_increment
            screen_changed = True
    
        if pg_events["keys_pressed"][pygame.K_MINUS]:
            display.scale -= display.scale_increment
            screen_changed = True
            scale_changed = True
        elif pg_events["keys_pressed"][pygame.K_EQUALS]:
            display.scale += display.scale_increment
            screen_changed = True
            scale_changed = True
    
        if screen_changed:
            level.block_screen_positions = get_block_screen_positions(level.block_ID_grid.shape,display)
            level.interactables_screen_positions = get_interactables_screen_positions(level.interactables,display)
            if scale_changed:
                level, display = resize_all(level, display)
    
    
        if not button_pressed:
            if pg_events["mouse_pressed"][0]:
                mouse_world_position = STW(pg_events["mouse_pos"],display)
                level, editor = edit_block(mouse_world_position, level, editor)
    
    
    
        return editor, level, level_name, display, pg_events["exit_editor"]
    
    def act_on_button_press(button, editor, level, pg_events, level_name, display):
    
        if button.name == "toggle_grid":
            if display.grid:
                display.grid = False
            else:
                display.grid = True
    
        else:
            if button.t:
                if button.pressed_bool:
                    button.pressed_bool = False
    
                else:
                    button.pressed_bool = True
            else:
    
                if button.name == "save_as":
                    new_level_name = input("Enter level folder name (default level_x ascending)\n==>: ")
                    save_changes(level,level_name,new_level_name)
                    level = load_level(new_level_name,display)
                    level_name = new_level_name
    
                elif button.name == "load":
                    while True:
                        print("Enter level folder name - (default level_x ascending) - Existing:")
                        for name in os.listdir("."):
                            if os.path.isdir(name):
                                if name[0:5] == "level":
                                    print("\""+name+"\"")
                        try:
                            level_name = input("\n==>: ")
                            level = load_level(level_name,display)
                            break
                        except Exception as e:
                            print("\""+str(level_name)+"\" could not be loaded successfully. Check folder format is compatible.")
                            raise e
    
        if pg_events["mouse_pressed"][0]:
            if button.name[0:11] == "block_place":
                editor.active_block = button.name[12]
    
        return editor, level, pg_events, level_name, display
    
    
    def render(editor, level, display, level_name):
        display.pg_display.blit(editor.background, (0, 0))
        level.render(display)
        editor.render(display,level)
        pygame.display.update()
    def save_changes(level,level_folder,new_level_name):
    
        if not os.path.exists(new_level_name):
            os.makedirs(new_level_name)
            for item in os.listdir("levels\\"+level_folder):
                shutil.copy("levels\\"+level_folder+"\\"+item,os.getcwd()+"\\"+new_level_name)
                print("copied:","levels\\"+level_folder+"\\"+item,"to:",os.getcwd()+new_level_name)
    
        with open(new_level_name+"\\block_dict.json", "w") as block_dict_file:
            json.dump(level.block_dict,block_dict_file)
    
        np.save(new_level_name+"\\level_blocks_grid.npy", level.block_ID_grid)
        interactables_dict = dict([interactable.get_dict_item() for interactable in level.interactables])
        with open(new_level_name+"\\interactables_dict.json", "w") as interactables_dict_file:
            json.dump(interactables_dict, interactables_dict_file)
    
        print("LEVEL SAVED")
    
    
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
    
    def sample_level_save():
        sample_grid = np.zeros((17,34),dtype=np.uint8)
        sample_grid[:8,:] = 1
        sample_grid[8:13,23] = 2
        np.save("level_(default)"+"\\level_blocks_grid.npy", sample_grid)
    
    
    # sample_level_save()
    main()
