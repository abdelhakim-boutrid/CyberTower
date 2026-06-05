import pyxel

top_left  = (0,32)
top_right = (pyxel.width, 32)
tm = 0 #Tilemap( 0 - 7 )

class App:

    def __init__(self):
        pyxel.init(256, 256, title="Nuit du Code")
        self.x = 0
        pyxel.load("theme.pyxres")
        pyxel.run(self.update, self.draw)

    def update(self):
        self.x = (self.x + 1) % pyxel.width

    def draw(self):
        pyxel.cls(0)
        pyxel.line(0,31,256,31,13)
        pyxel.bltm(0,32,tm,0,0,pyxel.width,pyxel.height-32)

class TowerType(enumerate):
    firewall = 1
    ruler = 2
    packet_filter = 3
    phising = 11
    DOS =12
    voicephising = 13

class Defense:
    def __init__(self):
        hp=16
        towers=list()

class tower:
    def __init__(self):
        damage=0
        name=""
        sprite=""

        
class Attack:
    def __init__(self):
        money=10
        monsters=list()

class monster:
    def __init__(self):
        damage=0
        name=""
        sprite=""
        
        

App()