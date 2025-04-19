import pygame


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
