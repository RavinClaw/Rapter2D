# Rapter2D
Rapter2D is a small time game editor / engine that is written on top of Pygame and written to be as usable as possible.
### Rapter2D Version: v***0.1_d1***

*[NOTE] Rapter2D is still in early development and anything can change at any moment*

## How to use Rapter2D
Since Rapter2D is still in early development it's hard to create a guide for the program since things are still changing, however here are a couple of basics that can help you develop in Rapter2D.

Rapter2D uses the standard python file (And Lua in the future for UI elements / Shaders if they are supported), you are able to use these outside of the internal code editor and if you want more features you should since it's still pretty limited in usability.


## Code Editor
The code editor is quite simple, it uses Python as it's programming language of choice

*This code renders "Hello World" on the game screen*
```py
from rapter2d import Text

text = Text("Hello World", 100, 100)

def main(window):
  text.render(window)
```

When using Rapter2D you will notice that there are 3 different functions that are integral for creating a game here (`def main(window)` / `def run(window)`, `def enable()` and `def disable()`)

`main` is the function that runs your code for every loop of the engine, this is required if you want to render things to the screen.
That makes it really easy to figure out what `window` is window is `pygame.Surface` the main screen for your game, using this is really simple if you know how `pygame.Surface` works.
```py
def main(window):
  ...
```

`enable` is the function that runs when your script is enabled, you would want to use this if you require a variable to be set durring runtime.
```py
def enable():
  ...
```

`disable` is the function taht runs when your script is disabled, you would want to use this if you want to unallocate variables or set them to `None` once the script stops running, tho none of that is requried.
```py
def disable():
  ...
```
