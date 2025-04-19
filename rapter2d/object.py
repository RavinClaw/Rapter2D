import pygame


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
                        self.screen.blit(asset.get("image"))
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
