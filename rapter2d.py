"""
# Rapter2D Game Engine
We have an API, maybe
"""
from lupa.lua54 import LuaRuntime
from colorama import Fore as F
from pygame.locals import *
from typing import Any
import importlib.util
import threading
import traceback
import datetime
import pygame
import json
import time
import sys
import os


pygame.font.init()
pygame.mixer.init()


# Some preset stuff
PRESET_RESOLUTION: tuple[int, int] = (1280, 720)
RAPTER2D_TITLE: str = "Rapter2D"
TILE_SIZE: int = 32
TAB_SIZE: int = 4
NAMESPACE: str = "Rapter2D"


class Logger:
    def log(text: str) -> None:
        string: str = F.BLACK + "[" + F.BLUE + NAMESPACE + F.BLACK + "][" + F.GREEN + "Info" + F.BLACK + "]" + F.CYAN + " > " + F.WHITE + text + F.RESET
        print(string)
    
    def warn(text: str) -> None:
        string: str = F.BLACK + "[" + F.BLUE + NAMESPACE + F.BLACK + "][" + F.YELLOW + "Warning" + F.BLACK + "]" + F.CYAN + " > " + F.WHITE + text + F.RESET
        print(string)
    
    def error(text: str) -> None:
        string: str = F.BLACK + "[" + F.BLUE + NAMESPACE + F.BLACK + "][" + F.RED + "Error" + F.BLACK + "]" + F.CYAN + " > " + F.WHITE + text + F.RESET
        print(string)


class Object:
    """ The base object for all objects use this as a parent `class YourClass(Object):` objects like this are auto recognized by the program """
    
    def __init__(self) -> None:
        """ The base info for your object these are required and should be altered if needed """
        self.size_x: int = 32
        self.size_y: int = 32
        self.x: int = 0
        self.y: int = 0
        self.image_id: str | None = None

    
    def handleInput(self, event: pygame.event.Event) -> None:
        """ Handles input provided by the program, You can also use `pygame.event.get(<the_event_you_want_to_listen_for>)` instead within the main loop if you only need a specific event """
        return None

    
    def render(self, screen: pygame.Surface, main_assets: list[dict] = []) -> bool:
        """ Renders the object, default render code is already included (remember to include `screen`, `main_assets` in that order) """
        try:
            if self.image_id is not None:
                for asset in main_assets:
                    if asset.get("id") == self.image_id:
                        screen.blit(asset.get("image"))
                        return True
                return False
            else:
                return False
        except Exception as msg:
            print(f"[Rapter2D][Object][Render][Error] Unable to render object: {msg}")
            return False

    
    def getX(self) -> int:
        """ Gets location X """
        return self.x


    def gety(self) -> int:
        """ Gets location Y """
        return self.y
    

    def setX(self, x: int) -> None:
        """ Sets location X """
        self.x = x
    

    def setY(self, y: int) -> None:
        """ Sets location Y """
        self.y = y
    

    def setImageId(self, asset_id: str | None) -> None:
        """ Set the Id of the Image to be rendered with the `render()` function later, setting it to none will remove all rendering """
        self.image_id = asset_id
    

    def getImageId(self) -> str | None:
        """ Gets the current image id """
        return self.image_id



class Text:
    def __init__(self, text: str, x: int, y: int, *, FontType: str | None = None, FontSize: int = 16, colour: tuple[int, int, int] | pygame.Color | list[int] = (255, 255, 255)) -> None:
        self.text = text
        self.x = x
        self.y = y
        self.font = pygame.font.Font(FontType, FontSize)
        self.colour = colour
    

    def render(self, screen: pygame.Surface) -> bool:
        try:
            text_render = self.font.render(self.text, True, self.colour)
            screen.blit(text_render, (self.x, self.y))
            return True
        except Exception as msg:
            print(f"[Rapter2D][Text][Render][Error] Unable to render Text: {msg}")
            return False
    

    def setX(self, x: int) -> None:
        self.x = x


    def setY(self, y: int) -> None:
        self.y = y


    def getX(self) -> int:
        return self.x


    def getY(self) -> int:
        return self.y


    def setText(self, text: str) -> None:
        self.text = text


    def getText(self) -> str:
        return self.text



class Button():
    STATE_IDLE = 'idle'
    STATE_ARMED = 'armed'
    STATE_DISARMED = 'disarmed'


    def __init__(self, window, loc, up, down):
        self.window = window
        self.loc = loc
        self.surfaceUp = up
        self.surfaceDown = down

        self.rect = self.surfaceUp.get_rect()
        self.rect[0] = loc[0]
        self.rect[1] = loc[1]

        self.state = Button.STATE_IDLE
    

    def getUpImage(self): return self.surfaceUp


    def getDownImage(self): return self.surfaceDown
    

    def setUpImage(self, up): self.surfaceUp = up


    def setDownImage(self, down): self.surfaceDown = down
    

    def handleEvent(self, eventObj):
        if eventObj.type not in (MOUSEMOTION, MOUSEBUTTONUP, MOUSEBUTTONDOWN):
            return False
        
        eventPointInButtonRect = self.rect.collidepoint(eventObj.pos)

        if self.state == Button.STATE_IDLE:
            if (eventObj.type == MOUSEBUTTONDOWN) and eventPointInButtonRect:
                self.state = Button.STATE_ARMED
            
        elif self.state == Button.STATE_ARMED:
            if (eventObj.type == MOUSEBUTTONUP) and eventPointInButtonRect:
                self.state = Button.STATE_IDLE
                return True

            if (eventObj.type == MOUSEMOTION) and (not eventPointInButtonRect):
                self.state = Button.STATE_DISARMED

        elif self.state == Button.STATE_DISARMED:
            if eventPointInButtonRect:
                self.state = Button.STATE_ARMED
            elif eventObj.type == MOUSEBUTTONUP:
                self.state = Button.STATE_IDLE

        return False
    

    def draw(self):
        if self.state == Button.STATE_ARMED:
            self.window.blit(self.surfaceDown, self.loc)
        else:
            self.window.blit(self.surfaceUp, self.loc)



class CooldownTimer:
    def __init__(self, cooldown_seconds):
        self.cooldown = cooldown_seconds
        self.last_used = 0

    def is_ready(self):
        return time.time() - self.last_used >= self.cooldown

    def trigger(self):
        if self.is_ready():
            self.last_used = time.time()
            return True
        return False


class LoggerManager:
    def __init__(self, logging_folder: str = "./logs/") -> None:
        self.logging_folder = logging_folder
        self.log_time: str = self.get_datetime()
        self.selected_path: str | None = None
    
    def get_datetime(self) -> str:
        return datetime.datetime.now().strftime("%d_%m_%Y")
    
    def init(self) -> None:
        if self.selected_path is not None:
            with open(self.selected_path, "w") as f:
                f.write(f"[{NAMESPACE}] > new log \"{self.logging_folder}{self.log_time}.log\", we are ready to log!")
        else:
            self.re_init()
    
    def re_init(self) -> None:
        self.log_time = self.get_datetime()
        suggested_path: str = f"{self.logging_folder}{self.log_time}"
        self.selected_path = suggested_path
        if os.path.exists(f"{self.logging_folder}{self.log_time}"):
            index: int = 1
            max_depth: int = 1000 # No more than 1,000 logs can be created per day
            depth: int = 1
            while (depth <= max_depth):
                suggested_path: str = f"{self.logging_folder}{self.log_time}_{index}"
                if not os.path.exists(suggested_path):
                    self.selected_path = suggested_path
                    break
                else:
                    index += 1
                depth += 1
            else:
                self.init()
        else:
            self.init()
        
    
    def log(self, text: str) -> bool:
        if not os.path.exists(self.selected_path):
            self.re_init()
            return False
        else:
            dt = datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
            with open(self.selected_path, "a") as f:
                f.write(f"[{NAMESPACE}][{dt}] {text}")
            return True


class Rapter2D:
    """
    # Rapter2D Game Engine
    Just some lousy game engine
    """
    
    def __init__(self) -> None:
        self.running: bool = True
        self.window: pygame.Surface = pygame.display.set_mode(PRESET_RESOLUTION, pygame.DOUBLEBUF)
        pygame.display.set_caption(RAPTER2D_TITLE)
        self.objects: list[Object | Text | CooldownTimer] = []
        self.show_wireframe: bool = False
        self.show_image: bool = True
        self.image_editor: bool = False
        self.assets_folder: str = f'{os.getenv("APPDATA")}/Rapter2D/assets/'
        self.scripts_folder: str = f'{os.getenv("APPDATA")}/Rapter2D/scripts/'
        if not os.path.exists(self.assets_folder): os.makedirs(self.assets_folder)
        if not os.path.exists(self.scripts_folder): os.makedirs(self.scripts_folder)
        self.assets: list[dict] = [
            {
                "id": "missing_texture",
                "image": pygame.image.load(f"{self.assets_folder}missing_texture.png"),
                "color": (4, 4, 4)
            }
        ]        
        self.separator_1: int = PRESET_RESOLUTION[0] // 2
        self.separator_2: int = PRESET_RESOLUTION[1] // 2
        self.game_window: pygame.Surface = pygame.Surface((PRESET_RESOLUTION[0] // 2, PRESET_RESOLUTION[1] // 2))
        self.script_window: pygame.Surface = pygame.Surface((PRESET_RESOLUTION[0] // 2, PRESET_RESOLUTION[1]))
        self.asset_window = pygame.Surface((self.separator_1, PRESET_RESOLUTION[1] - self.separator_2))
        self.line_text: str = ""
        self.lines: list[str] = []
        self.selected_line: int = len(self.lines)
        self.font: pygame.font.Font = pygame.font.Font(None, 28)
        self.selected_module: Any | None = None
        self.cursor_pos: int = 0
        self.auto_save_1_assets = (pygame.image.load(f"{self.assets_folder}auto_save_button_up.png"), pygame.image.load(f"{self.assets_folder}auto_save_button_down.png"))
        self.auto_save_2_assets = (pygame.image.load(f"{self.assets_folder}auto_save_2_button_up.png"), pygame.image.load(f"{self.assets_folder}auto_save_2_button_down.png"))
        self.save_button:      Button = Button(self.window, (PRESET_RESOLUTION[0] - 80,  PRESET_RESOLUTION[1] - 45), pygame.image.load(f"{self.assets_folder}save_button_up.png"), pygame.image.load(f"{self.assets_folder}save_button_down.png"))
        self.run_button:       Button = Button(self.window, (PRESET_RESOLUTION[0] - 150, PRESET_RESOLUTION[1] - 45), pygame.image.load(f"{self.assets_folder}run_button_up.png"),  pygame.image.load(f"{self.assets_folder}run_button_down.png"))
        self.load_button:      Button = Button(self.window, (PRESET_RESOLUTION[0] - 220, PRESET_RESOLUTION[1] - 45), pygame.image.load(f"{self.assets_folder}load_button_up.png"), pygame.image.load(f"{self.assets_folder}load_button_down.png"))
        self.auto_save_button = Button(self.window, (0, PRESET_RESOLUTION[1] - 45), self.auto_save_1_assets[0], self.auto_save_1_assets[1])
        self.reload_button    = Button(self.window, (0, PRESET_RESOLUTION[1] - 45), pygame.image.load(f"{self.assets_folder}/reload_button_up.png"), pygame.image.load(f"{self.assets_folder}/reload_button_down.png"))

        self.lua: LuaRuntime = LuaRuntime(max_memory=1024 * 64)
        self.error_code: int | None = None
        self.error_column: int | None = None
        self.selected_script: str = ""
        self.scroll_offset = 0
        self.line_height = 28
        self.enabled_auto_save: bool = True
        self.dragging_separator_1 = False
        self.dragging_separator_2 = False
        pygame.mouse.set_visible(False)


    def getErrorLineNum(self, filepath: str, e: Exception) -> tuple[int, int | None]:
        """ Grabs the line number from the error """
        if isinstance(e, SyntaxError):
            return e.lineno - 1, e.offset
        elif hasattr(e, '__traceback__'):
            tb = e.__traceback__
            extracted_tb = traceback.extract_tb(tb)
            for frame in reversed(extracted_tb):
                if filepath in frame.filename:
                    return frame.lineno - 1, None
            else:
                return extracted_tb[-1].lineno - 1, None
        else:
            return -1, -1
    

    def createNewScript(self, filepath: str) -> bool:
        """ Creates a new script """
        fullpath: str = self.scripts_folder + filepath
        if os.path.exists(fullpath):
            lines: list[str] = []
            with open(fullpath, "w") as f:
                f.writelines(lines)
            return True
        else:
            return False
    

    def loadScript(self, filepath: str) -> bool:
        """ Loads a specified script """
        fullpath: str = self.scripts_folder + filepath
        if os.path.exists(fullpath):
            with open(fullpath, "r") as f:
                self.lines = f.read().split("\n")
            self.lines.pop()
            self.selected_script = fullpath
            return True
        else:
            return False
    

    def writeScript(self, filepath: str) -> bool:
        """ Writes a specified script """
        fullpath: str = self.scripts_folder + filepath
        if os.path.exists(fullpath):
            words: str = ""
            for line in self.lines:
                words += "".join(f"{line}") + "\n"
            
            with open(fullpath, "w") as f:
                f.write(words)
            return True
        else:
            return False
    

    def executeScript(self, filepath: str) -> bool:
        """ Loads and executes a script """
        fullpath: str = self.scripts_folder + filepath
        if os.path.exists(fullpath):
            try:
                spec = importlib.util.spec_from_file_location(f"{filepath.replace('.py', '')}", fullpath)
                module = importlib.util.module_from_spec(spec)                
                namespace = filepath.replace(".py", "")
                
                def log(text: str) -> None:
                    string: str = F.BLACK + "[" + F.BLUE + namespace + F.BLACK + "][" + F.GREEN + "Info" + F.BLACK + "]" + F.CYAN + " > " + F.WHITE + text + F.RESET
                    print(string)
                def warn(text: str) -> None:
                    string: str = F.BLACK + "[" + F.BLUE + namespace + F.BLACK + "][" + F.YELLOW + "Warning" + F.BLACK + "]" + F.CYAN + " > " + F.WHITE + text + F.RESET
                    print(string)
                def error(text: str) -> None:
                    string: str = F.BLACK + "[" + F.BLUE + namespace + F.BLACK + "][" + F.RED + "Error" + F.BLACK + "]" + F.CYAN + " > " + F.WHITE + text + F.RESET
                    print(string)
                
                
                class LoggerManager:
                    def __init__(self, logging_folder: str = "./logs/") -> None:
                        self.logging_folder = logging_folder
                        self.log_time: str = self.get_datetime()
                        self.selected_path: str | None = None

                    def get_datetime(self) -> str:
                        return datetime.datetime.now().strftime("%d_%m_%Y")

                    def init(self) -> None:
                        if self.selected_path is not None:
                            with open(self.selected_path, "w") as f:
                                f.write(f"[{namespace}] > new log \"{self.logging_folder}{self.log_time}.log\", we are ready to log!")
                        else:
                            self.re_init()

                    def re_init(self) -> None:
                        self.log_time = self.get_datetime()
                        suggested_path: str = f"{self.logging_folder}{self.log_time}"
                        self.selected_path = suggested_path
                        if os.path.exists(f"{self.logging_folder}{self.log_time}"):
                            index: int = 1
                            max_depth: int = 1000 # No more than 1,000 logs can be created per day
                            depth: int = 1
                            while (depth <= max_depth):
                                suggested_path: str = f"{self.logging_folder}{self.log_time}_{index}"
                                if not os.path.exists(suggested_path):
                                    self.selected_path = suggested_path
                                    break
                                else:
                                    index += 1
                                depth += 1
                            else:
                                self.init()
                        else:
                            self.init()


                    def log(self, text: str) -> bool:
                        if not os.path.exists(self.selected_path):
                            self.re_init()
                            return False
                        else:
                            dt = datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
                            with open(self.selected_path, "a") as f:
                                f.write(f"[{namespace}][{dt}] {text}")
                            return True
                
                
                setattr(module, "assets", self.assets)
                
                logger = type("logger", (), {})
                setattr(module, "logger", logger)
                setattr(module.logger, "log", log)
                setattr(module.logger, "warn", warn)
                setattr(module.logger, "error", error)
                setattr(module, "LoggerManager", LoggerManager)
                spec.loader.exec_module(module)
                self.selected_module = module
                self.error_code = None
                self.error_column = None
                return True
            except Exception as msg:
                print(f"[Rapter2D][Script][Execute][Error] Unable to load script: {msg}")
                self.error_code, self.error_column = self.getErrorLineNum(self.selected_script, msg)
                return False
        else:
            return False
    

    def run_main(self) -> None:
        if self.selected_module is not None:
            try:
                if hasattr(self.selected_module, "main"):
                    self.selected_module.main(self.game_window)
                elif hasattr(self.selected_module, "run"):
                    self.selected_module.run(self.game_window)
            except Exception as msg:
                print(f"[Rapter2D][Run][Main][Error] Unable to run: {msg}")
                self.error_code, self.error_column = self.getErrorLineNum(self.selected_script, msg)
    

    def run_enable(self) -> None:
        if self.selected_module is not None:
            try:
                if hasattr(self.selected_module, "enable"):
                    self.selected_module.enable()
            except Exception as msg:
                print(f"[Rapter2D][Run][Enable][Error] Unable to run: {msg}")
                self.error_code, self.error_column = self.getErrorLineNum(self.selected_script, msg)
    

    def run_disable(self) -> None:
        if self.selected_module is not None:
            try:
                if hasattr(self.selected_module, "disable"):
                    self.selected_module.disable()
            except Exception as msg:
                print(f"[Rapter2D][Run][Disable][Error] Unable to run: {msg}")
                self.error_code, self.error_column = self.getErrorLineNum(self.selected_script, msg)
    
    
    def loadAssets(self) -> None:
        for asset in os.listdir(self.getAssetsFolder()):
            if os.path.isfile(f"{self.getAssetsFolder()}{asset}"):
                if asset.endswith(".png") or asset.endswith(".jpg") or asset.endswith(".jpeg"):
                    metadata: dict = {}
                    metadata_path: str = f"{self.getAssetsFolder()}{asset.replace('.png', '').replace('.jpg', '').replace('.jpeg', '')}.meta"
                    if os.path.exists(metadata_path):
                        with open(metadata_path, "r") as f:
                            metadata = json.load(f)
                    
                    image = pygame.image.load(f"{self.assets_folder}{asset}")
                
                    self.assets.append({
                        "name": f"{asset.replace('.png', '').replace('.jpg', '').replace('.jpeg', '')}",
                        "image": image,
                        "metadata": metadata
                    })
            else:
                print(f"[Rapter2D][Assets][Load][Skip] Skipped loading: {self.getAssetsFolder()}/{asset} because type: Folder")


    def getAssetsFolder(self) -> str:
        """ Gets the current asset path """
        return self.assets_folder


    def setAssetsFolder(self, assets_folder: str) -> None:
        """ Sets the asset path to your own assets path, Note: you will have to provide assets that come included with Rapter2D """
        self.assets_folder = assets_folder


    def getObjects(self) -> list[Any]:
        """ Sets all of the objects currently in the scene """
        return self.objects


    def setObjects(self, objects: list[Any]) -> None:
        """ Sets the objects list to a predefined list of objects. Useful for demos, templates or tutorials """
        self.objects = objects
    

    def addObject(self, obj: Any) -> bool:
        """ Adds an object to the scene """
        try:
            self.objects.append(obj)
            return True
        except Exception as msg:
            print(f"[Rapter2D][Object][Add][Error] Unable to add Object: {msg}")
            return False
    

    def removeObject(self, obj: Any | None = None, index: int | None = None) -> bool:
        """ Remove an object from the scene """
        try:
            if obj is not None:
                index = self.objects.index(obj)
                self.objects.pop(index)
                return True
            elif index is not None:
                self.objects.pop(index)
                return True
            else:
                return False
        except Exception as msg:
            print(f"[Rapter2D][Object][Remove][Error] Unable to remove Object: {msg}")
            return False
        

    def addObjects(self, objects: list[Any] = ...) -> None:
        """ Add multiple objects at once to the scene """
        for obj in objects:
            try:
                self.objects.append(obj)
            except Exception as msg:
                print(f"[Rapter2D][Objects][Add][Error] Unable to add Objects: {msg}")
    

    def removeObjects(self, objects: list[Any] | None = None, indexes: list[int] | None = None) -> None:
        """ Remove multiple objects at once from the scene """
        if objects is not None:
            for obj in objects:
                try:
                    index = self.objects.index(obj)
                    self.objects.pop(index)
                except Exception as msg:
                    print(f"[Rapter2D][Objects][Remove][Error] Unable to remove Objects: {msg}")

        elif indexes is not None:
            for index in indexes:
                try:
                    self.objects.pop(index)
                except Exception as msg:
                    print(f"[Rapter2D][Objects][Remove][Error] Unable to remove Objects: {msg}")
    
    
    def render_script_window(self) -> None:
        line_x: int = 40
        line_y: int = 20 - self.scroll_offset

        for y, line in enumerate(self.lines):
            if self.error_code is not None:
                if int(self.error_code) != int(y):
                    line_num = self.font.render(f"{y+1}", True, (255, 255, 255), (80, 80, 80))
                else:
                    line_num = self.font.render(f"{y+1}", True, (255, 255, 255), (200, 0, 0))
            else:
                line_num = self.font.render(f"{y+1}", True, (255, 255, 255), (80, 80, 80))
            
            # Handles rendering TABS
            tabs_render = self.font.render("", True, (0, 0, 144))


            display_line = line.replace("\t", " " * TAB_SIZE)
            
            if self.error_code is not None and int(self.error_code) == int(y):
                # Red background
                bg_surface = pygame.Surface((self.script_window.get_width(), self.line_height))
                bg_surface.fill((255, 0, 0))
                self.script_window.blit(bg_surface, (0, line_y))

                # Highlight error column if available
                if self.error_column is not None and self.error_column <= len(display_line):
                    error_start = display_line[:self.error_column - 1]
                    error_char = display_line[self.error_column - 1]
                    after_error = display_line[self.error_column:]

                    x_base = line_x + self.font.size(error_start)[0]
                    x_error = self.font.size(error_char)[0]

                    # draw everything before error char
                    self.script_window.blit(self.font.render(error_start, True, (255, 255, 255)), (line_x + line_num.get_width() + tabs_render.get_width() + 4, line_y))

                    # draw the error char in yellow
                    self.script_window.blit(self.font.render(error_char, True, (255, 255, 0)), (line_x + line_num.get_width() + tabs_render.get_width() + 4 + self.font.size(error_start)[0], line_y))

                    # draw the rest
                    self.script_window.blit(self.font.render(after_error, True, (255, 255, 255)), (line_x + line_num.get_width() + tabs_render.get_width() + 4 + self.font.size(error_start + error_char)[0], line_y))
                else:
                    # fallback: highlight whole line
                    text_render = self.font.render(display_line, True, (255, 255, 255))
                    self.script_window.blit(text_render, (line_x + line_num.get_width() + tabs_render.get_width() + 4, line_y))
            else:
                text_render = self.font.render(display_line, True, (255, 255, 255))
                self.script_window.blit(text_render, (line_x + line_num.get_width() + tabs_render.get_width() + 4, line_y))


            self.script_window.blit(line_num, (line_x, line_y))
            self.script_window.blit(tabs_render, (line_x + line_num.get_width(), line_y))
            self.script_window.blit(text_render, (line_x + line_num.get_width() + tabs_render.get_width() + 4, line_y))

            if y == self.selected_line:
                display_line = line.replace("\t", " " * TAB_SIZE)
                cursor_x = self.font.size(display_line[:self.cursor_pos + line[:self.cursor_pos].count("\t") * (TAB_SIZE - 1)])[0]
                pygame.draw.rect(
                    self.script_window,
                    (200, 200, 200),
                    (line_x + line_num.get_width() + tabs_render.get_width() + 4 + cursor_x, line_y, 2, self.font.get_height())
                )
            line_y += 28

        # Handle new line cursor
        if self.selected_line == len(self.lines):
            line_num = self.font.render(f"{self.selected_line}", True, (255, 255, 255), (80, 80, 80))
            self.script_window.blit(line_num, (line_x, line_y))
            pygame.draw.rect(
                self.script_window,
                (200, 200, 200),
                (line_x + line_num.get_width() + 4, line_y, 2, self.font.get_height())
            )

    
    def render_game_window(self) -> None:
        for obj in self.objects:
            if type(obj) == Object:
                obj.render(self.game_window, self.assets)
            else:
                obj.render(self.game_window)
    
    
    def render_asset_window(self) -> None:
        offset: int = 32
        asset_size: int = 64
        asset_space: int = 5

        max_width = self.asset_window.get_width() - offset
        max_height = self.asset_window.get_height() - offset

        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()

        index_x = offset
        index_y = offset

        for asset in self.assets:
            if index_x + asset_size > max_width:
                index_x = offset
                index_y += asset_size + asset_space

            if index_y + asset_size > max_height:
                break

            asset_box = pygame.Rect(index_x, index_y, asset_size, asset_size)
            image = pygame.transform.scale(asset.get("image"), (asset_size, asset_size))
            hovered = asset_box.collidepoint(mouse_x, mouse_y)

            pygame.draw.rect(self.asset_window, (128, 128, 128) if hovered else (255, 255, 255), asset_box)
            self.asset_window.blit(image, (index_x, index_y))
            pygame.draw.rect(self.asset_window, (8, 8, 8), asset_box, 2)

            if hovered:
                name = asset.get("name", "unknown")
                label = self.font.render(name, True, (0, 0, 0))
                label_bg = label.get_rect()
                label_bg.topleft = (index_x, index_y - 20 if index_y > 20 else index_y + asset_size + 5)
                pygame.draw.rect(self.asset_window, (255, 255, 255), label_bg)
                self.asset_window.blit(label, label_bg)

            index_x += asset_size + asset_space

    
    
    def clamp_scroll(self):
        max_scroll = max(0, len(self.lines) * self.line_height - self.script_window.get_height() + 40)
        self.scroll_offset = min(self.scroll_offset, max_scroll)
    
    
    def run(self) -> None:
        auto_save_cooldown = CooldownTimer(1)
        self.run_enable()
        self.cursor_pos: int = 0
        while self.running:
            try:
                self.run_main()
                for event in pygame.event.get():
                    if self.save_button.handleEvent(event):
                        print("Saving Script")
                        self.writeScript("main.py")
                    if self.run_button.handleEvent(event):
                        print("Executing Script")
                        self.executeScript("main.py")
                    if self.load_button.handleEvent(event):
                        print("Loading Script")
                        self.loadScript("main.py")
                    if self.auto_save_button.handleEvent(event):
                        if self.enabled_auto_save:
                            self.enabled_auto_save = False
                        else:
                            self.enabled_auto_save = True
                    if self.reload_button.handleEvent(event):
                        self.run_disable()
                        self.run_enable()

                    if event.type == pygame.QUIT:
                        self.running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.running = False

                        elif event.key == pygame.K_BACKSPACE:
                            if self.selected_line < len(self.lines):
                                if self.cursor_pos > 0:
                                    self.lines[self.selected_line] = (
                                        self.lines[self.selected_line][:self.cursor_pos - 1] +
                                        self.lines[self.selected_line][self.cursor_pos:]
                                    )
                                    self.cursor_pos -= 1
                                elif self.selected_line > 0:
                                    prev_len = len(self.lines[self.selected_line - 1])
                                    self.lines[self.selected_line - 1] += self.lines[self.selected_line]
                                    self.lines.pop(self.selected_line)
                                    self.selected_line -= 1
                                    self.cursor_pos = prev_len

                        elif event.key == pygame.K_RETURN:
                            if self.selected_line < len(self.lines):
                                current_line = self.lines[self.selected_line]
                                new_line = current_line[self.cursor_pos:]
                                self.lines[self.selected_line] = current_line[:self.cursor_pos]
                                self.lines.insert(self.selected_line + 1, new_line)
                            else:
                                self.lines.append("")
                            self.selected_line += 1
                            self.cursor_pos = 0

                        elif event.key == pygame.K_LEFT:
                            if self.cursor_pos > 0:
                                self.cursor_pos -= 1
                            elif self.selected_line > 0:
                                self.selected_line -= 1
                                self.cursor_pos = len(self.lines[self.selected_line])

                        elif event.key == pygame.K_RIGHT:
                            if self.selected_line < len(self.lines):
                                if self.cursor_pos < len(self.lines[self.selected_line]):
                                    self.cursor_pos += 1
                                elif self.selected_line + 1 < len(self.lines):
                                    self.selected_line += 1
                                    self.cursor_pos = 0

                        elif event.key == pygame.K_UP:
                            if self.selected_line > 0:
                                self.selected_line -= 1
                                self.cursor_pos = min(self.cursor_pos, len(self.lines[self.selected_line]))
                            if self.selected_line * self.line_height < self.scroll_offset:
                                self.scroll_offset = max(0, self.scroll_offset - self.line_height)
                                self.clamp_scroll()

                        elif event.key == pygame.K_DOWN:
                            if self.selected_line < len(self.lines):
                                self.selected_line += 1
                                if self.selected_line == len(self.lines):
                                    self.lines.append("")
                                self.cursor_pos = min(self.cursor_pos, len(self.lines[self.selected_line]))
                            visible_lines = self.script_window.get_height() // self.line_height
                            if (self.selected_line + 1) * self.line_height > self.scroll_offset + self.script_window.get_height() - 40:
                                self.scroll_offset += self.line_height
                                self.clamp_scroll()

                        elif event.key == pygame.K_TAB:
                            if self.selected_line >= len(self.lines):
                                self.lines.append("")
                            self.lines[self.selected_line] = (
                                self.lines[self.selected_line][:self.cursor_pos] +
                                "\t" +
                                self.lines[self.selected_line][self.cursor_pos:]
                            )
                            self.cursor_pos += 1

                        elif event.unicode:
                            if self.selected_line >= len(self.lines):
                                self.lines.append("")
                            line = self.lines[self.selected_line]
                            self.lines[self.selected_line] = line[:self.cursor_pos] + event.unicode + line[self.cursor_pos:]
                            self.cursor_pos += 1
                
                if self.enabled_auto_save:
                    if auto_save_cooldown.trigger():
                        self.writeScript("main.py")
                        self.executeScript("main.py")
                
                if self.enabled_auto_save:
                    self.auto_save_button.setUpImage(self.auto_save_1_assets[0])
                    self.auto_save_button.setDownImage(self.auto_save_1_assets[1])
                else:
                    self.auto_save_button.setUpImage(self.auto_save_2_assets[0])
                    self.auto_save_button.setDownImage(self.auto_save_2_assets[1])

                self.render_script_window()
                self.render_game_window()
                self.render_asset_window()

                self.window.blit(self.game_window, (0, 0))
                self.window.blit(self.script_window, (self.separator_1, 0))
                self.window.blit(self.asset_window, (0, self.separator_2))


                # Game Border
                pygame.draw.rect(self.window, (25, 25, 25), (0, 0, PRESET_RESOLUTION[0], 8))
                pygame.draw.rect(self.window, (25, 25, 25), (0, 0, 8, PRESET_RESOLUTION[1]))
                pygame.draw.rect(self.window, (25, 25, 25), (0, PRESET_RESOLUTION[1] - 8, PRESET_RESOLUTION[0], 32))
                pygame.draw.rect(self.window, (25, 25, 25), (PRESET_RESOLUTION[0] - 8, 0, 8, PRESET_RESOLUTION[1]))
                
                # Separators
                # Recalculate separator rectangles using updated positions
                Separator_1_Rect = pygame.Rect(self.separator_1, 0, 8, PRESET_RESOLUTION[1])
                Separator_2_Rect = pygame.Rect(0, self.separator_2, self.separator_1, 8)
                Separator_3_Rect = pygame.Rect(self.separator_1, PRESET_RESOLUTION[1] - 53, PRESET_RESOLUTION[0] - self.separator_1, 45)

                mouse_x, mouse_y = pygame.mouse.get_pos()
                if Separator_1_Rect.collidepoint(mouse_x, mouse_y):
                    pygame.draw.rect(self.window, (128, 128, 128), Separator_1_Rect)
                else:
                    pygame.draw.rect(self.window, (25, 25, 25), Separator_1_Rect)
                if Separator_2_Rect.collidepoint(mouse_x, mouse_y):
                    pygame.draw.rect(self.window, (128, 128, 128), Separator_2_Rect)
                else:
                    pygame.draw.rect(self.window, (25, 25, 25), Separator_2_Rect)
                if Separator_3_Rect.collidepoint(mouse_x, mouse_y):
                    pygame.draw.rect(self.window, (55, 55, 55), Separator_3_Rect)
                else:
                    pygame.draw.rect(self.window, (25, 25, 25), Separator_3_Rect)
                
                # Separator dragging logic
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if Separator_1_Rect.collidepoint(event.pos):
                        self.dragging_separator_1 = True
                    if Separator_2_Rect.collidepoint(event.pos):
                        self.dragging_separator_2 = True

                if event.type == pygame.MOUSEBUTTONUP:
                    self.dragging_separator_1 = False
                    self.dragging_separator_2 = False
                
                self.auto_save_button.loc = (self.separator_1 + 40, PRESET_RESOLUTION[1] - 45)
                self.reload_button.loc    = (self.separator_1 + 80, PRESET_RESOLUTION[1] - 45)

                self.auto_save_button.rect.topleft = self.auto_save_button.loc
                self.reload_button.rect.topleft = self.reload_button.loc


                if self.dragging_separator_1:
                    self.separator_1 = max(100, min(mouse_x, PRESET_RESOLUTION[0] - 350))

                if self.dragging_separator_2:
                    self.separator_2 = max(100, min(mouse_y, PRESET_RESOLUTION[1] - 100))


                # Update surface sizes dynamically after dragging
                self.game_window = pygame.Surface((self.separator_1, self.separator_2))
                self.script_window = pygame.Surface((PRESET_RESOLUTION[0] - self.separator_1, PRESET_RESOLUTION[1]))
                self.asset_window = pygame.Surface((self.separator_1, PRESET_RESOLUTION[1] - self.separator_2))


                self.save_button.draw()
                self.run_button.draw()
                self.load_button.draw()
                self.auto_save_button.draw()
                self.reload_button.draw()
                
                pygame.draw.circle(self.window, (255, 255, 255), (mouse_x, mouse_y), 8)
                pygame.draw.circle(self.window, (  0,   0,   0), (mouse_x, mouse_y), 8, 2)

                pygame.display.update()
                self.window.fill((0, 0, 0))
                self.script_window.fill((0, 0, 0))
                self.game_window.fill((0, 0, 0))
                self.asset_window.fill((15, 15, 15))


            except pygame.error as msg:
                print(f"[Rapter2D][Error] {msg}")
        self.run_disable()



if __name__ == "__main__":
    rapter2d = Rapter2D()
    rapter2d.loadAssets()
    
    if not rapter2d.loadScript("main.py"):
        rapter2d.createNewScript("main.py")
    else:
        rapter2d.loadScript("main.py")
        rapter2d.executeScript("main.py")
        
    rapter2d.run()
