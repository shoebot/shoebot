try:
    beziereditor = ximport("beziereditor")
except:
    beziereditor = ximport("__init__")
    reload(beziereditor)

speed(100)
size(400, 400)

def setup():
    
    global editor
    editor = beziereditor.start(filename="path")

def draw():
    
    global editor
    editor.draw()